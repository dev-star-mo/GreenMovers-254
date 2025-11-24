import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, BatchNormalization, Input
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import scipy.signal # Use scipy.signal directly

# --- 1. Configuration & Hyperparameters ---

SAMPLE_RATE = 16000  # Hz, typical for audio processing
DURATION = 2.0       # seconds per audio clip
N_SAMPLES = int(SAMPLE_RATE * DURATION)
N_MFCC = 13          # Number of MFCC features to extract

# Data generation parameters
N_SAMPLES_PER_CLASS = 500 # Number of synthetic samples to generate for each class

# Model parameters
# We will define the input shape dynamically after feature extraction
NUM_CLASSES = 3 # chainsaw, truck_engine, forest_noise
EPOCHS = 50
BATCH_SIZE = 32

# --- 2. Synthetic Data Generation ---

def generate_sine_wave(frequency, duration, sample_rate, amplitude=0.5):
    """Generates a pure sine wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def generate_white_noise(duration, sample_rate, amplitude=0.1):
    """Generates white noise."""
    return amplitude * np.random.randn(int(sample_rate * duration))

def create_synthetic_audio():
    """
    Creates synthetic audio data for our three classes.
    This is a placeholder for real-world data collection.
    """
    print("Generating synthetic audio data...")
    data = []
    labels = []

    # Class 0: Chainsaw (high-frequency buzz + some mid-range noise)
    for _ in range(N_SAMPLES_PER_CLASS):
        signal = generate_sine_wave(np.random.uniform(100, 120), DURATION, SAMPLE_RATE, 0.4)
        signal += generate_sine_wave(np.random.uniform(400, 500), DURATION, SAMPLE_RATE, 0.2)
        signal += generate_white_noise(DURATION, SAMPLE_RATE, 0.05)
        data.append(signal)
        labels.append(0)

    # Class 1: Truck Engine (low-frequency rumble)
    for _ in range(N_SAMPLES_PER_CLASS):
        signal = generate_sine_wave(np.random.uniform(50, 80), DURATION, SAMPLE_RATE, 0.5)
        signal += generate_sine_wave(np.random.uniform(100, 150), DURATION, SAMPLE_RATE, 0.2)
        signal += generate_white_noise(DURATION, SAMPLE_RATE, 0.05)
        data.append(signal)
        labels.append(1)

    # Class 2: Forest Noise (mostly white noise with occasional low-frequency elements)
    for _ in range(N_SAMPLES_PER_CLASS):
        signal = generate_white_noise(DURATION, SAMPLE_RATE, 0.3)
        if np.random.rand() > 0.5:
            # FIX: Generate the short sound
            thump_duration = 0.2 # seconds
            thump = generate_sine_wave(np.random.uniform(20, 40), thump_duration, SAMPLE_RATE, 0.5)
            
            # FIX: Place it at a random position in the main signal
            start_index = np.random.randint(0, N_SAMPLES - len(thump))
            signal[start_index : start_index + len(thump)] += thump
            
        data.append(signal)
        labels.append(2)

    print(f"Generated {len(data)} audio samples.")
    return np.array(data), np.array(labels)

# --- 3. Feature Extraction (Spectrogram) ---

def extract_spectrogram_features(audio_data, sample_rate, n_mfcc, n_fft=512, hop_length=256):
    """
    Extracts spectrogram features from audio data.
    This is a more robust approach for our CNN.
    """
    print("Extracting spectrogram features...")
    features = []
    # We'll use a fixed number of time steps for the model input
    fixed_time_steps = 32 
    
    for audio in audio_data:
        # Compute the spectrogram
        f, t, Sxx = scipy.signal.spectrogram(audio, fs=sample_rate, nperseg=n_fft, noverlap=n_fft - hop_length)
        
        # Take the first n_mfcc frequency bins (simulating MFCCs)
        feature = Sxx[:n_mfcc, :]
        
        # FIX: Ensure the time dimension is consistent
        # Pad with zeros if the spectrogram is too short, or truncate if too long
        if feature.shape[1] < fixed_time_steps:
            pad_width = fixed_time_steps - feature.shape[1]
            feature = np.pad(feature, pad_width=((0, 0), (0, pad_width)), mode='constant')
        elif feature.shape[1] > fixed_time_steps:
            feature = feature[:, :fixed_time_steps]
            
        features.append(feature)
        
    return np.array(features)


# --- 4. Model Definition ---

def build_model(input_shape, num_classes):
    """Builds a CNN model for audio classification."""
    model = Sequential([
        Input(shape=input_shape),
        
        Conv2D(32, kernel_size=(3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.3),

        Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.3),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

# --- 5. Main Execution Block ---

if __name__ == "__main__":
    # Generate data
    X_audio, y = create_synthetic_audio()
    
    # Extract features
    X = extract_spectrogram_features(X_audio, SAMPLE_RATE, N_MFCC)
    
    # Reshape data for CNN: add a channel dimension
    # The input shape is now determined dynamically
    INPUT_SHAPE = (X.shape[1], X.shape[2], 1)
    X = X.reshape(X.shape[0], *INPUT_SHAPE)
    
    # One-hot encode labels
    y_categorical = to_categorical(y, num_classes=NUM_CLASSES)
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")
    print(f"Model Input Shape: {INPUT_SHAPE}")
    
    # Build and summarize the model
    model = build_model(INPUT_SHAPE, NUM_CLASSES)
    model.summary()
    
    # Train the model
    print("\nStarting model training...")
    history = model.fit(X_train, y_train,
                        epochs=EPOCHS,
                        batch_size=BATCH_SIZE,
                        validation_data=(X_test, y_test),
                        verbose=1)
    
    # Evaluate the model
    print("\nEvaluating model on test data...")
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {accuracy*100:.2f}%")
    
    # Save the trained model
    model.save("audio_classifier.h5")
    print("\nModel saved successfully as audio_classifier.h5")
