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

last_search_results = []


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

    # Natural language commands
    if "time" in prompt:
        current_time = datetime.now().strftime("%I:%M %p")
        print(f"Jarvis: The time is {current_time}")
        continue

    if "open chrome" in prompt:
        os.startfile(APPS["chrome"])
        print("Jarvis: Opening Chrome...")
        continue

    if "open vscode" in prompt or "open vs code" in prompt:
        os.startfile(APPS["vscode"])
        print("Jarvis: Opening VS Code...")
        continue

    # File search
    if prompt.startswith("find file "):
        query = prompt.replace("find file ", "")

        results = find_file(query)
        last_search_results = results

        if results:
            print("Jarvis: I found these files:")
            for i, result in enumerate(results, start=1):
                print(f"{i}. {result}")
        else:
            print("Jarvis: No matching files found.")

        continue

    # Open searched file
    if prompt.startswith("open file "):
        try:
            index = int(prompt.replace("open file ", "")) - 1

            if 0 <= index < len(last_search_results):
                os.startfile(last_search_results[index])
                print("Jarvis: Opening file...")
            else:
                print("Jarvis: Invalid file number.")

        except ValueError:
            print("Jarvis: Please provide a valid file number.")

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