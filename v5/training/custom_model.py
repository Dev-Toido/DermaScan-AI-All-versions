import tensorflow as tf

class GradientAccumulationModel(tf.keras.Model):
    """
    A custom wrapper for any Keras Model that implements Gradient Accumulation.
    This allows training with effectively large batch sizes on hardware with low VRAM.
    """
    def __init__(self, inputs, outputs, accumulation_steps=4, **kwargs):
        super().__init__(inputs, outputs, **kwargs)
        self.accumulation_steps = accumulation_steps
        self.grad_accumulator = None
        self.steps_counter = tf.Variable(0, dtype=tf.int64, trainable=False)

    def train_step(self, data):
        x, y = data

        # Initialize the accumulator on the first step
        if self.grad_accumulator is None:
            self.grad_accumulator = [
                tf.Variable(tf.zeros_like(var), trainable=False) 
                for var in self.trainable_variables
            ]

        with tf.GradientTape() as tape:
            y_pred = self(x, training=True)
            loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)
            # Scale the loss by the accumulation steps
            scaled_loss = loss / tf.cast(self.accumulation_steps, tf.float32)

        # Calculate gradients
        gradients = tape.gradient(scaled_loss, self.trainable_variables)

        # Accumulate the gradients
        for i in range(len(self.grad_accumulator)):
            self.grad_accumulator[i].assign_add(gradients[i])

        self.steps_counter.assign_add(1)

        # Apply gradients only if accumulation_steps have been reached
        def apply_gradients():
            self.optimizer.apply_gradients(zip(self.grad_accumulator, self.trainable_variables))
            # Reset accumulator
            for var in self.grad_accumulator:
                var.assign(tf.zeros_like(var))
            return tf.constant(True)

        def skip_apply():
            return tf.constant(False)

        tf.cond(tf.equal(self.steps_counter % self.accumulation_steps, 0), apply_gradients, skip_apply)

        # Update metrics
        self.compiled_metrics.update_state(y, y_pred)
        return {m.name: m.result() for m in self.metrics}
