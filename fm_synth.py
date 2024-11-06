import numpy as np
import time
from tkinter import Tk, Scale, HORIZONTAL, Label, Button, OptionMenu, StringVar, Frame, ttk, Entry, IntVar
from scipy.signal import sawtooth, square
from queue import Queue
import threading
import soundfile as sf
import sounddevice as sd  # اضافه کردن sounddevice
from chorus_effect import juno_chorus
from moog_filter import MoogFilter
from ds_filter import DaveSmithFilter
from prophet5_filter import Prophet5Filter
from korg_ms20_filter import KorgMS20Filter
from oberheim_sem_filter import OberheimSEMFilter
from sequencer import Sequencer
from adsr_module import ADSR  # Import the new ADSR module

# GUI window setup
root = Tk()
root.title("FM Synthesizer with Enhanced Quality")
root.geometry("1200x800")

# Tab control setup
tab_control = ttk.Notebook(root)

# Synthesizer control tab
synth_tab = Frame(tab_control)
tab_control.add(synth_tab, text='Synthesizer Controls')

# Sequencer tab
sequencer_tab = Frame(tab_control)
tab_control.add(sequencer_tab, text='Sequencer')

# Audio Settings tab
audio_settings_tab = Frame(tab_control)
tab_control.add(audio_settings_tab, text='Audio Settings')

# Pack tabs
tab_control.pack(expand=1, fill='both')

# Synthesizer settings
SAMPLE_RATE = 48000
BUFFER_SIZE = 256

# Parameters (Define these parameters before creating filter objects)
attack, decay, sustain, release = 0.05, 0.2, 0.8, 0.3
cutoff_freq, resonance = 100, 0.7  # Defined before filter initialization
distortion_amount, wet_dry = 0.5, 0.5
chorus_rate, chorus_depth, chorus_mix = 0.8, 0.003, 0.5

# Initialize ADSR object
adsr = ADSR(sample_rate=SAMPLE_RATE, attack=attack, decay=decay, sustain=sustain, release=release)

# Initialize filter objects (after defining cutoff_freq and resonance)
filter_objects = {
    "Moog": MoogFilter(SAMPLE_RATE, cutoff_freq, resonance),
    "Dave Smith": DaveSmithFilter(SAMPLE_RATE, cutoff_freq, resonance),
    "Prophet-5": Prophet5Filter(SAMPLE_RATE, cutoff_freq, resonance),
    "Korg MS-20": KorgMS20Filter(SAMPLE_RATE, cutoff_freq, resonance),
    "Oberheim SEM": OberheimSEMFilter(SAMPLE_RATE, cutoff_freq, resonance)
}

# Variable to track selected filter
selected_filter = StringVar(root)
selected_filter.set("Moog")  # Default to Moog

# Sound buffer queue
sound_queue = Queue()

# Frames for layout organization in synth_tab
adsr_frame = Frame(synth_tab)
adsr_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
filter_frame = Frame(synth_tab)
filter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
distortion_frame = Frame(synth_tab)
distortion_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")
chorus_frame = Frame(synth_tab)
chorus_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")
note_frame = Frame(synth_tab)
note_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")

# Add a dropdown in the GUI for selecting the filter
Label(filter_frame, text="Select Filter").pack()
OptionMenu(filter_frame, selected_filter, *filter_objects.keys()).pack()

# Waveform generation
def generate_wave(frequency, waveform='sine', duration=1.0):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if waveform == 'sine':
        return np.sin(2 * np.pi * frequency * t)
    elif waveform == 'square':
        return square(2 * np.pi * frequency * t)
    elif waveform == 'sawtooth':
        return sawtooth(2 * np.pi * frequency * t)
    else:
        return np.zeros_like(t)

# Apply ADSR envelope
def apply_adsr(wave, duration, note_on_length):
    env = adsr.generate_envelope(duration=duration, note_on_length=note_on_length)
    return wave * env

# Apply selected filter
def apply_filter(wave, cutoff, resonance):
    # Update cutoff and resonance for the selected filter
    current_filter = filter_objects[selected_filter.get()]
    current_filter.cutoff = cutoff
    current_filter.resonance = resonance
    return current_filter.process(wave)

