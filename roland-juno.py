import numpy as np
import soundfile as sf
import scipy.signal
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
import os

# Chorus effect parameters
SAMPLE_RATE = 44100  # Standard sample rate
DEPTH = 0.003  # Depth of modulation in seconds (adjust for effect strength)
RATE = 0.8  # Rate of the LFO in Hz
DRY_WET = 0.5  # Mix between dry and wet signal

def juno_chorus(input_signal, rate=RATE, depth=DEPTH, dry_wet=DRY_WET):
    # Creating an LFO for modulation (sinusoidal)
    num_samples = len(input_signal)
    lfo = np.sin(2 * np.pi * rate * np.arange(num_samples) / SAMPLE_RATE)
    
    # Compute delay in samples
    delay_samples = (1 + lfo * depth) * SAMPLE_RATE
    
    # Initialize output signal
    output_signal = np.zeros(num_samples)
    
    for i in range(num_samples):
        # Calculate delay offset for chorus effect
        delay = int(delay_samples[i])  # Convert to integer delay offset
        if i - delay >= 0:
            output_signal[i] = dry_wet * input_signal[i - delay] + (1 - dry_wet) * input_signal[i]
        else:
            output_signal[i] = input_signal[i]
    
    return output_signal

# Load a test audio file or generate a test signal
def generate_sine_wave(freq, duration, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

# Example usage with a sine wave
duration = 3  # Duration of test tone in seconds
frequency = 440  # Test tone frequency
test_tone = generate_sine_wave(frequency, duration)

# Apply the chorus effect
chorused_signal = juno_chorus(test_tone)

# Save the output to a file
output_file = "juno_chorus_effect.wav"
write(output_file, SAMPLE_RATE, chorused_signal.astype(np.float32))

print(f"Chorus effect applied and saved as {output_file}")

# Optionally, plot the original and chorused signals for visualization
plt.figure(figsize=(12, 6))
plt.plot(test_tone[:1000], label="Original Signal")
plt.plot(chorused_signal[:1000], label="Chorus Signal", alpha=0.75)
plt.legend()
plt.title("Chorus Effect - Waveform Comparison (Zoomed In)")
plt.xlabel("Sample")
plt.ylabel("Amplitude")
plt.show()
