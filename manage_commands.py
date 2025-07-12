#!/usr/bin/env python3
"""
Utility for managing voice assistant commands
"""

import json
import os
import sys
from typing import Dict, Any

def load_commands(filename: str = 'commands.json') -> Dict[str, Any]:
    """Load commands from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON файла: {e}")
        return {}

def save_commands(commands: Dict[str, Any], filename: str = 'commands.json'):
    """Save commands to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(commands, f, ensure_ascii=False, indent=2)
        print(f"✅ Команды сохранены в {filename}")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def list_commands(commands: Dict[str, Any]):
    """List all commands"""
    if not commands:
        print("📝 Команды не найдены")
        return
    
    total_commands = 0
    for category, category_commands in commands.items():
        print(f"\n📂 {category.upper()}:")
        for cmd, data in category_commands.items():
            description = data.get('description', 'Без описания')
            action = data.get('action', 'Неизвестно')
            params = data.get('params', [])
            print(f"  🎯 {cmd}")
            print(f"     Действие: {action}")
            if params:
                print(f"     Параметры: {params}")
            print(f"     Описание: {description}")
            total_commands += 1
    
    print(f"\n📊 Всего команд: {total_commands}")

def add_command(commands: Dict[str, Any], category: str, command: str, action: str, params: list, description: str):
    """Add new command"""
    if category not in commands:
        commands[category] = {}
    
    commands[category][command] = {
        "action": action,
        "params": params,
        "description": description
    }
    print(f"✅ Команда '{command}' добавлена в категорию '{category}'")

def remove_command(commands: Dict[str, Any], command: str):
    """Remove command"""
    for category in commands:
        if command in commands[category]:
            del commands[category][command]
            print(f"✅ Команда '{command}' удалена из категории '{category}'")
            return
    print(f"❌ Команда '{command}' не найдена")

def search_command(commands: Dict[str, Any], query: str):
    """Search commands by query"""
    found = False
    for category, category_commands in commands.items():
        for cmd, data in category_commands.items():
            if query.lower() in cmd.lower() or query.lower() in data.get('description', '').lower():
                if not found:
                    print(f"\n🔍 Результаты поиска для '{query}':")
                    found = True
                print(f"  📂 {category}: {cmd}")
                print(f"     {data.get('description', 'Без описания')}")
    
    if not found:
        print(f"🔍 Команды с '{query}' не найдены")

def show_help():
    """Show help"""
    print("""
🎤 Утилита управления командами голосового ассистента

Использование:
  python manage_commands.py [команда] [параметры]

Команды:
  list                    - Показать все команды
  add <категория> <команда> <действие> <параметры> <описание>
                          - Добавить новую команду
  remove <команда>        - Удалить команду
  search <запрос>         - Найти команды
  help                    - Показать эту справку

Примеры:
  python manage_commands.py list
  python manage_commands.py add applications "открой spotify" open_app ["Spotify"] "Открывает Spotify"
  python manage_commands.py remove "открой spotify"
  python manage_commands.py search "браузер"

Доступные действия:
  - open_app: открыть приложение
  - kill_process: закрыть процесс
  - open_url: открыть URL
  - system_command: выполнить системную команду
  - move_mouse: двигать мышью
  - click_mouse: кликнуть мышью
  - say: произнести текст
  - take_screenshot: сделать скриншот
  - focus_mode: режим фокуса
  - timer_5_minutes: таймер
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    commands = load_commands()
    
    if command == 'list':
        list_commands(commands)
    
    elif command == 'add':
        if len(sys.argv) < 7:
            print("❌ Недостаточно параметров для добавления команды")
            print("Использование: add <категория> <команда> <действие> <параметры> <описание>")
            return
        
        category = sys.argv[2]
        cmd = sys.argv[3]
        action = sys.argv[4]
        params_str = sys.argv[5]
        description = sys.argv[6]
        
        try:
            params = json.loads(params_str) if params_str != '[]' else []
        except json.JSONDecodeError:
            print("❌ Ошибка в формате параметров. Используйте JSON формат, например: [\"param1\", \"param2\"]")
            return
        
        add_command(commands, category, cmd, action, params, description)
        save_commands(commands)
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("❌ Укажите команду для удаления")
            return
        
        cmd = sys.argv[2]
        remove_command(commands, cmd)
        save_commands(commands)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ Укажите запрос для поиска")
            return
        
        query = sys.argv[2]
        search_command(commands, query)
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        show_help()

if __name__ == "__main__":
    main() 