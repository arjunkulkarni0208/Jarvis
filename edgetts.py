import asyncio
import edge_tts
from playsound import playsound
import os

filename = "edge_output.mp3"
async def speak(text):
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")  # Male voice
    await communicate.save(filename)

def talk(words):
    asyncio.run(speak(words))
    playsound(filename)
    os.remove(filename)
