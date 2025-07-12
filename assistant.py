import speech_recognition as sr
import psutil
import os
import pyautogui
import time
from datetime import datetime
import threading
import subprocess
import platform
import pygame
import pyttsx3
import re
import json
import sys
import signal

def load_commands():
    """Load commands from JSON file"""
    try:
        with open('commands.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Файл commands.json не найден. Используются встроенные команды.")
        sys.stdout.flush()
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON файла: {e}")
        sys.stdout.flush()
        return {}

success_sound = os.path.abspath("success.wav")
error_sound = os.path.abspath("error.wav")

try:
    pygame.mixer.init()
except Exception as e:
    print(f"Ошибка инициализации pygame mixer: {e}")
    sys.stdout.flush()

def play_success():
    try:
        if os.path.exists(success_sound):
            pygame.mixer.Sound(success_sound).play()
    except Exception as e:
        print(f"Ошибка воспроизведения звука успеха: {e}")
        sys.stdout.flush()

def play_error():
    try:
        if os.path.exists(error_sound):
            pygame.mixer.Sound(error_sound).play()
    except Exception as e:
        print(f"Ошибка воспроизведения звука ошибки: {e}")
        sys.stdout.flush()

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    russian_voice = None
    for voice in voices:
        if 'russian' in voice.name.lower() or 'milena' in voice.name.lower():
            russian_voice = voice.id
            break
    if russian_voice:
        engine.setProperty('voice', russian_voice)
    else:
        if voices:
            engine.setProperty('voice', voices[0].id)
except Exception as e:
    print(f"Ошибка инициализации TTS: {e}")
    sys.stdout.flush()
    engine = None

def say(text):
    print(f"🗣️ {text}")
    sys.stdout.flush()
    try:
        if engine:
            engine.say(text)
            engine.runAndWait()
    except Exception as e:
        print(f"Ошибка озвучки: {e}")
        sys.stdout.flush()

commands_enabled = True
recording_note = False
note_lines = []
screen_recording = False
recording_process = None

def kill_process(name):
    found = False
    try:
        for proc in psutil.process_iter(['name']):
            if name.lower() in proc.info['name'].lower():
                proc.kill()
                found = True
        if found:
            play_success()
        else:
            play_error()
    except Exception as e:
        print(f"Ошибка при завершении процесса {name}: {e}")
        sys.stdout.flush()
        play_error()

def open_app(app_name):
    try:
        os.system(f"open -a '{app_name}'")
        play_success()
    except Exception as e:
        print(f"Ошибка при открытии приложения {app_name}: {e}")
        sys.stdout.flush()
        play_error()

def open_url(url):
    """Open URL in browser"""
    try:
        os.system(f"open '{url}'")
        play_success()
    except Exception as e:
        print(f"Ошибка при открытии URL {url}: {e}")
        sys.stdout.flush()
        play_error()

def system_command(command):
    """Execute system command"""
    try:
        os.system(command)
        play_success()
    except Exception as e:
        print(f"Ошибка при выполнении команды {command}: {e}")
        sys.stdout.flush()
        play_error()

def move_mouse():
    try:
        pyautogui.move(100, 0, duration=0.5)
        pyautogui.move(-100, 0, duration=0.5)
        play_success()
    except Exception as e:
        print(f"Ошибка при движении мыши: {e}")
        sys.stdout.flush()
        play_error()

def click_mouse():
    try:
        pyautogui.click()
        play_success()
    except Exception as e:
        print(f"Ошибка при клике мыши: {e}")
        sys.stdout.flush()
        play_error()

def close_all(name):
    count = 0
    try:
        for proc in psutil.process_iter(['name']):
            if name.lower() in proc.info['name'].lower():
                proc.kill()
                count += 1
        if count:
            play_success()
        else:
            play_error()
    except Exception as e:
        print(f"Ошибка при закрытии процессов {name}: {e}")
        sys.stdout.flush()
        play_error()

def take_screenshot():
    try:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.expanduser(f"~/Desktop/screenshot_{now}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        play_success()
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        sys.stdout.flush()
        play_error()

def focus_mode():
    """Enable focus mode - close distracting applications"""
    try:
        for app in ["Telegram", "Discord", "Messages"]:
            kill_process(app)
        open_app("Visual Studio Code")
        play_success()
    except Exception as e:
        print(f"Ошибка при включении режима фокуса: {e}")
        sys.stdout.flush()
        play_error()

def append_note(text):
    global note_lines
    note_lines.append(text)

def save_note():
    global note_lines
    try:
        if note_lines:
            path = os.path.expanduser("~/Desktop/voice_note.txt")
            with open(path, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}\n" + "\n".join(note_lines) + "\n\n")
            note_lines = []
            play_success()
        else:
            play_error()
    except Exception as e:
        print(f"Ошибка при сохранении заметки: {e}")
        sys.stdout.flush()
        play_error()

def cancel_note():
    global note_lines
    note_lines.clear()
    play_success()

def timer_5_minutes():
    """Set timer for 5 minutes"""
    try:
        say("Таймер на 5 минут установлен")
        def timer_callback():
            time.sleep(300)
            say("Время истекло! Таймер на 5 минут завершен")
        threading.Thread(target=timer_callback, daemon=True).start()
    except Exception as e:
        print(f"Ошибка установки таймера: {e}")
        sys.stdout.flush()
        play_error()

def timer_10_minutes():
    """Set timer for 10 minutes"""
    try:
        say("Таймер на 10 минут установлен")
        def timer_callback():
            time.sleep(600)
            say("Время истекло! Таймер на 10 минут завершен")
        threading.Thread(target=timer_callback, daemon=True).start()
    except Exception as e:
        print(f"Ошибка установки таймера: {e}")
        sys.stdout.flush()
        play_error()

def timer_30_minutes():
    """Set timer for 30 minutes"""
    try:
        say("Таймер на 30 минут установлен")
        def timer_callback():
            time.sleep(1800)
            say("Время истекло! Таймер на 30 минут завершен")
        threading.Thread(target=timer_callback, daemon=True).start()
    except Exception as e:
        print(f"Ошибка установки таймера: {e}")
        sys.stdout.flush()
        play_error()

FUNCTION_MAP = {
    "open_app": open_app,
    "kill_process": kill_process,
    "open_url": open_url,
    "system_command": system_command,
    "move_mouse": move_mouse,
    "click_mouse": click_mouse,
    "take_screenshot": take_screenshot,
    "focus_mode": focus_mode,
    "say": say,
    "disable_commands": lambda: disable_commands(),
    "enable_commands": lambda: enable_commands(),
    "timer_5_minutes": timer_5_minutes,
    "timer_10_minutes": timer_10_minutes,
    "timer_30_minutes": timer_30_minutes
}

def disable_commands():
    global commands_enabled
    commands_enabled = False
    play_success()

def enable_commands():
    global commands_enabled
    commands_enabled = True
    play_success()

def disable_commands_for(duration, unit):
    global commands_enabled
    commands_enabled = False
    play_success()
    seconds = duration
    if unit.startswith('мин'):
        seconds *= 60
    elif unit.startswith('час'):
        seconds *= 3600
    def reenable():
        global commands_enabled
        time.sleep(seconds)
        commands_enabled = True
        play_success()
    threading.Thread(target=reenable, daemon=True).start()

def click_mouse_times(times):
    try:
        for _ in range(times):
            pyautogui.click()
            time.sleep(0.1)
        play_success()
    except Exception as e:
        print(f"Ошибка при клике мыши {times} раз: {e}")
        sys.stdout.flush()
        play_error()

def move_mouse_direction(direction, pixels):
    try:
        dx, dy = 0, 0
        if direction == 'вверх':
            dy = -pixels
        elif direction == 'вниз':
            dy = pixels
        elif direction == 'влево':
            dx = -pixels
        elif direction == 'вправо':
            dx = pixels
        pyautogui.move(dx, dy, duration=0.5)
        play_success()
    except Exception as e:
        print(f"Ошибка при движении мыши: {e}")
        sys.stdout.flush()
        play_error()

def execute_command(command_data):
    """Execute command based on JSON data"""
    try:
        action = command_data.get("action")
        params = command_data.get("params", [])
        
        if action in FUNCTION_MAP:
            func = FUNCTION_MAP[action]
            if params:
                func(*params)
            else:
                func()
        else:
            print(f"Неизвестное действие: {action}")
            sys.stdout.flush()
            play_error()
    except Exception as e:
        print(f"Ошибка при выполнении команды: {e}")
        sys.stdout.flush()
        play_error()

def recognize_command():
    global recording_note, commands_enabled
    
    commands_data = load_commands()
    
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Слушаю...")
            sys.stdout.flush()
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="ru-RU").lower()
            print(f"Ты сказал: {text}")
            sys.stdout.flush()

            if recording_note:
                if "сохрани заметку" in text:
                    save_note()
                    recording_note = False
                    return
                elif "удали заметку" in text:
                    cancel_note()
                    recording_note = False
                    return
                else:
                    append_note(text)
                    return

            if "запиши заметку" in text:
                recording_note = True
                note_lines.clear()
                play_success()
                return

            for category, commands in commands_data.items():
                for cmd_phrase, cmd_data in commands.items():
                    if cmd_phrase in text:
                        if category == "assistant_control":
                            execute_command(cmd_data)
                            return
                        
                        if cmd_phrase == "включи команды":
                            execute_command(cmd_data)
                            return

                        if not commands_enabled:
                            print("Команды выключены.")
                            sys.stdout.flush()
                            return
                        
                        execute_command(cmd_data)
                        return

            m = re.search(r"выключи команды на (\d+) (секунд[уы]?|минут[уы]?|час[аов]?)", text)
            if m:
                duration = int(m.group(1))
                unit = m.group(2)
                disable_commands_for(duration, unit)
                return
            m = re.search(r"кликни (\d+) раз", text)
            if m:
                times = int(m.group(1))
                click_mouse_times(times)
                return
            m = re.search(r"пошевели мышкой (вверх|вниз|влево|вправо) (\d+) пиксел[еяй]", text)
            if m:
                direction = m.group(1)
                pixels = int(m.group(2))
                move_mouse_direction(direction, pixels)
                return

            if not commands_enabled:
                print("Команды выключены.")
                sys.stdout.flush()
                return

            play_error()
        except sr.UnknownValueError:
            play_error()
        except sr.RequestError as e:
            print(f"Ошибка распознавания речи: {e}")
            sys.stdout.flush()
            play_error()
    except Exception as e:
        print(f"Ошибка при работе с микрофоном: {e}")
        sys.stdout.flush()
        play_error()

def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    print("\n🛑 Получен сигнал завершения. Останавливаю ассистента...")
    sys.stdout.flush()
    print("👋 Ассистент остановлен!")
    sys.stdout.flush()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎤 Голосовой ассистент запущен!")
    sys.stdout.flush()
    print("Скажите команду...")
    sys.stdout.flush()
    
    commands_data = load_commands()
    if commands_data:
        print(f"✅ Загружено {sum(len(commands) for commands in commands_data.values())} команд из JSON файла")
        sys.stdout.flush()
    else:
        print("⚠️ Команды не загружены из JSON файла")
        sys.stdout.flush()
    
    while True:
        try:
            recognize_command()
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            sys.stdout.flush()
            break
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            sys.stdout.flush()
            time.sleep(1)
