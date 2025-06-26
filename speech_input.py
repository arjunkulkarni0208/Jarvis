import speech_recognition as sr

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except Exception as e:
        print("Error:", e)
        return ""
