import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input

img = cv2.imread('dog_original.jpg')
img_resized = cv2.resize(img, (224, 224))
img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
img_array = np.expand_dims(img_rgb, axis=0)
img_array = preprocess_input(img_array)

model = ResNet50(weights='imagenet')

last_conv_layer_name = 'conv5_block3_out'
grad_model = tf.keras.models.Model(
    model.inputs, [model.get_layer(last_conv_layer_name).output, model.output]
)

with tf.GradientTape() as tape:
    conv_outputs, predictions = grad_model(img_array)
    class_idx = tf.argmax(predictions[0])
    loss = predictions[:, class_idx]

grads = tape.gradient(loss, conv_outputs)
pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

conv_outputs = conv_outputs[0]
heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
heatmap = tf.squeeze(heatmap)

heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
heatmap = heatmap.numpy()

heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)

superimposed_img = heatmap_colored * 0.4 + img * 0.6
cv2.imwrite('dog_heatmap.jpg', superimposed_img)
