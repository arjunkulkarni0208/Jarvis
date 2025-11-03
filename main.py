import requests
import whisper_stt as stt
import edgetts

def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"

def end():
    exit()

try:
    while True:
        if __name__ == "__main__":
            while True:
                user_input = "Pretext: My name is Arjun and your name is Jarvis. answer in short. Message: " + stt.record_and_transcribe()
                if user_input.lower() in ["exit", "quit"]:
                    break
                answer = ask_ollama(user_input)
                print("Jarvis:", answer)
                edgetts.talk(answer)

except KeyboardInterrupt:
    end()

