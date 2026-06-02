import requests
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

while True:
    prompt = input("You: ").strip().lower()

    if prompt == "exit":
        print("Jarvis: Goodbye!")
        break

    if prompt == "open chrome":
        os.startfile(CHROME_PATH)
        print("Jarvis: Opening Chrome...")
        continue

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma2:2b",
            "prompt": prompt,
            "stream": False
        }
    )

    print("Jarvis:", response.json()["response"])