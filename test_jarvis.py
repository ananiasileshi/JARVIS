import requests
import os
from datetime import datetime

APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\ANANIA\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}

SEARCH_FOLDERS = [
    r"C:\Users\ANANIA\Desktop",
    r"C:\Users\ANANIA\Documents",
    r"C:\Users\ANANIA\Pictures",
    r"C:\Users\ANANIA\Videos",
    r"C:\Users\ANANIA\Downloads"
]


def find_file(query):
    matches = []

    for root in SEARCH_FOLDERS:
        if not os.path.exists(root):
            continue

        for folder, _, files in os.walk(root):
            for file in files:
                if query.lower() in file.lower():
                    matches.append(os.path.join(folder, file))

    return matches[:10]


while True:
    prompt = input("You: ").strip().lower()

    if prompt == "exit":
        print("Jarvis: Goodbye!")
        break

    # Open applications
    if prompt.startswith("open "):
        app = prompt.replace("open ", "")

        if app in APPS:
            os.startfile(APPS[app])
            print(f"Jarvis: Opening {app}...")
        else:
            print("Jarvis: I don't know that application yet.")

        continue

    # Time command
    if prompt == "what time is it":
        current_time = datetime.now().strftime("%I:%M %p")
        print(f"Jarvis: The time is {current_time}")
        continue

    # File search
    if prompt.startswith("find file "):
        query = prompt.replace("find file ", "")

        results = find_file(query)

        if results:
            print("Jarvis: I found these files:")
            for result in results:
                print("-", result)
        else:
            print("Jarvis: No matching files found.")

        continue

    # AI Chat
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma2:2b",
            "prompt": prompt,
            "stream": False
        }
    )

    print("Jarvis:", response.json()["response"])