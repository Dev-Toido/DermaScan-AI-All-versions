import tensorflow as tf

class FocalLoss(tf.keras.losses.Loss):
    """
    Focal Loss implementation for handling class imbalance, particularly for 
    boosting the sensitivity of the rare, highly critical classes like Melanoma.
    
    Formula: FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, gamma=2.0, alpha=0.25, name='focal_loss', **kwargs):
        super().__init__(name=name, **kwargs)
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        # Clip predictions to prevent NaN in log
        y_pred = tf.clip_by_value(y_pred, tf.keras.backend.epsilon(), 1 - tf.keras.backend.epsilon())
        
        # Calculate cross entropy
        cross_entropy = -y_true * tf.math.log(y_pred)
        
        # Calculate focal loss weight
        weight = self.alpha * tf.math.pow(1 - y_pred, self.gamma)
        
        # Apply weight to cross entropy
        focal_loss = weight * cross_entropy
        
        return tf.reduce_mean(tf.reduce_sum(focal_loss, axis=-1))

    def get_config(self):
        config = super().get_config()
        config.update({
            "gamma": self.gamma,
            "alpha": self.alpha
        })
        return config

if __name__ == "__main__":
    # Test the loss
    import numpy as np
    y_true = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
    y_pred = np.array([[0.9, 0.05, 0.05], [0.1, 0.8, 0.1]], dtype=np.float32)
    fl = FocalLoss()
    print("Test Focal Loss Output:", fl(y_true, y_pred).numpy())
