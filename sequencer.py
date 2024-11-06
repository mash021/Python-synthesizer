# sequencer.py (Sequencer Module with Graphical Step Control)
import time
import numpy as np
from tkinter import Tk, Button, StringVar, Label, Frame
import threading

class Sequencer:
    def __init__(self, sample_rate, step_duration, scale_notes, pattern_length=16):
        self.sample_rate = sample_rate
        self.step_duration = step_duration
        self.scale_notes = scale_notes
        self.pattern_length = pattern_length
        self.current_step = 0
        self.pattern = [scale_notes[i % len(scale_notes)] for i in range(pattern_length)]
        self.running = False  # Added to control sequencer state

        # GUI setup for manual control of sequencer steps
        self.root = Tk()
        self.root.title("Graphical Sequencer")
        self.root.geometry("800x200")
        
        # Frame for buttons
        self.sequencer_frame = Frame(self.root)
        self.sequencer_frame.grid(row=0, column=0, padx=10, pady=10)

        # Step buttons to visually control sequencer notes
        self.step_buttons = []
        for i in range(self.pattern_length):
            btn = Button(self.sequencer_frame, text=self.current_note_to_label(self.pattern[i]), command=lambda i=i: self.update_step(i), width=5, height=2)
            btn.grid(row=0, column=i, padx=5, pady=5)
            self.step_buttons.append(btn)
        
        # Start and Stop buttons
        self.control_frame = Frame(self.root)
        self.control_frame.grid(row=1, column=0, padx=10, pady=10)

        self.play_button = Button(self.control_frame, text="Play", command=self.start_sequencer, width=10, height=2)
        self.play_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = Button(self.control_frame, text="Stop", command=self.stop_sequencer, width=10, height=2)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

    def current_note_to_label(self, note_idx):
        labels = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4", "C5"]
        return labels[note_idx % len(labels)]

    def update_step(self, step_idx):
        current_note = self.pattern[step_idx]
        self.pattern[step_idx] = (current_note + 1) % len(self.scale_notes)
        self.step_buttons[step_idx].config(text=self.current_note_to_label(self.pattern[step_idx]))

    def next_note_frequency(self):
        note_frequency = self.pattern[self.current_step]
        self.current_step = (self.current_step + 1) % self.pattern_length
        return note_frequency

    def run_sequencer(self, play_callback):
        self.running = True  # Start the sequencer
        while self.running:
            frequency = self.next_note_frequency()
            play_callback(frequency)
            time.sleep(self.step_duration)

    def stop(self):
        self.running = False  # Stop the sequencer

    def start_sequencer(self):
        self.stop()  # Ensure any previous thread is stopped
        self.sequencer_thread = threading.Thread(target=self.run_sequencer, args=(self.play_callback,), daemon=True)
        self.sequencer_thread.start()

    def stop_sequencer(self):
        self.stop()

    def play_callback(self, frequency):
        print(f"Playing frequency: {frequency} Hz")
        # This function should be overridden to integrate with the synthesizer

    def run_gui(self):
        self.root.mainloop()

# Example usage:
# The A Minor scale notes in frequency (in Hz)
a_minor_scale = [220.0, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00]

# Initialize the sequencer with a sample rate of 48 kHz, a step duration of 0.5 seconds, and A minor scale
# sequencer = Sequencer(sample_rate=48000, step_duration=0.5, scale_notes=a_minor_scale)
# sequencer.run_gui()
