import sounddevice as sd
import numpy as np

duration = 3  # seconds
fs = 16000
print("Recording...")
rec = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()
print("Playing back...")
sd.play(rec, fs)
sd.wait()
print("Done.")
