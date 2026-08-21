import tensorflow as tf
import sys

print("\n===============================")
print("  TENSORFLOW HARDWARE TEST")
print("===============================\n")

print(f"Python Version: {sys.version}")
print(f"TensorFlow Version: {tf.__version__}")

gpus = tf.config.list_physical_devices('GPU')
print(f"Num GPUs Available: {len(gpus)}")

if gpus:
    for i, gpu in enumerate(gpus):
        print(f"GPU {i}: {gpu.name}")
        details = tf.config.experimental.get_device_details(gpu)
        print(f"Details: {details}")
    print("\n✅ GPU is perfectly connected to TensorFlow in WSL!")
else:
    print("\n❌ TensorFlow cannot see the GPU. Check WSL CUDA drivers.")
