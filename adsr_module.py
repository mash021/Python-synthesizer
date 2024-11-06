# adsr_module.py - ADSR Envelope Generator Similar to Serum
import numpy as np

class ADSR:
    def __init__(self, sample_rate, attack=0.1, decay=0.1, sustain=0.7, release=0.1):
        self.sample_rate = sample_rate
        self.attack_time = attack
        self.decay_time = decay
        self.sustain_level = sustain
        self.release_time = release

    def set_params(self, attack=None, decay=None, sustain=None, release=None):
        if attack is not None:
            self.attack_time = attack
        if decay is not None:
            self.decay_time = decay
        if sustain is not None:
            self.sustain_level = sustain
        if release is not None:
            self.release_time = release

    def generate_envelope(self, duration, note_on_length):
        """
        Generate ADSR envelope for a given duration.
        
        :param duration: Total duration of the sound (in seconds)
        :param note_on_length: Length of time the note is held before releasing (in seconds)
        :return: Numpy array containing the ADSR envelope
        """
        length = int(self.sample_rate * duration)
        env = np.zeros(length)
        
        # Calculate sample counts for each ADSR phase
        attack_samples = int(self.attack_time * self.sample_rate)
        decay_samples = int(self.decay_time * self.sample_rate)
        sustain_samples = int(note_on_length * self.sample_rate) - attack_samples - decay_samples
        release_samples = length - (attack_samples + decay_samples + sustain_samples)
        
        # Generate attack phase
        if attack_samples > 0:
            env[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Generate decay phase
        if decay_samples > 0:
            env[attack_samples:attack_samples + decay_samples] = np.linspace(1, self.sustain_level, decay_samples)
        
        # Generate sustain phase
        if sustain_samples > 0:
            env[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = self.sustain_level
        
        # Generate release phase
        if release_samples > 0:
            env[-release_samples:] = np.linspace(self.sustain_level, 0, release_samples)
        
        return env

# Example Usage
# adsr = ADSR(sample_rate=48000, attack=0.05, decay=0.1, sustain=0.8, release=0.2)
# envelope = adsr.generate_envelope(duration=2.0, note_on_length=1.0)
# This module can be imported and used in the main synthesizer code