# Distortion
def apply_distortion(wave, amount, wet_dry):
    distorted_wave = np.tanh(amount * wave)
    return (wet_dry * distorted_wave) + ((1 - wet_dry) * wave)

# Audio settings variables
audio_sample_rate = IntVar(value=SAMPLE_RATE)
audio_buffer_size = IntVar(value=BUFFER_SIZE)
selected_device = StringVar()
selected_device_index = None  # Default device

# Function to get a list of available audio devices
def get_audio_devices():
    devices = sd.query_devices()
    device_names = [f"{idx}: {device['name']}" for idx, device in enumerate(devices)]
    return device_names

# Populate the dropdown with device names
device_names = get_audio_devices()
selected_device.set(device_names[sd.default.device[1]] if device_names else "No device found")

# Audio Settings Controls
Label(audio_settings_tab, text="Select Audio Device").pack()
device_menu = OptionMenu(audio_settings_tab, selected_device, *device_names)
device_menu.pack()

Label(audio_settings_tab, text="Sample Rate (Hz)").pack()
sample_rate_entry = Entry(audio_settings_tab, textvariable=audio_sample_rate)
sample_rate_entry.pack()

Label(audio_settings_tab, text="Buffer Size").pack()
buffer_size_entry = Entry(audio_settings_tab, textvariable=audio_buffer_size)
buffer_size_entry.pack()

# Apply audio settings button
def apply_audio_settings():
    global SAMPLE_RATE, BUFFER_SIZE, selected_device_index
    try:
        SAMPLE_RATE = int(audio_sample_rate.get())
        BUFFER_SIZE = int(audio_buffer_size.get())
        device_info = selected_device.get()

        # Extract device index from the selected string
        device_index = int(device_info.split(":")[0])
        selected_device_index = device_index

        # Set the default device in sounddevice
        sd.default.device = selected_device_index

        print("Audio settings updated:")
        print(f"Device: {device_info}, Sample Rate: {SAMPLE_RATE}, Buffer Size: {BUFFER_SIZE}")
    except ValueError:
        print("Invalid audio settings. Please enter valid integers.")

Button(audio_settings_tab, text="Apply Settings", command=apply_audio_settings).pack()

# FM generator
def generate_fm_sound(frequency, waveform, duration):
    # Step 1: Generate carrier and modulator waves
    carrier = generate_wave(frequency, waveform, duration)
    modulator = generate_wave(frequency * 0.5, waveform, duration)
    fm_wave = carrier * (1 + modulator)

    # Step 2: Apply ADSR envelope
    fm_wave = apply_adsr(fm_wave, duration, duration * 0.6)

    # Step 3: Apply selected filter
    fm_wave = apply_filter(fm_wave, cutoff_freq, resonance)

    # Step 4: Apply Chorus Effect
    fm_wave = juno_chorus(fm_wave, rate=chorus_rate, depth=chorus_depth, dry_wet=chorus_mix)

    # Step 5: Apply Distortion
    fm_wave = apply_distortion(fm_wave, distortion_amount, wet_dry)

    # Step 6: Return the final processed wave
    return fm_wave

# Add sound to the buffer
def mix_sounds():
    sounds = []
    base_freq = note_options[selected_note.get()]
    sounds.append(generate_fm_sound(base_freq, 'sine', 1.0))
    sounds.append(generate_fm_sound(base_freq * 0.75, 'sawtooth', 1.0))
    sounds.append(generate_fm_sound(base_freq * 1.5, 'square', 1.0))

    final_sound = np.sum(sounds, axis=0)
    final_sound = np.clip(final_sound, -1, 1)
    final_sound = (final_sound).astype(np.float32)  # تغییر نوع داده به float32

    if final_sound.ndim == 1:
        final_sound = np.column_stack((final_sound, final_sound))

    sound_queue.put(final_sound)
    sf.write('output_sound.wav', final_sound, SAMPLE_RATE)

