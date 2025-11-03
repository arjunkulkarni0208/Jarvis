from gtts import gTTS
from playsound import playsound
import os

def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = "demo.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)
