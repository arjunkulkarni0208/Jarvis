import whisper
import speech_input as rec

def record_and_transcribe(duration=5, sample_rate=16000):
    print("🎯 Hold 'R' key to record; release to stop.")
    rec.record_while_holding_r()


    print("🧠 Loading Whisper model...")
    model = whisper.load_model("small")
    print("🔍 Transcribing...")
    result = model.transcribe('output.wav')
    print("📝 You said:", result["text"])
    return result["text"]
