import whisper
import sounddevice as sd
from scipy.io.wavfile import write

def record_and_transcribe(duration=5, sample_rate=16000):
    print("🎙️ Recording... Speak now.")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    write("temp.wav", sample_rate, recording)

    print("🧠 Loading Whisper model...")
    model = whisper.load_model("small")
    print("🔍 Transcribing...")
    result = model.transcribe("temp.wav")
    print("📝 You said:", result["text"])
    return result["text"]
