import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pynput import keyboard

def record_while_holding_r(sample_rate=16000):
    print("🎯 Hold the 'R' key to start recording...")

    frames = []
    recording = False
    finished = False

    def on_press(key):
        nonlocal recording
        try:
            if key.char == 'r' and not recording:
                print("🔴 Recording...")
                recording = True
        except AttributeError:
            pass

    def on_release(key):
        nonlocal recording, finished
        try:
            if key.char == 'r' and recording:
                print("⏹️  Stopped recording.")
                recording = False
                finished = True
                return False  # stop listener
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # loop: record frames until finished becomes True
    while not finished:
        if recording:
            data = sd.rec(1024, samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait()
            frames.append(data)

    if frames:
        audio = np.concatenate(frames, axis=0)
        write("output.wav", sample_rate, audio)
        print("✅ Saved recording as output.wav")
    else:
        print("⚠️ No audio recorded.")

if __name__ == "__main__":
    record_while_holding_r()
