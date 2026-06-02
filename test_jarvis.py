import requests
import os
from datetime import datetime

APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\ANANIA\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:2b"
TIMEOUT = 30


def find_file(query, root=r"C:\Users\ANANIA"):
    """Search for files matching the query (up to 5 results)."""
    matches = []
    try:
        for folder, _, files in os.walk(root):
            for file in files:
                if query.lower() in file.lower():
                    matches.append(os.path.join(folder, file))
            if len(matches) >= 5:
                break
    except Exception as e:
        print(f"Jarvis: Error searching files: {e}")
    return matches[:5]


def query_ollama(prompt):
    """Query Ollama API with error handling."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json().get("response", "I didn't get a valid response.")
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Is it running on localhost:11434?"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Ollama may be busy."
    except (ValueError, KeyError):
        return "Error: Invalid response from Ollama."
    except Exception as e:
        return f"Error: {str(e)}"


def show_help():
    """Display available commands."""
    commands = [
        "open [app] - Open an application (chrome, vscode)",
        "what time is it - Get current time",
        "what date is it - Get current date",
        "find file [query] - Search for files",
        "help - Show this message",
        "exit - Quit Jarvis"
    ]
    print("\nJarvis: Available commands:")
    for cmd in commands:
        print(f"  • {cmd}")
    print()


def main():
    """Main JARVIS conversation loop."""
    print("Jarvis: Hello! Type 'help' for commands.\n")
    
    while True:
        try:
            prompt = input("You: ").strip().lower()
            
            if not prompt:
                continue

            if prompt == "exit":
                print("Jarvis: Goodbye!")
                break

            if prompt == "help":
                show_help()
                continue

            # Open applications
            if prompt.startswith("open "):
                app = prompt.replace("open ", "").strip()
                if app in APPS:
                    os.startfile(APPS[app])
                    print(f"Jarvis: Opening {app}...\n")
                else:
                    print(f"Jarvis: I don't know '{app}'. Available: {', '.join(APPS.keys())}\n")
                continue

            # Time command
            if prompt == "what time is it":
                current_time = datetime.now().strftime("%I:%M %p")
                print(f"Jarvis: The time is {current_time}\n")
                continue

            # Date command
            if prompt == "what date is it":
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                print(f"Jarvis: Today is {current_date}\n")
                continue

            # File search
            if prompt.startswith("find file "):
                query = prompt.replace("find file ", "").strip()
                results = find_file(query)

                if results:
                    print("Jarvis: I found these files:")
                    for result in results:
                        print(f"  • {result}")
                    print()
                else:
                    print("Jarvis: No matching files found.\n")
                continue

            # AI chat with Ollama
            response = query_ollama(prompt)
            print(f"Jarvis: {response}\n")

        except KeyboardInterrupt:
            print("\n\nJarvis: Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Jarvis: An unexpected error occurred: {e}\n")


if __name__ == "__main__":
    main()