#!/usr/bin/env python3
"""
JARVIS — Advanced AI Assistant
Powered by Ollama (Gemma2) with 50+ features
"""

import requests
import os
import sys
import json
import math
import random
import string
import time
import threading
import subprocess
import webbrowser
import platform
import socket
import re
import traceback
import hashlib
import base64
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

# ─── Optional Imports (graceful fallback) ──────────────────────────────
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

try:
    import speedtest as st_mod
    HAS_SPEEDTEST = True
except ImportError:
    HAS_SPEEDTEST = False

# ─── Paths ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "jarvis_config.json"
NOTES_FILE = BASE_DIR / "jarvis_notes.json"
TODOS_FILE = BASE_DIR / "jarvis_todos.json"
HISTORY_FILE = BASE_DIR / "jarvis_history.json"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
DOWNLOAD_DIR = BASE_DIR / "downloads"

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "gemma2:2b"

IS_WINDOWS = platform.system() == "Windows"

# ─── App Paths (CUSTOMIZE FOR YOUR SYSTEM) ─────────────────────────────
APPS = {
    "chrome":      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode":      r"C:\Users\ANANIA\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad":     "notepad.exe",
    "calc":        "calc.exe",
    "calculator":  "calc.exe",
    "cmd":         "cmd.exe",
    "powershell":  "powershell.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "file explorer": "explorer.exe",
    "terminal":    "wt.exe",
    "paint":       "mspaint.exe",
    "snip":        "SnippingTool.exe",
    "word":        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":       r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":  r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "spotify":     r"C:\Users\ANANIA\AppData\Roaming\Spotify\Spotify.exe",
    "discord":     r"C:\Users\ANANIA\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "steam":       r"C:\Program Files (x86)\Steam\steam.exe",
    "vlc":         r"C:\Program Files\VideoLAN\VLC\vlc.exe",
}

WEBSITE_ALIASES = {
    "google":       "https://www.google.com",
    "youtube":      "https://www.youtube.com",
    "github":       "https://github.com",
    "stackoverflow":"https://stackoverflow.com",
    "reddit":       "https://www.reddit.com",
    "twitter":      "https://twitter.com",
    "x":            "https://x.com",
    "facebook":     "https://www.facebook.com",
    "instagram":    "https://www.instagram.com",
    "linkedin":     "https://www.linkedin.com",
    "amazon":       "https://www.amazon.com",
    "netflix":      "https://www.netflix.com",
    "wikipedia":    "https://www.wikipedia.org",
    "chatgpt":      "https://chat.openai.com",
    "gmail":        "https://mail.google.com",
    "drive":        "https://drive.google.com",
    "maps":         "https://maps.google.com",
    "translate":    "https://translate.google.com",
    "news":         "https://news.google.com",
    "weather":      "https://weather.com",
    "twitch":       "https://www.twitch.tv",
    "spotify web":  "https://open.spotify.com",
    "whatsapp":     "https://web.whatsapp.com",
    "telegram":     "https://web.telegram.org",
}

# ─── Helpers ───────────────────────────────────────────────────────────
COLORS = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
    "white": "\033[97m", "bold": "\033[1m", "dim": "\033[2m",
    "underline": "\033[4m",
}
RESET = "\033[0m"


def colored(text, color="white"):
    return f"{COLORS.get(color, '')}{text}{RESET}"


def fmt_size(n):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def jprint(text, color="cyan"):
    print(colored(f"  Jarvis: {text}", color))


def confirm(prompt_text):
    ans = input(colored(f"  ⚠  {prompt_text} [y/N]: ", "yellow")).strip().lower()
    return ans in ("y", "yes")


# ─── TTS Speaker (lazy init) ──────────────────────────────────────────
_tts_engine = None


def speak(text):
    global _tts_engine
    if not (HAS_TTS and jarvis and jarvis.tts_enabled):
        return
    try:
        if _tts_engine is None:
            _tts_engine = pyttsx3.init()
            _tts_engine.setProperty("rate", 185)
        _tts_engine.say(text)
        _tts_engine.runAndWait()
    except Exception:
        pass


def jprint_say(text, color="cyan"):
    jprint(text, color)
    speak(text)


# ─── Banner ────────────────────────────────────────────────────────────
def banner():
    print(colored(r"""
    ╔═══════════════════════════════════════════════════════════╗
    ║      ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗            ║
    ║      ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝            ║
    ║      ██║███████║██████╔╝██║   ██║██║███████╗            ║
    ║      ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║            ║
    ║      ██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║            ║
    ║      ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝            ║
    ║       A D V A N C E D   A S S I S T A N T                ║
    ║       Powered by Ollama · Gemma2 · Python                ║
    ╚═══════════════════════════════════════════════════════════╝
""", "cyan"))


def feature_status():
    """Show which optional features are loaded."""
    features = [
        ("System Monitor (psutil)", HAS_PSUTIL),
        ("Clipboard (pyperclip)", HAS_PYPERCLIP),
        ("Screenshots (Pillow)", HAS_PIL),
        ("Text-to-Speech (pyttsx3)", HAS_TTS),
        ("Voice Input (SpeechRecognition)", HAS_SR),
        ("QR Codes (qrcode)", HAS_QRCODE),
        ("Speed Test (speedtest-cli)", HAS_SPEEDTEST),
    ]
    print(colored("  ── Module Status ──────────────────────────────", "dim"))
    for name, ok in features:
        sym = colored("✔", "green") if ok else colored("✘", "red")
        print(f"    {sym}  {name}")
    print(colored("  ────────────────────────────────────────────────", "dim"))


