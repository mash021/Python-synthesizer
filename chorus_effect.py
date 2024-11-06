import numpy as np

SAMPLE_RATE = 44100  # Standard sample rate for audio

def juno_chorus(input_signal, rate=0.8, depth=0.003, dry_wet=0.5):
    """Apply enhanced Roland Juno-style stereo chorus effect with better clarity and depth."""
    num_samples = len(input_signal)
    
    # Low-frequency oscillators for modulating the delay, with a phase offset for stereo
    lfo_left = np.sin(2 * np.pi * rate * np.arange(num_samples) / SAMPLE_RATE)
    lfo_right = np.sin(2 * np.pi * rate * np.arange(num_samples) / SAMPLE_RATE + np.pi / 2)  # 90-degree phase shift
    
    # Delay in samples, modulated by the LFOs
    max_delay = int(SAMPLE_RATE * depth)
    delay_left = (1 + lfo_left * depth) * max_delay
    delay_right = (1 + lfo_right * depth) * max_delay

    # Prepare output signal with stereo channels
    output_signal = np.zeros((num_samples, 2))
    
    for i in range(num_samples):
        # Interpolate for fractional delay times
        delay_l = delay_left[i]
        delay_r = delay_right[i]
        
        # Left channel
        int_delay_l = int(np.floor(delay_l))
        frac_delay_l = delay_l - int_delay_l
        if i - int_delay_l >= 1:
            delayed_sample_l = (
                (1 - frac_delay_l) * input_signal[i - int_delay_l] + 
                frac_delay_l * input_signal[i - int_delay_l - 1]
            )
            output_signal[i, 0] = dry_wet * delayed_sample_l + (1 - dry_wet) * input_signal[i]
        else:
            output_signal[i, 0] = input_signal[i]  # No delay if out of bounds

        # Right channel
        int_delay_r = int(np.floor(delay_r))
        frac_delay_r = delay_r - int_delay_r
        if i - int_delay_r >= 1:
            delayed_sample_r = (
                (1 - frac_delay_r) * input_signal[i - int_delay_r] + 
                frac_delay_r * input_signal[i - int_delay_r - 1]
            )
            output_signal[i, 1] = dry_wet * delayed_sample_r + (1 - dry_wet) * input_signal[i]
        else:
            output_signal[i, 1] = input_signal[i]  # No delay if out of bounds

    return output_signal
