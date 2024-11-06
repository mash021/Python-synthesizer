# ds_filter.py (Dave Smith Filter Implementation)
import numpy as np

class DaveSmithFilter:
    def __init__(self, sample_rate, cutoff, resonance):
        self.sample_rate = sample_rate
        self.cutoff = cutoff
        self.resonance = resonance
        self._initialize_state()

    def _initialize_state(self):
        # Initialize filter state
        self.buffer = [0.0, 0.0]
        self.cutoff_tuned = 0.0
        self.resonance_tuned = 0.0

    def process(self, input_signal):
        # Tuning cutoff frequency
        self.cutoff_tuned = 2 * np.sin(np.pi * self.cutoff / self.sample_rate)
        self.resonance_tuned = min(max(self.resonance, 0.0), 4.0)

        output = np.zeros_like(input_signal)
        for i in range(len(input_signal)):
            x = input_signal[i] - self.resonance_tuned * self.buffer[1]
            self.buffer[0] += self.cutoff_tuned * (np.tanh(x) - np.tanh(self.buffer[0]))
            self.buffer[1] += self.cutoff_tuned * (np.tanh(self.buffer[0]) - np.tanh(self.buffer[1]))
            output[i] = self.buffer[1]

        return output

# Example usage:
# filter = DaveSmithFilter(sample_rate=96000, cutoff=200, resonance=0.7)
# filtered_signal = filter.process(input_signal)