# Sound playback thread
def play_sound_from_queue():
    while True:
        if not sound_queue.empty():
            sound_data = sound_queue.get()
            sd.play(sound_data, samplerate=SAMPLE_RATE, device=selected_device_index)
            sd.wait()

# Thread for continuous playback
sound_thread = threading.Thread(target=play_sound_from_queue, daemon=True)
sound_thread.start()

# Control update functions
def update_adsr(param, value):
    new_value = float(value) / 100
    if param in ["attack", "decay", "sustain", "release"]:
        adsr.set_params(**{param: new_value})

def update_filter(param, value):
    globals()[param] = float(value)

def update_distortion(param, value):
    globals()[param] = float(value) / 100

def update_chorus(param, value):
    globals()[param] = float(value)

def apply_accent(wave, accent_factor=1.5, position=0.5):
    accent_length = int(len(wave) * 0.1)  # 10% of the wave length as accent duration
    start_idx = int(len(wave) * position)

    wave[start_idx:start_idx + accent_length] *= accent_factor
    return np.clip(wave, -1, 1)  # To avoid clipping

# ADSR Controls
Label(adsr_frame, text="Attack").pack()
Scale(adsr_frame, from_=0, to=100, orient=HORIZONTAL, command=lambda v: update_adsr("attack", v)).pack()
Label(adsr_frame, text="Decay").pack()
Scale(adsr_frame, from_=0, to=100, orient=HORIZONTAL, command=lambda v: update_adsr("decay", v)).pack()
Label(adsr_frame, text="Sustain").pack()
Scale(adsr_frame, from_=0, to=100, orient=HORIZONTAL, command=lambda v: update_adsr("sustain", v)).pack()
Label(adsr_frame, text="Release").pack()
Scale(adsr_frame, from_=0, to=100, orient=HORIZONTAL, command=lambda v: update_adsr("release", v)).pack()

# Filter Controls
Label(filter_frame, text="Cutoff Frequency").pack()
Scale(filter_frame, from_=40, to=500, orient=HORIZONTAL, command=lambda v: update_filter("cutoff_freq", v)).pack()
Label(filter_frame, text="Resonance").pack()
Scale(filter_frame, from_=0, to=300, orient=HORIZONTAL, command=lambda v: update_filter("resonance", v)).pack()

# Distortion Controls
Label(distortion_frame, text="Distortion Amount").pack()
Scale(distortion_frame, from_=0, to=100, orient=HORIZONTAL, command=lambda v: update_distortion("distortion_amount", v)).pack()
Label(distortion_frame, text="Wet/Dry Mix").pack()
Scale(distortion_frame, from_=0, to=100, orient=HORIZONTAL, command=lambda v: update_distortion("wet_dry", v)).pack()

# Chorus Effect Controls
Label(chorus_frame, text="Chorus Rate").pack()
Scale(chorus_frame, from_=0.1, to=5, orient=HORIZONTAL, resolution=0.1, command=lambda v: update_chorus("chorus_rate", v)).pack()
Label(chorus_frame, text="Chorus Depth").pack()
Scale(chorus_frame, from_=0.001, to=0.01, orient=HORIZONTAL, resolution=0.001, command=lambda v: update_chorus("chorus_depth", v)).pack()
Label(chorus_frame, text="Chorus Mix").pack()
Scale(chorus_frame, from_=0, to=1, orient=HORIZONTAL, resolution=0.01, command=lambda v: update_chorus("chorus_mix", v)).pack()

# Note selection and play button
note_options = {
    "C2 (65.41 Hz)": 65.41,
    "C3 (130.81 Hz)": 130.81,
    "C4 (261.63 Hz)": 261.63,
    "C5 (523.25 Hz)": 523.25,
    "C6 (1046.50 Hz)": 1046.50
}
selected_note = StringVar(note_frame)
selected_note.set("C4 (261.63 Hz)")
Label(note_frame, text="Select Note").pack()
OptionMenu(note_frame, selected_note, *note_options.keys()).pack()
play_button = Button(note_frame, text="Play Sound", command=mix_sounds)
play_button.pack()

# Execute GUI mainloop
root.mainloop()
