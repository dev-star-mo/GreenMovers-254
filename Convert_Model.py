import tensorflow as tf
import numpy as np

# --- Configuration ---
MODEL_H5_PATH = "audio_classifier.h5"
MODEL_TFLITE_PATH = "audio_classifier_quantized.tflite"

# --- 1. Load the Trained Keras Model ---
print(f"Loading model from {MODEL_H5_PATH}...")
model = tf.keras.models.load_model(MODEL_H5_PATH)
print("Model loaded successfully.")
model.summary()

# --- 2. Generate Representative Dataset for Quantization ---
# This is a crucial step. The converter needs a sample of real data
# to understand the range of values (min/max) for each activation
# in the model. This ensures the 8-bit integer conversion is accurate.

def representative_dataset():
    # Load the same synthetic data generator you used for training
    # We need this to create samples for the converter
    # NOTE: For a real project, you would use a small subset of your
    # actual training/validation data, not synthetic data.
    from msitushield_model import create_synthetic_audio, extract_spectrogram_features, N_MFCC, SAMPLE_RATE, DURATION
    
    # Generate a small batch of data
    X_audio, _ = create_synthetic_audio()
    # We only need a few samples, e.g., 10-20
    X_audio = X_audio[:20] 
    
    # Extract features in the same way as training
    X_features = extract_spectrogram_features(X_audio, SAMPLE_RATE, N_MFCC)
    
    # The model expects a 4D tensor: (batch_size, height, width, channels)
    # We yield one sample at a time as a list
    for sample in X_features:
        # Add the channel dimension and wrap in a list
        yield [np.expand_dims(sample, axis=0).astype(np.float32)]

print("\nPreparing representative dataset for quantization...")
# This is just a sanity check to make sure the function works
for sample in representative_dataset():
    print(f"Sample shape for converter: {sample[0].shape}")
    break

# --- 3. Convert the Model to TensorFlow Lite with Quantization ---
print("\nStarting model conversion to TFLite with full integer quantization...")

converter = tf.lite.TFLiteConverter.from_keras_model(model)

# This is the key line for microcontroller deployment
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# This tells the converter to use our representative dataset
converter.representative_dataset = representative_dataset

# This ensures the model's input and output tensors are also integers
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

# Perform the conversion
tflite_quant_model = converter.convert()

# --- 4. Save the Quantized Model ---
with open(MODEL_TFLITE_PATH, 'wb') as f:
    f.write(tflite_quant_model)

print(f"\n✅ Model successfully converted and saved to {MODEL_TFLITE_PATH}")
print(f"Original .h5 model size: ~{len(open(MODEL_H5_PATH, 'rb').read()) / 1024:.2f} KB")
print(f"Quantized .tflite model size: ~{len(open(MODEL_TFLITE_PATH, 'rb').read()) / 1024:.2f} KB")