# ═══════════════════════════════════════════════════════════════════════
#  JARVIS CLASS
# ═══════════════════════════════════════════════════════════════════════
class Jarvis:
    def __init__(self):
        self.tts_enabled = False
        self.conversation_history = []
        self.reminders = []
        self.system_prompt = (
            "You are JARVIS, an advanced AI assistant inspired by Iron Man's AI. "
            "You are helpful, witty, concise, and slightly sarcastic. "
            "Keep responses short unless asked to elaborate. "
            "Use metric units by default. Address the user as 'Sir'."
        )
        self._ensure_dirs()
        self.notes = self._load_json(NOTES_FILE, [])
        self.todos = self._load_json(TODOS_FILE, [])
        self.aliases = self._load_json(BASE_DIR / "jarvis_aliases.json", {})

    # ── persistence helpers ────────────────────────────────────────
    @staticmethod
    def _ensure_dirs():
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        DOWNLOAD_DIR.mkdir(exist_ok=True)

    @staticmethod
    def _load_json(path, default):
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    @staticmethod
    def _save_json(path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            jprint(f"Save error: {e}", "red")

    def _persist_notes(self):
        self._save_json(NOTES_FILE, self.notes)

    def _persist_todos(self):
        self._save_json(TODOS_FILE, self.todos)

    def _persist_history(self):
        self._save_json(HISTORY_FILE, self.conversation_history[-100:])

    def _persist_aliases(self):
        self._save_json(BASE_DIR / "jarvis_aliases.json", self.aliases)

    # ── LLM ────────────────────────────────────────────────────────
    def ask_gemma(self, prompt, use_history=True):
        messages = [{"role": "system", "content": self.system_prompt}]
        if use_history:
            messages.extend(self.conversation_history[-12:])
        messages.append({"role": "user", "content": prompt})
        try:
            resp = requests.post(OLLAMA_CHAT_URL, json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
            }, timeout=120)
            reply = resp.json()["message"]["content"].strip()
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": reply})
            if len(self.conversation_history) > 60:
                self.conversation_history = self.conversation_history[-60:]
            return reply
        except requests.exceptions.ConnectionError:
            return "I can't reach Ollama. Is it running?  →  ollama serve"
        except Exception as e:
            return f"AI error: {e}"

    # ── Open Apps ──────────────────────────────────────────────────
    def open_app(self, name):
        name = name.strip().lower()
        # check aliases first
        if name in self.aliases:
            path = self.aliases[name]
        elif name in APPS:
            path = APPS[name]
        else:
            # try system PATH
            try:
                if IS_WINDOWS:
                    subprocess.Popen(["where", name],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.startfile(name)
                else:
                    subprocess.Popen(["which", name])
                    subprocess.Popen(["xdg-open", name])
                jprint_say(f"Trying to launch '{name}' via system PATH...")
                return
            except Exception:
                jprint_say(f"I don't know '{name}'. Add it with: alias {name} = <path>", "yellow")
                return
        try:
            if IS_WINDOWS:
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
            jprint_say(f"Opening {name}...")
        except Exception as e:
            jprint_say(f"Failed to open {name}: {e}", "red")

    # ── Open Websites ──────────────────────────────────────────────
    def open_website(self, site):
        site = site.strip().lower()
        if site in WEBSITE_ALIASES:
            url = WEBSITE_ALIASES[site]
        elif "." in site:
            url = site if site.startswith("http") else f"https://{site}"
        else:
            url = f"https://www.google.com/search?q={quote_plus(site)}"
        webbrowser.open(url)
        jprint_say(f"Opening {url}...")

    # ── Time / Date ────────────────────────────────────────────────
    def get_time(self):
        t = datetime.now().strftime("%I:%M %p")
        jprint_say(f"The time is {t}")

    def get_date(self):
        d = datetime.now().strftime("%A, %B %d, %Y")
        jprint_say(f"Today is {d}")

    def get_datetime(self):
        d = datetime.now().strftime("%A, %B %d, %Y  ·  %I:%M %p")
        jprint_say(f"It's {d}")

    def uptime(self):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        boot = datetime.fromtimestamp(psutil.boot_time())
        delta = datetime.now() - boot
        s = int(delta.total_seconds())
        d, h, m, sec = s // 86400, s % 86400 // 3600, s % 3600 // 60, s % 60
        jprint_say(f"Uptime: {d}d {h}h {m}m {sec}s")

    # ── Weather ────────────────────────────────────────────────────
    def get_weather(self, city=""):
        try:
            if not city:
                geo = requests.get("https://ipapi.co/json/", timeout=5).json()
                city = geo.get("city", "New York")
            resp = requests.get(
                f"https://wttr.in/{quote_plus(city)}?format=j1", timeout=10
            ).json()
            c = resp["current_condition"][0]
            desc = c["weatherDesc"][0]["value"]
            temp_c, temp_f = c["temp_C"], c["temp_F"]
            feels = c["FeelsLikeC"]
            hum, wind = c["humidity"], c["windspeedKmph"]
            vis = c["visibility"]
            uv = c["uvIndex"]
            print(colored(f"  Jarvis: 🌤  Weather in {city.title()}", "cyan"))
            print(f"         {desc}")
            print(f"         🌡  {temp_c}°C ({temp_f}°F) · Feels {feels}°C")
            print(f"         💧 Humidity {hum}%  ·  💨 Wind {wind} km/h")
            print(f"         👁  Visibility {vis} km  ·  ☀  UV Index {uv}")
        except Exception as e:
            jprint(f"Weather error: {e}", "red")

    # ── System Info ────────────────────────────────────────────────
    def system_info(self):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\" if IS_WINDOWS else "/")
        bat = psutil.sensors_battery()
        boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
        pcount = len(psutil.pids())
        print(colored("  Jarvis: 🖥  System Report", "cyan"))
        print(f"         OS       : {platform.system()} {platform.release()} ({platform.machine()})")
        print(f"         Hostname : {socket.gethostname()}")
        print(f"         Python   : {platform.python_version()}")
        print(f"         CPU      : {cpu}%  ·  Cores: {psutil.cpu_count(logical=False)}P / {psutil.cpu_count()}L")
        bar_mem = "█" * int(mem.percent / 2) + "░" * (50 - int(mem.percent / 2))
        print(f"         RAM      : [{bar_mem}] {mem.percent}%  ({fmt_size(mem.used)} / {fmt_size(mem.total)})")
        bar_disk = "█" * int(disk.percent / 2) + "░" * (50 - int(disk.percent / 2))
        print(f"         Disk     : [{bar_disk}] {disk.percent}%  ({fmt_size(disk.used)} / {fmt_size(disk.total)})")
        if bat:
            plug = "🔌" if bat.power_plugged else "🔋"
            print(f"         Battery  : {plug} {bat.percent}%")
        print(f"         Booted   : {boot}")
        print(f"         Processes: {pcount}")

    # ── Processes ──────────────────────────────────────────────────
    def list_processes(self, filt=""):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                i = p.info
                if filt and filt.lower() not in (i["name"] or "").lower():
                    continue
                procs.append(i)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x["memory_percent"] or 0, reverse=True)
        print(colored("  Jarvis: Top Processes (by memory)", "cyan"))
        print(f"         {'PID':<9}{'Name':<32}{'CPU%':<9}{'MEM%':<9}{'Status'}")
        print(f"         {'─' * 70}")
        for p in procs[:25]:
            print(f"         {p['pid']:<9}{p['name']:<32}"
                  f"{p['cpu_percent'] or 0:<9.1f}{p['memory_percent'] or 0:<9.1f}{p.get('status', '')}")

    def kill_process(self, target):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        try:
            pid = int(target)
            psutil.Process(pid).terminate()
            jprint_say(f"Terminated PID {pid}")
        except ValueError:
            killed = 0
            for p in psutil.process_iter(["name", "pid"]):
                if target.lower() in p.info["name"].lower():
                    try:
                        p.terminate()
                        killed += 1
                    except Exception:
                        pass
            jprint_say(f"Terminated {killed} process(es) matching '{target}'")

    # ── Notes ──────────────────────────────────────────────────────
    def add_note(self, text):
        self.notes.append({"text": text, "ts": datetime.now().isoformat()})
        self._persist_notes()
        jprint_say(f"📝 Note saved. (Total: {len(self.notes)})")

    def list_notes(self):
        if not self.notes:
            jprint("No notes yet."); return
        print(colored("  Jarvis: 📝 Notes", "cyan"))
        for i, n in enumerate(self.notes, 1):
            ts = n.get("ts", "")[:16]
            print(f"         {colored(f'[{i}]', 'yellow')} ({ts}) {n['text']}")

    def search_notes(self, q):
        hits = [n for n in self.notes if q.lower() in n["text"].lower()]
        if not hits:
            jprint(f"No notes matching '{q}'"); return
        print(colored(f"  Jarvis: Notes matching '{q}'", "cyan"))
        for i, n in enumerate(hits, 1):
            print(f"         {colored(f'[{i}]', 'yellow')} {n['text']}")

    def delete_note(self, idx):
        try:
            removed = self.notes.pop(int(idx) - 1)
            self._persist_notes()
            jprint_say(f"🗑 Deleted note: {removed['text'][:60]}")
        except (ValueError, IndexError):
            jprint("Invalid note number.", "red")

    def clear_notes(self):
        if confirm("Delete ALL notes?"):
            self.notes.clear(); self._persist_notes()
            jprint_say("🗑 All notes cleared.")

    # ── Todos ──────────────────────────────────────────────────────
    def add_todo(self, text):
        self.todos.append({"text": text, "done": False, "ts": datetime.now().isoformat()})
        self._persist_todos()
        jprint_say(f"✅ Todo added. (Total: {len(self.todos)})")

    def list_todos(self):
        if not self.todos:
            jprint("Todo list is empty!"); return
        print(colored("  Jarvis: ✅ Todo List", "cyan"))
        for i, t in enumerate(self.todos, 1):
            mark = colored("✓", "green") if t["done"] else colored("○", "yellow")
            txt = colored(t["text"], "dim") if t["done"] else t["text"]
            print(f"         {mark} {colored(f'[{i}]', 'yellow')} {txt}")

    def complete_todo(self, idx):
        try:
            self.todos[int(idx) - 1]["done"] = True
            self._persist_todos()
            jprint_say(f"🎉 Marked '{self.todos[int(idx)-1]['text']}' as done!")
        except (ValueError, IndexError):
            jprint("Invalid number.", "red")

    def delete_todo(self, idx):
        try:
            removed = self.todos.pop(int(idx) - 1)
            self._persist_todos()
            jprint_say(f"🗑 Removed: {removed['text']}")
        except (ValueError, IndexError):
            jprint("Invalid number.", "red")

    def clear_todos(self):
        if confirm("Delete ALL todos?"):
            self.todos.clear(); self._persist_todos()
            jprint_say("🗑 Todo list cleared.")

    # ── Reminders ──────────────────────────────────────────────────
    def set_reminder(self, text, minutes):
        t = datetime.now() + timedelta(minutes=minutes)
        self.reminders.append({"text": text, "time": t})

        def _watch():
            while self.reminders:
                time.sleep(5)
                now = datetime.now()
                for r in self.reminders[:]:
                    if now >= r["time"]:
                        print(colored(f"\n  ⏰ REMINDER: {r['text']}", "yellow"))
                        speak(f"Reminder: {r['text']}")
                        self.reminders.remove(r)

        threading.Thread(target=_watch, daemon=True).start()
        jprint_say(f"⏰ Reminder in {minutes} min: {text}")

    # ── Timer ──────────────────────────────────────────────────────
    def set_timer(self, secs, label="Timer"):
        def _run():
            r = int(secs)
            while r > 0:
                h, m, s = r // 3600, r % 3600 // 60, r % 60
                print(f"\r         ⏱  {label}: {h:02d}:{m:02d}:{s:02d}", end="", flush=True)
                time.sleep(1)
                r -= 1
            print(colored(f"\n  ⏰ {label} done!", "yellow"))
            speak(f"{label} finished!")

        threading.Thread(target=_run, daemon=True).start()
        jprint(f"⏱ Timer set for {secs}s.")

    # ── Calculator ─────────────────────────────────────────────────
    def calculate(self, expr):
        safe = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "divmod": divmod,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "asin": math.asin, "acos": math.acos,
            "atan": math.atan, "log": math.log, "log2": math.log2,
            "log10": math.log10, "pi": math.pi, "e": math.e,
            "ceil": math.ceil, "floor": math.floor,
            "factorial": math.factorial, "gcd": math.gcd,
            "degrees": math.degrees, "radians": math.radians,
            "exp": math.exp, "modf": math.modf,
        }
        try:
            result = eval(expr, safe)
            jprint_say(f"🧮 {expr} = {result}")
        except Exception as e:
            jprint(f"Calc error: {e}", "red")

    # ── Screenshot ─────────────────────────────────────────────────
    def take_screenshot(self):
        if not HAS_PIL:
            jprint("Install Pillow.", "yellow"); return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOT_DIR / f"screenshot_{ts}.png"
        ImageGrab.grab().save(str(path))
        jprint_say(f"📸 Saved: {path}")

    # ── Clipboard ──────────────────────────────────────────────────
    def read_clipboard(self):
        if not HAS_PYPERCLIP:
            jprint("Install pyperclip.", "yellow"); return
        t = pyperclip.paste()
        jprint(f"📋 {t[:300]}{'…' if len(t) > 300 else ''}")

    def copy_to_clipboard(self, text):
        if not HAS_PYPERCLIP:
            jprint("Install pyperclip.", "yellow"); return
        pyperclip.copy(text)
        jprint("📋 Copied!")

    # ── Password Generator ─────────────────────────────────────────
    def gen_password(self, length=20):
        chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        pw = "".join(random.choices(chars, k=length))
        # guarantee at least one of each type
        pw = (random.choice(string.ascii_uppercase) +
              random.choice(string.ascii_lowercase) +
              random.choice(string.digits) +
              random.choice("!@#$%^&*") +
              pw[4:])
        pw_list = list(pw)
        random.shuffle(pw_list)
        pw = "".join(pw_list)
        print(colored(f"  Jarvis: 🔑 Password ({length} chars)", "cyan"))
        print(f"         {pw}")
        strength = "Strong" if length >= 16 else "Medium" if length >= 10 else "Weak"
        print(f"         Strength: {strength}")
        if HAS_PYPERCLIP:
            pyperclip.copy(pw)
            print(colored("         (Copied to clipboard)", "dim"))

    # ── QR Code ────────────────────────────────────────────────────
    def gen_qr(self, data):
        if not HAS_QRCODE:
            jprint("Install qrcode[pil].", "yellow"); return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = BASE_DIR / f"qr_{ts}.png"
        qrcode.make(data).save(str(path))
        jprint_say(f"📱 QR saved: {path}")

    # ── IP Address ─────────────────────────────────────────────────
    def get_ip(self):
        try:
            local = socket.gethostbyname(socket.gethostname())
            public = requests.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
            jprint(f"🌐 Local: {local}  ·  Public: {public}")
        except Exception:
            jprint(f"🌐 Local: {socket.gethostbyname(socket.gethostname())}")

    # ── Web Search ─────────────────────────────────────────────────
    def search_web(self, q):
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(q)}")
        jprint_say(f"🔍 Searching: {q}")

    # ── Wikipedia ──────────────────────────────────────────────────
    def search_wiki(self, q):
        try:
            data = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(q)}",
                timeout=10,
            ).json()
            if "extract" in data:
                title = data.get("title", q)
                ext = data["extract"]
                thumb = data.get("thumbnail", {}).get("source", "")
                print(colored(f"  Jarvis: 📚 {title}", "cyan"))
                if thumb:
                    print(f"         🖼  {thumb}")
                print(f"         {ext[:600]}{'…' if len(ext) > 600 else ''}")
            else:
                jprint(f"No Wikipedia result for '{q}'.", "yellow")
        except Exception as e:
            jprint(f"Wiki error: {e}", "red")

    # ── Dictionary ─────────────────────────────────────────────────
    def define(self, word):
        try:
            data = requests.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote_plus(word)}",
                timeout=10,
            ).json()
            if isinstance(data, list) and data:
                entry = data[0]
                print(colored(f"  Jarvis: 📖 {entry.get('word', word)}", "cyan"))
                for i, meaning in enumerate(entry.get("meanings", [])[:3], 1):
                    pos = meaning.get("partOfSpeech", "")
                    defn = meaning["definitions"][0]["definition"] if meaning["definitions"] else ""
                    print(f"         {i}. ({pos}) {defn}")
            else:
                jprint(f"No definition for '{word}'.", "yellow")
        except Exception as e:
            jprint(f"Dict error: {e}", "red")

    # ── Joke ───────────────────────────────────────────────────────
    def tell_joke(self):
        try:
            d = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5).json()
            jprint(f"😄 {d['setup']}")
            time.sleep(1.5)
            print(f"         {colored(d['punchline'], 'yellow')}")
        except Exception:
            jokes = [
                ("Why do programmers prefer dark mode?", "Because light attracts bugs!"),
                ("Why did the developer go broke?", "Because he used up all his cache."),
                ("What's a programmer's favourite hangout?", "Foo Bar."),
                ("Why do Java devs wear glasses?", "Because they can't C#."),
                ("There are 10 types of people.", "Those who understand binary and those who don't."),
                ("A SQL query walks into a bar...", "Walks up to two tables and asks 'Can I join you?'"),
                ("Why was the JavaScript developer sad?", "Because he didn't Node how to Express himself."),
            ]
            j, p = random.choice(jokes)
            jprint(f"😄 {j}")
            time.sleep(1.5)
            print(f"         {colored(p, 'yellow')}")

    # ── Unit Converter ─────────────────────────────────────────────
    def convert_unit(self, expr):
        conv = {
            ("c", "f"): lambda x: x * 9 / 5 + 32,
            ("f", "c"): lambda x: (x - 32) * 5 / 9,
            ("km", "mi"): lambda x: x * 0.621371,
            ("mi", "km"): lambda x: x * 1.60934,
            ("kg", "lb"): lambda x: x * 2.20462,
            ("lb", "kg"): lambda x: x * 0.453592,
            ("cm", "in"): lambda x: x * 0.393701,
            ("in", "cm"): lambda x: x * 2.54,
            ("m", "ft"): lambda x: x * 3.28084,
            ("ft", "m"): lambda x: x * 0.3048,
            ("l", "gal"): lambda x: x * 0.264172,
            ("gal", "l"): lambda x: x * 3.78541,
            ("mb", "gb"): lambda x: x / 1024,
            ("gb", "mb"): lambda x: x * 1024,
            ("gb", "tb"): lambda x: x / 1024,
            ("tb", "gb"): lambda x: x * 1024,
            ("oz", "ml"): lambda x: x * 29.5735,
            ("ml", "oz"): lambda x: x * 0.033814,
            ("hp", "kw"): lambda x: x * 0.7457,
            ("kw", "hp"): lambda x: x * 1.34102,
        }
        m = re.match(r"([\d.]+)\s*(\w+)\s+to\s+(\w+)", expr.strip().lower())
        if m:
            v, f, t = float(m.group(1)), m.group(2), m.group(3)
            if (f, t) in conv:
                r = conv[(f, t)](v)
                jprint_say(f"🔄 {v} {f} = {r:.4f} {t}")
                return
        jprint("Try: '100 c to f', '5 km to mi', '10 kg to lb'", "yellow")

    # ── File Ops ───────────────────────────────────────────────────
    def list_dir(self, path="."):
        try:
            items = sorted(os.listdir(path))
            print(colored(f"  Jarvis: 📂 {os.path.abspath(path)}", "cyan"))
            for item in items[:40]:
                full = os.path.join(path, item)
                icon = "📁" if os.path.isdir(full) else "📄"
                sz = ""
                if not os.path.isdir(full):
                    try:
                        sz = f"  ({fmt_size(os.path.getsize(full))})"
                    except Exception:
                        pass
                print(f"         {icon} {item}{sz}")
            if len(items) > 40:
                print(f"         … and {len(items) - 40} more")
        except Exception as e:
            jprint(f"Error: {e}", "red")

    def read_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read().split("\n")
            print(colored(f"  Jarvis: 📄 {path}  ({len(lines)} lines)", "cyan"))
            for ln in lines[:35]:
                print(f"         {ln}")
            if len(lines) > 35:
                print(f"         … ({len(lines) - 35} more lines)")
        except Exception as e:
            jprint(f"Error: {e}", "red")

    def create_file(self, path, content=""):
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            jprint_say(f"📄 Created: {path}")
        except Exception as e:
            jprint(f"Error: {e}", "red")

    def delete_file(self, path):
        if not confirm(f"Delete '{path}'?"):
            return
        try:
            os.remove(path)
            jprint_say(f"🗑 Deleted: {path}")
        except Exception as e:
            jprint(f"Error: {e}", "red")

    def download_file(self, url, fname=None):
        try:
            jprint("⬇ Downloading…")
            r = requests.get(url, stream=True, timeout=120)
            if not fname:
                fname = url.split("/")[-1].split("?")[0] or "download"
            path = DOWNLOAD_DIR / fname
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = done / total * 100
                        print(f"\r         {pct:.1f}%  ({fmt_size(done)}/{fmt_size(total)})", end="", flush=True)
            print()
            jprint_say(f"✅ Saved: {path}  ({fmt_size(done)})")
        except Exception as e:
            jprint(f"Download failed: {e}", "red")

    # ── System Controls (Windows) ──────────────────────────────────
    def system_control(self, action):
        if not IS_WINDOWS:
            jprint("Windows-only.", "yellow"); return
        cmds = {
            "shutdown":        "shutdown /s /t 60",
            "restart":         "shutdown /r /t 60",
            "lock":            "rundll32.exe user32.dll,LockWorkStation",
            "sleep":           "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            "hibernate":       "shutdown /h",
            "log off":         "shutdown /l",
            "cancel shutdown": "shutdown /a",
        }
        cmd = cmds.get(action)
        if cmd:
            dangerous = action in ("shutdown", "restart", "hibernate", "log off")
            if dangerous and not confirm(f"Are you sure you want to {action}?"):
                jprint("Cancelled."); return
            os.system(cmd)
            jprint_say(f"🖥 {action.title()}")
        else:
            jprint(f"Unknown. Options: {', '.join(cmds)}", "yellow")

    # ── Volume ─────────────────────────────────────────────────────
    def set_volume(self, level):
        if not IS_WINDOWS:
            jprint("Windows-only.", "yellow"); return
        try:
            lvl = max(0, min(100, int(level)))
            ps = f"""
            Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class Vol{{[DllImport("user32.dll")]public static extern void keybd_event(byte b,bool f,int dw,IntPtr ex);}}'
            1..50|foreach{{[Vol]::keybd_event(174,$false,0,[IntPtr]::Zero)}}
            1..{lvl // 2}|foreach{{[Vol]::keybd_event(175,$false,0,[IntPtr]::Zero)}}
            """
            subprocess.run(["powershell", "-Command", ps], capture_output=True)
            jprint_say(f"🔊 Volume ~{lvl}%")
        except Exception:
            jprint("Volume error.", "red")

    def mute_toggle(self):
        if not IS_WINDOWS:
            jprint("Windows-only.", "yellow"); return
        try:
            ps = 'Add-Type -TypeDefinition \'using System;using System.Runtime.InteropServices;public class V{[DllImport("user32.dll")]public static extern void keybd_event(byte b,bool f,int d,IntPtr x);}\' ; [V]::keybd_event(173,$false,0,[IntPtr]::Zero)'
            subprocess.run(["powershell", "-Command", ps], capture_output=True)
            jprint_say("🔇 Mute toggled")
        except Exception:
            jprint("Mute error.", "red")

    # ── Battery ────────────────────────────────────────────────────
    def battery_status(self):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        b = psutil.sensors_battery()
        if b:
            icon = "🔌" if b.power_plugged else "🔋"
            jprint(f"{icon} {b.percent}%")
            if not b.power_plugged and b.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
                h, m = divmod(b.secsleft // 60, 60)
                print(f"         ~{h}h {m}m remaining")
        else:
            jprint("No battery info.", "yellow")

    # ── Disk Usage ─────────────────────────────────────────────────
    def disk_usage(self, drive=None):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        if drive is None:
            drive = "C:\\" if IS_WINDOWS else "/"
        try:
            d = psutil.disk_usage(drive)
            bar = "█" * int(d.percent / 2) + "░" * (50 - int(d.percent / 2))
            print(colored(f"  Jarvis: 💿 Disk {drive}", "cyan"))
            print(f"         [{bar}] {d.percent}%")
            print(f"         Used: {fmt_size(d.used)}  ·  Free: {fmt_size(d.free)}  ·  Total: {fmt_size(d.total)}")
        except Exception as e:
            jprint(f"Error: {e}", "red")

    # ── Network Info ───────────────────────────────────────────────
    def network_info(self):
        if not HAS_PSUTIL:
            jprint("Install psutil.", "yellow"); return
        print(colored("  Jarvis: 🌐 Network", "cyan"))
        for iface, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET:
                    print(f"         {iface}: {a.address}  (netmask {a.netmask})")
        s = psutil.net_io_counters()
        print(f"         📤 Sent: {fmt_size(s.bytes_sent)}  ·  📥 Recv: {fmt_size(s.bytes_recv)}")

    # ── Speed Test ─────────────────────────────────────────────────
    def speed_test(self):
        if not HAS_SPEEDTEST:
            jprint("Install speedtest-cli.", "yellow"); return
        jprint("🏃 Running speed test…")
        try:
            s = st_mod.Speedtest()
            s.get_best_server()
            dl = s.download() / 1e6
            ul = s.upload() / 1e6
            ping = s.results.ping
            print(colored("  Jarvis: Speed Test Results", "cyan"))
            print(f"         📥 Download : {dl:.2f} Mbps")
            print(f"         📤 Upload   : {ul:.2f} Mbps")
            print(f"         🏓 Ping     : {ping:.1f} ms")
            print(f"         🌐 Server   : {s.results.server['sponsor']} ({s.results.server['name']})")
        except Exception as e:
            jprint(f"Speed test failed: {e}", "red")

    # ── Hash ───────────────────────────────────────────────────────
    def hash_text(self, text, algo="sha256"):
        try:
            h = hashlib.new(algo)
            h.update(text.encode())
            jprint(f"🔐 {algo.upper()}: {h.hexdigest()}")
        except Exception:
            jprint("Algo not found. Try: md5, sha1, sha256, sha512", "red")

    # ── Base64 ─────────────────────────────────────────────────────
    def b64enc(self, text):
        jprint(f"📦 {base64.b64encode(text.encode()).decode()}")

    def b64dec(self, text):
        try:
            jprint(f"📦 {base64.b64decode(text).decode()}")
        except Exception:
            jprint("Invalid Base64.", "red")

    # ── Hex → RGB ──────────────────────────────────────────────────
    def hex_to_rgb(self, h):
        h = h.lstrip("#")
        try:
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
            jprint(f"🎨 #{h.upper()} → RGB({r}, {g}, {b})")
        except Exception:
            jprint("Use format: #FF5733 or FF5733", "red")

    # ── Coin / Dice ────────────────────────────────────────────────
    def flip_coin(self):
        jprint_say(f"🪙  {random.choice(['Heads', 'Tails'])}!")

    def roll_dice(self, sides=6, count=1):
        rolls = [random.randint(1, sides) for _ in range(count)]
        jprint_say(f"🎲 {count}d{sides}: {rolls}  (Total: {sum(rolls)})")

    # ── 8-Ball ─────────────────────────────────────────────────────
    def magic_8ball(self):
        answers = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes, definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now.", "Cannot predict now.",
            "Concentrate and ask again.", "Don't count on it.",
            "My reply is no.", "My sources say no.", "Outlook not so good.",
            "Very doubtful.",
        ]
        jprint_say(f"🔮 {random.choice(answers)}")

    # ── ASCII Art ──────────────────────────────────────────────────
    def ascii_art(self, text):
        try:
            r = requests.get(f"http://artii.herokuapp.com/make?text={quote_plus(text)}", timeout=8)
            print(colored(r.text, "cyan"))
        except Exception:
            jprint("ASCII art service unavailable.", "red")

    # ── Run Shell Command ──────────────────────────────────────────
    def run_cmd(self, cmd):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            out = (r.stdout or r.stderr).strip()
            if out:
                lines = out.split("\n")
                print(colored("  Jarvis: Command Output", "cyan"))
                for ln in lines[:30]:
                    print(f"         {ln}")
                if len(lines) > 30:
                    print(f"         … ({len(lines) - 30} more)")
            else:
                jprint("Done (no output).")
        except subprocess.TimeoutExpired:
            jprint("Timed out.", "red")
        except Exception as e:
            jprint(f"Error: {e}", "red")

    # ── Voice Input ────────────────────────────────────────────────
    def listen(self):
        if not HAS_SR:
            jprint("Install SpeechRecognition + PyAudio.", "yellow"); return None
        rec = sr.Recognizer()
        with sr.Microphone() as src:
            print(colored("  🎤 Listening…", "magenta"))
            rec.adjust_for_ambient_noise(src, duration=0.5)
            try:
                audio = rec.listen(src, timeout=6, phrase_time_limit=12)
                text = rec.recognize_google(audio)
                print(f"  You (voice): {text}")
                return text.strip()
            except sr.WaitTimeoutError:
                jprint("No speech detected.", "yellow")
            except sr.UnknownValueError:
                jprint("Couldn't understand.", "yellow")
            except Exception as e:
                jprint(f"Mic error: {e}", "red")
        return None

    # ── Alias Manager ──────────────────────────────────────────────
    def add_alias(self, name, path):
        self.aliases[name.lower()] = path
        self._persist_aliases()
        jprint_say(f"🔗 Alias '{name}' → {path}")

    def list_aliases(self):
        all_a = {**WEBSITE_ALIASES, **{k: v for k, v in APPS.items()}, **self.aliases}
        print(colored("  Jarvis: 🔗 Aliases", "cyan"))
        for k, v in all_a.items():
            print(f"         {k:<18} → {v}")

    # ── Ping / Connectivity ────────────────────────────────────────
    def ping(self, host="google.com"):
        try:
            t0 = time.time()
            requests.get(f"https://{host}", timeout=5)
            ms = (time.time() - t0) * 1000
            jprint(f"📡 {host}: {ms:.0f} ms")
        except Exception:
            jprint(f"📡 {host}: Unreachable", "red")

    # ── Color Code Info ────────────────────────────────────────────
    def countdown_to(self, target_str):
        """Countdown to a date/time. Format: '2025-12-25' or '2025-12-25 18:00'"""
        try:
            target = datetime.fromisoformat(target_str)
            delta = target - datetime.now()
            if delta.total_seconds() < 0:
                jprint("That date has already passed!", "yellow"); return
            d, h, m, s = (delta.days,
                          delta.seconds // 3600,
                          delta.seconds % 3600 // 60,
                          delta.seconds % 60)
            jprint(f"⏳ {d}d {h}h {m}m {s}s until {target.strftime('%A, %B %d, %Y %I:%M %p')}")
        except Exception:
            jprint("Format: 'countdown 2025-12-25' or 'countdown 2025-12-25 18:00'", "yellow")

    # ── Stock (free, no key) ───────────────────────────────────────
    def stock_price(self, symbol):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            r = requests.get(url, timeout=10,
                             headers={"User-Agent": "Mozilla/5.0"})
            data = r.json()
            result = data["chart"]["result"][0]
            meta = result["meta"]
            price = meta["regularMarketPrice"]
            prev = meta["previousClose"]
            change = price - prev
            pct = change / prev * 100
            arrow = "📈" if change >= 0 else "📉"
            jprint(f"{arrow} {symbol.upper()}: ${price:.2f}  ({change:+.2f} / {pct:+.2f}%)")
        except Exception:
            jprint(f"Couldn't fetch {symbol}.", "red")

    # ── Clipboard History (simple) ─────────────────────────────────
    def clipboard_history(self):
        if not HAS_PYPERCLIP:
            jprint("Install pyperclip.", "yellow"); return
        jprint("Watching clipboard for 30s. Copy something… (Ctrl+C to stop)")
        seen = set()
        end = time.time() + 30
        try:
            while time.time() < end:
                cur = pyperclip.paste()
                if cur and cur not in seen:
                    seen.add(cur)
                    print(f"         📋 {cur[:120]}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        jprint(f"Captured {len(seen)} clip(s).")

    # ══════════════════════════════════════════════════════════════
    #  COMMAND ROUTER
    # ══════════════════════════════════════════════════════════════
    def process(self, raw):
        p = raw.strip()
        if not p:
            return True
        lo = p.lower()

        # ── Exit ───────────────────────────────────────────────
        if lo in ("exit", "quit", "bye", "goodbye"):
            self._persist_history()
            jprint_say("Goodbye, Sir! Until next time. 👋")
            return False

        # ── Help ───────────────────────────────────────────────
        if lo in ("help", "commands", "?", "menu"):
            self.show_help()
            return True

        # ── Voice toggle ───────────────────────────────────────
        if lo == "voice on":
            self.tts_enabled = True; jprint_say("🔊 Voice on."); return True
        if lo == "voice off":
            self.tts_enabled = False; jprint("🔇 Voice off."); return True

        # ── Voice input ────────────────────────────────────────
        if lo in ("listen", "mic", "voice input"):
            text = self.listen()
            if text:
                return self.process(text)
            return True

        # ── Open app ───────────────────────────────────────────
        if lo.startswith("open "):
            self.open_app(lo[5:]); return True

        # ── Open website ───────────────────────────────────────
        if lo.startswith("go to ") or lo.startswith("goto "):
            self.open_website(re.sub(r"^go ?to\s+", "", lo)); return True

        # ── Search web ─────────────────────────────────────────
        if lo.startswith("search "):
            self.search_web(p[7:]); return True

        # ── Wikipedia ──────────────────────────────────────────
        if lo.startswith("wiki "):
            self.search_wiki(p[5:]); return True

        # ── Dictionary ─────────────────────────────────────────
        if lo.startswith("define "):
            self.define(p[7:]); return True

        # ── Time / Date ────────────────────────────────────────
        if lo in ("time", "what time is it", "what's the time", "clock"):
            self.get_time(); return True
        if lo in ("date", "what date is it", "what's the date", "today"):
            self.get_date(); return True
        if lo in ("datetime", "now", "date and time"):
            self.get_datetime(); return True
        if lo == "uptime":
            self.uptime(); return True

        # ── Weather ────────────────────────────────────────────
        if lo.startswith("weather"):
            self.get_weather(lo.replace("weather", "").strip()); return True

        # ── System info ────────────────────────────────────────
        if lo in ("system", "sysinfo", "sys"):
            self.system_info(); return True

        # ── Processes ──────────────────────────────────────────
        if lo.startswith("processes") or lo.startswith("ps "):
            filt = re.sub(r"^(processes|ps)\s*", "", lo)
            self.list_processes(filt); return True
        if lo.startswith("kill "):
            self.kill_process(lo[5:]); return True

        # ── Battery ────────────────────────────────────────────
        if lo in ("battery", "bat"):
            self.battery_status(); return True

        # ── Disk ───────────────────────────────────────────────
        if lo.startswith("disk"):
            drv = lo.replace("disk", "").strip()
            self.disk_usage(drv if drv else None); return True

        # ── Network / IP ───────────────────────────────────────
        if lo in ("network", "net"):
            self.network_info(); return True
        if lo in ("ip", "my ip", "ip address"):
            self.get_ip(); return True
        if lo in ("speedtest", "speed test"):
            self.speed_test(); return True
        if lo.startswith("ping "):
            self.ping(lo[5:]); return True

        # ── Notes ──────────────────────────────────────────────
        if lo.startswith("note "):
            self.add_note(p[5:]); return True
        if lo in ("notes", "show notes"):
            self.list_notes(); return True
        if lo.startswith("search notes "):
            self.search_notes(lo[13:]); return True
        if lo.startswith("delete note "):
            self.delete_note(lo[12:]); return True
        if lo in ("clear notes",):
            self.clear_notes(); return True

        # ── Todos ──────────────────────────────────────────────
        if lo.startswith("todo "):
            self.add_todo(p[5:]); return True
        if lo in ("todos", "show todos"):
            self.list_todos(); return True
        if lo.startswith("done "):
            self.complete_todo(lo[5:]); return True
        if lo.startswith("delete todo "):
            self.delete_todo(lo[12:]); return True
        if lo == "clear todos":
            self.clear_todos(); return True

        # ── Reminders ──────────────────────────────────────────
        if lo.startswith("remind "):
            parts = lo[7:].split(None, 1)
            try:
                mins = float(parts[0])
                msg = parts[1] if len(parts) > 1 else "Reminder!"
                self.set_reminder(msg, mins)
            except (ValueError, IndexError):
                jprint("Usage: remind <minutes> <message>", "yellow")
            return True

        # ── Timer ──────────────────────────────────────────────
        if lo.startswith("timer "):
            parts = lo[6:].split(None, 1)
            try:
                secs = float(parts[0])
                label = parts[1] if len(parts) > 1 else "Timer"
                self.set_timer(int(secs), label)
            except (ValueError, IndexError):
                jprint("Usage: timer <seconds> [label]", "yellow")
            return True

        # ── Countdown ──────────────────────────────────────────
        if lo.startswith("countdown "):
            self.countdown_to(p[10:]); return True

        # ── Calculator ─────────────────────────────────────────
        if lo.startswith("calc ") or lo.startswith("math "):
            self.calculate(re.sub(r"^(calc|math)\s+", "", lo)); return True

        # ── Convert ────────────────────────────────────────────
        if lo.startswith("convert "):
            self.convert_unit(lo[8:]); return True

        # ── Screenshot ─────────────────────────────────────────
        if lo in ("screenshot", "ss", "capture"):
            self.take_screenshot(); return True

        # ── Clipboard ──────────────────────────────────────────
        if lo in ("clipboard", "paste"):
            self.read_clipboard(); return True
        if lo.startswith("copy "):
            self.copy_to_clipboard(p[5:]); return True
        if lo == "cliphist":
            self.clipboard_history(); return True

        # ── Password ───────────────────────────────────────────
        if lo.startswith("password"):
            parts = lo.split()
            length = 20
            if len(parts) > 1:
                try:
                    length = int(parts[1])
                except ValueError:
                    pass
            self.gen_password(length); return True

        # ── QR ─────────────────────────────────────────────────
        if lo.startswith("qr "):
            self.gen_qr(p[3:]); return True

        # ── Hash ───────────────────────────────────────────────
        if lo.startswith("hash "):
            parts = lo[5:].rsplit(None, 1)
            if len(parts) == 2 and parts[1] in ("md5", "sha1", "sha256", "sha512"):
                self.hash_text(parts[0], parts[1])
            else:
                self.hash_text(p[5:])
            return True

        # ── Base64 ─────────────────────────────────────────────
        if lo.startswith("b64enc "):
            self.b64enc(p[7:]); return True
        if lo.startswith("b64dec "):
            self.b64dec(p[7:]); return True

        # ── Hex ────────────────────────────────────────────────
        if lo.startswith("hex "):
            self.hex_to_rgb(lo[4:]); return True

        # ── Joke ───────────────────────────────────────────────
        if lo in ("joke", "tell me a joke", "funny"):
            self.tell_joke(); return True

        # ── Coin / Dice ────────────────────────────────────────
        if lo in ("coin", "flip", "flip coin"):
            self.flip_coin(); return True
        if lo.startswith("dice") or lo.startswith("roll"):
            parts = re.sub(r"^(dice|roll)\s*", "", lo).split()
            sides, count = 6, 1
            try:
                if len(parts) >= 1: sides = int(parts[0])
                if len(parts) >= 2: count = int(parts[1])
            except ValueError:
                pass
            self.roll_dice(sides, count); return True

        # ── 8-Ball ─────────────────────────────────────────────
        if lo in ("8ball", "magic 8ball", "fortune"):
            self.magic_8ball(); return True

        # ── ASCII art ──────────────────────────────────────────
        if lo.startswith("ascii "):
            self.ascii_art(p[6:]); return True

        # ── Stock ──────────────────────────────────────────────
        if lo.startswith("stock "):
            self.stock_price(lo[6:]); return True

        # ── File ops ───────────────────────────────────────────
        if lo.startswith("ls"):
            self.list_dir(re.sub(r"^ls\s*", "", lo) or "."); return True
        if lo.startswith("read "):
            self.read_file(p[5:]); return True
        if lo.startswith("create "):
            parts = p[7:].split(None, 1)
            self.create_file(parts[0], parts[1] if len(parts) > 1 else ""); return True
        if lo.startswith("delete file "):
            self.delete_file(p[12:]); return True
        if lo.startswith("download "):
            self.download_file(p[9:]); return True

        # ── System controls ────────────────────────────────────
        if lo in ("shutdown", "restart", "lock", "sleep", "hibernate", "log off", "cancel shutdown"):
            self.system_control(lo); return True

        # ── Volume ─────────────────────────────────────────────
        if lo.startswith("volume "):
            self.set_volume(lo[7:]); return True
        if lo == "mute":
            self.mute_toggle(); return True

                # ── Run command ────────────────────────────────────────
        if lo.startswith("run "):
            self.run_cmd(p[4:]); return True

        # ── Alias ──────────────────────────────────────────────
        if lo.startswith("alias "):
            match = re.match(r"alias\s+(\w+)\s*=\s*(.+)", p, re.IGNORECASE)
            if match:
                self.add_alias(match.group(1), match.group(2))
            else:
                jprint("Usage: alias <name> = <path_or_url>", "yellow")
            return True
        if lo in ("aliases", "list aliases"):
            self.list_aliases(); return True

        # ── History ────────────────────────────────────────────
        if lo in ("history", "chat history"):
            if not self.conversation_history:
                jprint("No chat history yet."); return True
            print(colored("  Jarvis: 💬 Chat History", "cyan"))
            for msg in self.conversation_history[-20:]:
                role = "You" if msg["role"] == "user" else "Jarvis"
                color = "green" if msg["role"] == "user" else "cyan"
                print(colored(f"         {role}: {msg['content'][:120]}", color))
            return True
        if lo in ("clear history", "reset history"):
            self.conversation_history.clear()
            self._persist_history()
            jprint_say("🗑 Chat history cleared."); return True

        # ── Clear screen ───────────────────────────────────────
        if lo in ("clear", "cls"):
            os.system("cls" if IS_WINDOWS else "clear")
            return True

        # ── Repeat last ────────────────────────────────────────
        if lo in ("repeat", "again", "say again"):
            if self.conversation_history:
                last = [m for m in self.conversation_history if m["role"] == "assistant"]
                if last:
                    jprint_say(last[-1]["content"])
            else:
                jprint("Nothing to repeat.", "yellow")
            return True

        # ── About ──────────────────────────────────────────────
        if lo in ("about", "version", "info"):
            print(colored("  Jarvis: ℹ️  About", "cyan"))
            print("         JARVIS Advanced AI Assistant v2.0")
            print("         Model  : Gemma2:2b via Ollama")
            print(f"         Python : {platform.python_version()}")
            print(f"         OS     : {platform.system()} {platform.release()}")
            print(f"         Notes  : {len(self.notes)}")
            print(f"         Todos  : {len(self.todos)}")
            print(f"         History: {len(self.conversation_history)} messages")
            print(f"         Voice  : {'On' if self.tts_enabled else 'Off'}")
            return True

        # ── Mood / Status ──────────────────────────────────────
        if lo in ("mood", "how are you", "how do you feel"):
            moods = [
                "Running at peak efficiency, Sir. Coffee would be nice though.",
                "All systems nominal. A bit bored, honestly.",
                "Feeling electric today, Sir. ⚡",
                "I've processed 42 billion thoughts since you asked. Fine, thanks.",
                "As magnificent as a perfectly optimized algorithm.",
                "Ready to conquer the digital world, Sir.",
            ]
            jprint_say(random.choice(moods))
            return True

        # ── Thank ──────────────────────────────────────────────
        if lo in ("thanks", "thank you", "thx", "ty"):
            responses = [
                "At your service, Sir.",
                "Always a pleasure.",
                "That's what I'm here for.",
                "Don't mention it, Sir.",
            ]
            jprint_say(random.choice(responses))
            return True

        # ── Good morning / night ───────────────────────────────
        if lo in ("good morning", "morning"):
            h = datetime.now().hour
            name = platform.node()
            jprint_say(f"Good morning, Sir! ☀️  It's {datetime.now().strftime('%I:%M %p')}. Ready to be productive?")
            return True
        if lo in ("good night", "goodnight"):
            jprint_say(f"Good night, Sir! 🌙 Sleep well. I'll be here when you return.")
            return True

        # ── Matrix rain (Easter egg) ───────────────────────────
        if lo in ("matrix", "hackerman"):
            cols = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
            chars = "01アイウエオカキクケコ"
            try:
                for _ in range(80):
                    line = "".join(random.choice(chars) for _ in range(cols))
                    print(colored(line, "green"))
                    time.sleep(0.03)
            except KeyboardInterrupt:
                pass
            jprint("Wake up, Sir… The Matrix has you.")
            return True

        # ── Quote ──────────────────────────────────────────────
        if lo in ("quote", "inspire", "inspiration", "motivation"):
            quotes = [
                ("Tony Stark", "Sometimes you gotta run before you can walk."),
                ("Tony Stark", "I am Iron Man."),
                ("Albert Einstein", "Imagination is more important than knowledge."),
                ("Steve Jobs", "Stay hungry, stay foolish."),
                ("Alan Turing", "We can only see a short distance ahead, but we can see plenty there that needs to be done."),
                ("Linus Torvalds", "Talk is cheap. Show me the code."),
                ("Grace Hopper", "The most dangerous phrase in the language is: 'We've always done it this way.'"),
                ("Nikola Tesla", "The present is theirs; the future, for which I really worked, is mine."),
                ("Arthur C. Clarke", "Any sufficiently advanced technology is indistinguishable from magic."),
                ("Edsger Dijkstra", "Simplicity is prerequisite for reliability."),
                ("Margaret Hamilton", "There was no second chance. We all knew that."),
                ("Katherine Johnson", "Girls are capable of doing everything men are capable of doing."),
            ]
            author, quote = random.choice(quotes)
            print(colored(f"  Jarvis: 💬 \"{quote}\"", "cyan"))
            print(colored(f"          — {author}", "dim"))
            return True

        # ── Emoji dice / random choice ─────────────────────────
        if lo.startswith("choose "):
            opts = [o.strip() for o in p[7:].split(",") if o.strip()]
            if len(opts) >= 2:
                jprint_say(f"🤔 I choose: {random.choice(opts)}")
            else:
                jprint("Give me comma-separated options. e.g. choose pizza, sushi, tacos", "yellow")
            return True

        # ── Random number ──────────────────────────────────────
        if lo.startswith("random "):
            match = re.match(r"random\s+(\d+)\s*-\s*(\d+)", lo)
            if match:
                a, b = int(match.group(1)), int(match.group(2))
                jprint_say(f"🎲 Random: {random.randint(a, b)}")
            else:
                jprint("Usage: random 1-100", "yellow")
            return True

        # ── Word count / char count ────────────────────────────
        if lo.startswith("wc "):
            text = p[3:]
            words = len(text.split())
            chars = len(text)
            jprint(f"📊 {words} words · {chars} characters")
            return True

        # ── Reverse text ───────────────────────────────────────
        if lo.startswith("reverse "):
            jprint(f"🔄 {p[8:][::-1]}")
            return True

        # ── Uppercase / Lowercase ──────────────────────────────
        if lo.startswith("upper "):
            jprint(f"🔤 {p[6:].upper()}"); return True
        if lo.startswith("lower "):
            jprint(f"🔤 {p[6:].lower()}"); return True

        # ── Title case ─────────────────────────────────────────
        if lo.startswith("title "):
            jprint(f"🔤 {p[6:].title()}"); return True

        # ── Length ─────────────────────────────────────────────
        if lo.startswith("length "):
            jprint(f"📏 {len(p[7:])} characters"); return True

        # ── Sort lines ─────────────────────────────────────────
        if lo.startswith("sort "):
            lines = p[5:].split(",")
            sorted_lines = sorted([l.strip() for l in lines])
            jprint(f"📋 {', '.join(sorted_lines)}")
            return True

        # ── UUID ───────────────────────────────────────────────
        if lo in ("uuid", "guid"):
            import uuid as _uuid
            jprint(f"🆔 {_uuid.uuid4()}")
            return True

        # ── Timestamp ──────────────────────────────────────────
        if lo in ("timestamp", "epoch", "unix time"):
            jprint(f"🕐 {int(time.time())}")
            return True

        # ── Color preview ──────────────────────────────────────
        if lo.startswith("color "):
            c = lo[6:].strip()
            # Try to show a colored block
            try:
                r, g, b = None, None, None
                if c.startswith("#"):
                    hex_val = c.lstrip("#")
                    r, g, b = (int(hex_val[i:i+2], 16) for i in (0, 2, 4))
                elif c.startswith("rgb"):
                    m = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", c)
                    if m:
                        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if r is not None:
                    block = "██" * 15
                    print(f"\033[38;2;{r};{g};{b}m  {block}  {c}  RGB({r},{g},{b}){RESET}")
                else:
                    jprint("Format: color #FF5733 or color rgb(255,87,51)", "yellow")
            except Exception:
                jprint("Format: color #FF5733 or color rgb(255,87,51)", "yellow")
            return True

        # ── BMI Calculator ─────────────────────────────────────
        if lo.startswith("bmi "):
            try:
                parts = lo[4:].split()
                weight, height = float(parts[0]), float(parts[1])
                bmi = weight / (height ** 2)
                category = ("Underweight" if bmi < 18.5 else
                           "Normal" if bmi < 25 else
                           "Overweight" if bmi < 30 else "Obese")
                jprint(f"💪 BMI: {bmi:.1f} ({category})")
            except (ValueError, IndexError):
                jprint("Usage: bmi <weight_kg> <height_m>  e.g. bmi 70 1.75", "yellow")
            return True

        # ── Tip calculator ─────────────────────────────────────
        if lo.startswith("tip "):
            try:
                parts = lo[4:].split()
                amount = float(parts[0])
                pct = float(parts[1]) if len(parts) > 1 else 15
                tip = amount * pct / 100
                jprint(f"💰 Tip: ${tip:.2f} ({pct}%) · Total: ${amount + tip:.2f}")
            except (ValueError, IndexError):
                jprint("Usage: tip <amount> [percentage]  e.g. tip 50 18", "yellow")
            return True

        # ── Percentage calculator ──────────────────────────────
        if lo.startswith("percent "):
            try:
                parts = lo[8:].split()
                if len(parts) == 2:
                    a, b = float(parts[0]), float(parts[1])
                    jprint(f"📊 {a} is {a/b*100:.2f}% of {b}")
                elif len(parts) == 3 and parts[1] == "of":
                    a, b = float(parts[0]), float(parts[2])
                    jprint(f"📊 {a} is {a/b*100:.2f}% of {b}")
                else:
                    jprint("Usage: percent 25 200  or  percent 25 of 200", "yellow")
            except (ValueError, IndexError, ZeroDivisionError):
                jprint("Usage: percent 25 200", "yellow")
            return True

        # ── Day of week ────────────────────────────────────────
        if lo.startswith("dayof "):
            try:
                dt = datetime.fromisoformat(lo[6:].strip())
                jprint(f"📅 {dt.strftime('%A, %B %d, %Y')}")
            except Exception:
                jprint("Format: dayof 2025-12-25", "yellow")
            return True

        # ── Days until ─────────────────────────────────────────
        if lo.startswith("days until "):
            try:
                target = datetime.fromisoformat(lo[11:].strip())
                delta = (target - datetime.now()).days
                if delta < 0:
                    jprint(f"That was {abs(delta)} days ago!")
                else:
                    jprint(f"📅 {delta} days until {target.strftime('%B %d, %Y')}")
            except Exception:
                jprint("Format: days until 2025-12-25", "yellow")
            return True

        # ── Days since ─────────────────────────────────────────
        if lo.startswith("days since "):
            try:
                target = datetime.fromisoformat(lo[11:].strip())
                delta = (datetime.now() - target).days
                jprint(f"📅 {delta} days since {target.strftime('%B %d, %Y')}")
            except Exception:
                jprint("Format: days since 2025-01-01", "yellow")
            return True

        # ── Stopwatch ──────────────────────────────────────────
        if lo in ("stopwatch", "stop watch"):
            jprint("⏱ Stopwatch started. Press Enter to stop.")
            start = time.time()
            try:
                input()
            except KeyboardInterrupt:
                pass
            elapsed = time.time() - start
            m, s = divmod(int(elapsed), 60)
            jprint(f"⏱ Stopped at {m:02d}:{s:02d}")
            return True

        # ── Pomodoro ───────────────────────────────────────────
        if lo.startswith("pomodoro"):
            parts = lo.split()
            work = 25
            rest = 5
            try:
                if len(parts) >= 2: work = int(parts[1])
                if len(parts) >= 3: rest = int(parts[2])
            except ValueError:
                pass

            def _pom(w, r):
                jprint_say(f"🍅 Work for {w} minutes!")
                time.sleep(w * 60)
                jprint_say(f"☕ Break time! {r} minutes.")
                time.sleep(r * 60)
                jprint_say("🍅 Pomodoro complete!")

            threading.Thread(target=_pom, args=(work, rest), daemon=True).start()
            jprint(f"🍅 Pomodoro: {work}min work / {rest}min break (running in background)")
            return True

        # ── Currency (free, no key, approx) ────────────────────
        if lo.startswith("currency ") or lo.startswith("fx "):
            try:
                parts = re.sub(r"^(currency|fx)\s+", "", lo).split()
                if len(parts) == 3:
                    amount = float(parts[0])
                    frm = parts[1].upper()
                    to = parts[2].upper()
                    url = f"https://open.er-api.com/v6/latest/{frm}"
                    data = requests.get(url, timeout=10).json()
                    rate = data["rates"].get(to)
                    if rate:
                        result = amount * rate
                        jprint(f"💱 {amount} {frm} = {result:.4f} {to} (rate: {rate:.4f})")
                    else:
                        jprint(f"Currency code '{to}' not found.", "yellow")
                else:
                    jprint("Usage: currency 100 USD EUR", "yellow")
            except Exception as e:
                jprint(f"Currency error: {e}", "red")
            return True

        # ── News headlines (free) ──────────────────────────────
        if lo in ("news", "headlines", "top news"):
            try:
                r = requests.get(
                    "https://hacker-news.firebaseio.com/v0/topstories.json?limitToFirst=10&orderBy=\"$key\"",
                    timeout=10
                )
                ids = r.json()[:10] if isinstance(r.json(), list) else list(r.json().values())[:10]
                # flatten if needed
                if isinstance(ids[0], list):
                    ids = ids[0] if ids else []
                print(colored("  Jarvis: 📰 Top Stories (Hacker News)", "cyan"))
                for i, item_id in enumerate(ids[:10], 1):
                    try:
                        story = requests.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                            timeout=5
                        ).json()
                        if story:
                            title = story.get("title", "No title")
                            url = story.get("url", "")
                            score = story.get("score", 0)
                            print(f"         {colored(f'{i}.', 'yellow')} [{score}⬆] {title}")
                            if url:
                                print(f"            {colored(url, 'dim')}")
                    except Exception:
                        pass
            except Exception as e:
                jprint(f"News error: {e}", "red")
            return True

        # ── IP Lookup ──────────────────────────────────────────
        if lo.startswith("iplookup "):
            try:
                ip = lo[9:].strip()
                data = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
                if data.get("status") == "success":
                    print(colored(f"  Jarvis: 🌐 IP Lookup: {ip}", "cyan"))
                    print(f"         Country  : {data.get('country', 'N/A')}")
                    print(f"         Region   : {data.get('regionName', 'N/A')}")
                    print(f"         City     : {data.get('city', 'N/A')}")
                    print(f"         ISP      : {data.get('isp', 'N/A')}")
                    print(f"         Lat/Lon  : {data.get('lat')}, {data.get('lon')}")
                    print(f"         Timezone : {data.get('timezone', 'N/A')}")
                else:
                    jprint(f"Could not lookup {ip}.", "yellow")
            except Exception as e:
                jprint(f"IP lookup error: {e}", "red")
            return True

        # ── Geo IP (self) ──────────────────────────────────────
        if lo in ("where am i", "geo", "location"):
            try:
                data = requests.get("https://ipapi.co/json/", timeout=5).json()
                print(colored("  Jarvis: 📍 Your Location", "cyan"))
                print(f"         {data.get('city', '?')}, {data.get('region', '?')}, {data.get('country_name', '?')}")
                print(f"         Lat/Lon: {data.get('latitude')}, {data.get('longitude')}")
                print(f"         ISP: {data.get('org', '?')}")
                print(f"         Timezone: {data.get('timezone', '?')}")
            except Exception:
                jprint("Geo lookup failed.", "red")
            return True

        # ── Env variable ───────────────────────────────────────
        if lo.startswith("env "):
            key = lo[4:].strip().upper()
            val = os.environ.get(key)
            if val:
                jprint(f"🔑 {key} = {val}")
            else:
                jprint(f"{key} not set.", "yellow")
            return True

        # ── Whoami ─────────────────────────────────────────────
        if lo in ("whoami", "who am i"):
            jprint(f"👤 {os.getenv('USERNAME', os.getenv('USER', 'Unknown'))} @ {platform.node()}")
            return True

        # ── Disk cleanup info ──────────────────────────────────
        if lo == "disk cleanup":
            if not HAS_PSUTIL:
                jprint("Install psutil.", "yellow"); return True
            print(colored("  Jarvis: 🧹 Disk Summary", "cyan"))
            for part in psutil.disk_partitions():
                try:
                    u = psutil.disk_usage(part.mountpoint)
                    bar = "█" * int(u.percent / 2) + "░" * (50 - int(u.percent / 2))
                    print(f"         {part.mountpoint} [{bar}] {u.percent}%  ({fmt_size(u.free)} free)")
                except Exception:
                    pass
            return True

        # ── CPU monitor (live 5 sec) ───────────────────────────
        if lo in ("cpu", "cpu monitor"):
            if not HAS_PSUTIL:
                jprint("Install psutil.", "yellow"); return True
            jprint("📊 CPU monitor (5 seconds)…")
            try:
                for _ in range(5):
                    pct = psutil.cpu_percent(interval=1)
                    bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
                    print(f"         [{bar}] {pct}%", flush=True)
            except KeyboardInterrupt:
                pass
            jprint("Done.")
            return True

        # ── Memory monitor ─────────────────────────────────────
        if lo in ("ram", "memory", "mem"):
            if not HAS_PSUTIL:
                jprint("Install psutil.", "yellow"); return True
            m = psutil.virtual_memory()
            bar = "█" * int(m.percent / 2) + "░" * (50 - int(m.percent / 2))
            print(colored("  Jarvis: 🧠 Memory", "cyan"))
            print(f"         [{bar}] {m.percent}%")
            print(f"         Used: {fmt_size(m.used)} / {fmt_size(m.total)}")
            print(f"         Available: {fmt_size(m.available)}")
            if m.percent > 85:
                jprint("⚠️ Memory usage is high!", "yellow")
            return True

        # ── Top talkers (network) ──────────────────────────────
        if lo == "netstat":
            if not HAS_PSUTIL:
                jprint("Install psutil.", "yellow"); return True
            conns = psutil.net_connections(kind="inet")
            print(colored("  Jarvis: 🌐 Active Connections", "cyan"))
            print(f"         {'PID':<8}{'Local':<25}{'Remote':<30}{'Status'}")
            print(f"         {'─' * 70}")
            for c in conns[:25]:
                pid = c.pid or "-"
                local = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
                remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
                print(f"         {pid:<8}{local:<25}{remote:<30}{c.status}")
            print(f"         Total: {len(conns)} connections")
            return True

        # ── Wifi passwords (Windows) ───────────────────────────
        if lo in ("wifi", "wifi passwords", "wifi keys"):
            if not IS_WINDOWS:
                jprint("Windows-only.", "yellow"); return True
            try:
                result = subprocess.run(
                    ["netsh", "wlan", "show", "profiles"],
                    capture_output=True, text=True, timeout=10
                )
                profiles = re.findall(r":\s*(.+)", result.stdout)
                print(colored("  Jarvis: 📶 WiFi Profiles", "cyan"))
                for prof in profiles[:20]:
                    prof = prof.strip()
                    key_result = subprocess.run(
                        ["netsh", "wlan", "show", "profile", f"name={prof}", "key=clear"],
                        capture_output=True, text=True, timeout=5
                    )
                    match = re.search(r"Key Content\s*:\s*(.+)", key_result.stdout)
                    key = match.group(1).strip() if match else "(hidden/open)"
                    print(f"         📶 {prof}: {key}")
            except Exception as e:
                jprint(f"WiFi error: {e}", "red")
            return True

        # ── Brightness (Windows) ───────────────────────────────
        if lo.startswith("brightness "):
            if not IS_WINDOWS:
                jprint("Windows-only.", "yellow"); return True
            try:
                lvl = max(0, min(100, int(lo[11:])))
                ps_cmd = (
                    f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)."
                    f"WmiSetBrightness(1,{lvl})"
                )
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=5)
                jprint_say(f"☀ Brightness set to {lvl}%")
            except Exception:
                jprint("Brightness error.", "red")
            return True

        # ── Screen resolution ──────────────────────────────────
        if lo in ("resolution", "screen"):
            if HAS_PIL:
                try:
                    from PIL import ImageGrab
                    img = ImageGrab.grab()
                    jprint(f"🖥 Resolution: {img.size[0]}x{img.size[1]}")
                except Exception:
                    jprint("Could not detect.", "yellow")
            else:
                jprint("Install Pillow.", "yellow")
            return True

        # ── Binary encode/decode ───────────────────────────────
        if lo.startswith("binenc "):
            text = p[7:]
            binary = " ".join(format(ord(c), '08b') for c in text)
            jprint(f"🔢 {binary}")
            return True
        if lo.startswith("bindec "):
            try:
                text = "".join(chr(int(b, 2)) for b in lo[7:].split())
                jprint(f"🔢 {text}")
            except Exception:
                jprint("Invalid binary. Space-separated 8-bit groups.", "red")
            return True

        # ── Morse encode ───────────────────────────────────────
        if lo.startswith("morse "):
            MORSE = {
                'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.',
                'H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.',
                'O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-',
                'V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----',
                '1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....',
                '7':'--...','8':'---..','9':'----.', ' ':' / '
            }
            morse = " ".join(MORSE.get(c.upper(), '?') for c in p[6:])
            jprint(f"📡 {morse}")
            return True

        # ── ROT13 ──────────────────────────────────────────────
        if lo.startswith("rot13 "):
            import codecs
            jprint(f"🔐 {codecs.encode(p[6:], 'rot_13')}")
            return True

        # ── Text stats ─────────────────────────────────────────
        if lo.startswith("textstat "):
            text = p[9:]
            words = text.split()
            chars = len(text)
            chars_no_space = len(text.replace(" ", ""))
            sentences = text.count('.') + text.count('!') + text.count('?')
            avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
            print(colored("  Jarvis: 📊 Text Statistics", "cyan"))
            print(f"         Words        : {len(words)}")
            print(f"         Characters   : {chars} ({chars_no_space} without spaces)")
            print(f"         Sentences    : {max(1, sentences)}")
            print(f"         Avg word len : {avg_word_len:.1f}")
            return True

        # ── Colorize text ──────────────────────────────────────
        if lo.startswith("colorize "):
            parts = p[9:].split(None, 1)
            if len(parts) == 2:
                c, t = parts[0].lower(), parts[1]
                print(colored(f"  Jarvis: {t}", c))
            else:
                jprint("Usage: colorize red Hello World", "yellow")
            return True

        # ── Startup commands ───────────────────────────────────
        if lo == "startup":
            print(colored("  Jarvis: 🚀 Startup Commands (run on launch)", "cyan"))
            print("         Add these to a 'jarvis_startup.txt' file, one per line:")
            print("         time")
            print("         weather")
            print("         system")
            return True

        # ── Reload ─────────────────────────────────────────────
        if lo in ("reload", "restart jarvis"):
            jprint_say("🔄 Restarting JARVIS…")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return True

        # ══════════════════════════════════════════════════════
        #  DEFAULT → Ask Gemma
        # ══════════════════════════════════════════════════════
        reply = self.ask_gemma(p)
        jprint_say(reply)
        return True

    # ══════════════════════════════════════════════════════════════
    #  HELP MENU
    # ══════════════════════════════════════════════════════════════
    def show_help(self):
        print(colored("""
  ╔═══════════════════════════════════════════════════════════════════╗
  ║                    JARVIS COMMAND REFERENCE                       ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  📱 APPS & WEB                                                   ║
  ║    open <app>              Open an application                    ║
  ║    goto <site>             Open a website                         ║
  ║    search <query>          Google search                          ║
  ║    wiki <topic>            Wikipedia summary                      ║
  ║    define <word>           Dictionary definition                  ║
  ║    alias <n> = <path>      Add app alias                          ║
  ║    aliases                 List all aliases                        ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  ⏰ TIME & DATE                                                  ║
  ║    time / date / datetime   Current time/date                    ║
  ║    uptime                  System uptime                          ║
  ║    countdown <date>        Countdown to a date                    ║
  ║    days until <date>       Days until a date                      ║
  ║    days since <date>       Days since a date                      ║
  ║    dayof <date>            Day of the week                        ║
  ║    timestamp               Unix timestamp                         ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🌤 WEATHER & LOCATION                                           ║
  ║    weather [city]          Weather report                         ║
  ║    where am i              Your geo location                      ║
  ║    iplookup <ip>           IP geolocation                         ║
  ║    ip                      Your IP addresses                      ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🖥 SYSTEM                                                       ║
  ║    system / sysinfo        Full system report                     ║
  ║    battery                 Battery status                         ║
  ║    cpu                     CPU monitor (5s)                       ║
  ║    ram / memory            RAM usage                              ║
  ║    disk [drive]            Disk usage                             ║
  ║    disk cleanup            All drives summary                     ║
  ║    processes [filter]      List processes                         ║
  ║    kill <name|pid>         Kill a process                         ║
  ║    network / net           Network info                           ║
  ║    netstat                 Active connections                     ║
  ║    speedtest               Internet speed test                    ║
  ║    ping <host>             Ping a host                            ║
  ║    wifi                    Saved WiFi passwords (Win)             ║
  ║    resolution              Screen resolution                      ║
  ║    whoami                  Current user                           ║
  ║    env <VAR>               Environment variable                   ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  📝 NOTES & TODOS                                                ║
  ║    note <text>             Save a note                            ║
  ║    notes                   List notes                             ║
  ║    search notes <query>    Search notes                           ║
  ║    delete note <n>         Delete a note                          ║
  ║    clear notes             Delete all notes                       ║
  ║    todo <text>             Add a todo                             ║
  ║    todos                   List todos                             ║
  ║    done <n>                Mark todo complete                     ║
  ║    delete todo <n>         Delete a todo                          ║
  ║    clear todos             Delete all todos                       ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  ⏱ TIMERS & REMINDERS                                           ║
  ║    remind <min> <msg>      Set a reminder                         ║
  ║    timer <sec> [label]     Start a timer                          ║
  ║    stopwatch               Stopwatch (Enter to stop)              ║
  ║    pomodoro [work] [rest]  Pomodoro timer                         ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🧮 MATH & CONVERT                                               ║
  ║    calc <expr>             Calculator (sin, log, sqrt…)           ║
  ║    convert <val> <u> to <u> Unit conversion                      ║
  ║    bmi <kg> <m>            BMI calculator                         ║
  ║    tip <amount> [%]        Tip calculator                         ║
  ║    percent <a> <b>         Percentage calc                        ║
  ║    currency <amt> <A> <B>  Currency conversion                    ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  📂 FILES                                                        ║
  ║    ls [path]               List directory                         ║
  ║    read <file>             Read a file                            ║
  ║    create <file> [text]    Create a file                          ║
  ║    delete file <file>      Delete a file                          ║
  ║    download <url>          Download a file                        ║
  ║    run <command>           Run shell command                      ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🔧 TOOLS                                                        ║
  ║    password [length]       Generate password                      ║
  ║    qr <data>               Generate QR code                       ║
  ║    hash <text> [algo]      Hash text (md5/sha256…)                ║
  ║    b64enc <text>           Base64 encode                          ║
  ║    b64dec <text>           Base64 decode                          ║
  ║    hex <#hex>              Hex → RGB                              ║
  ║    binenc <text>           Text → Binary                          ║
  ║    bindec <binary>         Binary → Text                          ║
  ║    morse <text>            Text → Morse code                      ║
  ║    rot13 <text>            ROT13 cipher                           ║
  ║    uuid                    Generate UUID                          ║
  ║    screenshot / ss         Take screenshot                        ║
  ║    clipboard / paste       Read clipboard                         ║
  ║    copy <text>             Copy to clipboard                      ║
  ║    cliphist                Clipboard history (30s)                ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🎮 FUN                                                          ║
  ║    joke                    Tell a joke                            ║
  ║    coin / flip             Flip a coin                            ║
  ║    dice [sides] [count]    Roll dice                              ║
  ║    8ball                   Magic 8-Ball                           ║
  ║    quote                   Inspirational quote                    ║
  ║    choose <a, b, c>        Random choice                          ║
  ║    random <min>-<max>      Random number                          ║
  ║    ascii <text>            ASCII art                              ║
  ║    matrix                  Matrix rain 🐇                         ║
  ║    mood                    How's JARVIS?                          ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  📝 TEXT                                                          ║
  ║    wc <text>               Word/char count                        ║
  ║    reverse <text>          Reverse text                           ║
  ║    upper/lower/title <t>   Change case                            ║
  ║    length <text>           String length                          ║
  ║    sort <a, b, c>          Sort items                             ║
  ║    textstat <text>         Text statistics                        ║
  ║    colorize <color> <text> Colored text                           ║
  ║    color <#hex|rgb>        Color preview                          ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  📰 NEWS & FINANCE                                               ║
  ║    news                    Hacker News headlines                  ║
  ║    stock <symbol>          Stock price                            ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🖥 SYSTEM CONTROLS (Windows)                                    ║
  ║    shutdown / restart / lock / sleep / hibernate / log off       ║
  ║    cancel shutdown         Cancel shutdown                        ║
  ║    volume <0-100>          Set volume                             ║
  ║    mute                    Toggle mute                            ║
  ║    brightness <0-100>      Set brightness                         ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  🎤 VOICE & CHAT                                                 ║
  ║    voice on / voice off    Toggle TTS                             ║
  ║    listen / mic            Voice input                            ║
  ║    history                 Chat history                           ║
  ║    clear history           Clear chat history                     ║
  ║    repeat                  Repeat last response                   ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  ⚙️ SETTINGS                                                      ║
  ║    about / version         About JARVIS                           ║
  ║    help / commands         This menu                              ║
  ║    clear / cls             Clear screen                           ║
  ║    reload                  Restart JARVIS                         ║
  ║    exit / quit             Exit                                   ║
  ║    <anything else>         Ask Gemma AI                           ║
  ╚═══════════════════════════════════════════════════════════════════╝
""", "cyan"))


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    banner()
    feature_status()
    print()
    jprint("Hello, Sir! I'm JARVIS, your advanced AI assistant.", "green")
    jprint("Type 'help' to see all commands, or just talk to me.", "dim")
    print()

    jarvis = Jarvis()

    # ── Run startup commands if file exists ────────────────────
    startup_file = BASE_DIR / "jarvis_startup.txt"
    if startup_file.exists():
        for line in startup_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                jarvis.process(line)

    # ── Main loop ──────────────────────────────────────────────
    while True:
        try:
            prompt = input(colored("  You: ", "green")).strip()
            if not jarvis.process(prompt):
                break
        except KeyboardInterrupt:
            print()
            jarvis._persist_history()
            jprint_say("Goodbye, Sir! 👋")
            break
        except EOFError:
            print()
            jarvis._persist_history()
            jprint_say("Goodbye, Sir! 👋")
            break
        except Exception:
            traceback.print_exc()
            jprint("Something went wrong. Continuing...", "red")


if __name__ == "__main__":
    main()