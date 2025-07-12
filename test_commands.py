#!/usr/bin/env python3
"""
Тестовый скрипт для проверки всех команд голосового ассистента
"""

import json
import sys
import os
from typing import Dict, Any

def load_commands() -> Dict[str, Any]:
    """Загружает команды из JSON файла"""
    try:
        with open('commands.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Файл commands.json не найден")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON файла: {e}")
        return {}

def test_command_structure(commands: Dict[str, Any]) -> bool:
    """Тестирует структуру команд"""
    print("🔍 Тестирование структуры команд...")
    
    if not commands:
        print("❌ Команды не загружены")
        return False
    
    required_fields = ["action", "params", "description"]
    valid_actions = [
        "open_app", "kill_process", "open_url", "system_command",
        "move_mouse", "click_mouse", "take_screenshot", "focus_mode",
        "say", "disable_commands", "enable_commands",
        "timer_5_minutes", "timer_10_minutes", "timer_30_minutes"
    ]
    
    valid_categories = [
        "applications", "close_applications", "websites", "system",
        "music", "mouse", "special", "assistant_control"
    ]
    
    errors = []
    total_commands = 0
    
    for category, category_commands in commands.items():
        if category not in valid_categories:
            errors.append(f"❌ Неизвестная категория: {category}")
        
        for command, data in category_commands.items():
            total_commands += 1
            
            # Проверяем обязательные поля
            for field in required_fields:
                if field not in data:
                    errors.append(f"❌ Команда '{command}' не имеет поля '{field}'")
            
            # Проверяем действие
            if "action" in data and data["action"] not in valid_actions:
                errors.append(f"❌ Команда '{command}' имеет неизвестное действие: {data['action']}")
            
            # Проверяем параметры
            if "params" in data and not isinstance(data["params"], list):
                errors.append(f"❌ Команда '{command}' имеет неправильный формат параметров")
    
    print(f"📊 Найдено {total_commands} команд в {len(commands)} категориях")
    
    if errors:
        print("\n❌ Найдены ошибки:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ Структура команд корректна")
        return True

def test_specific_commands(commands: Dict[str, Any]) -> bool:
    """Тестирует конкретные команды"""
    print("\n🎯 Тестирование конкретных команд...")
    
    # Список важных команд для проверки
    important_commands = {
        "applications": ["открой браузер", "открой терминал", "открой код"],
        "websites": ["открой youtube", "открой github"],
        "system": ["заблокируй экран", "открой папку загрузки"],
        "music": ["включи музыку", "пауза"],
        "assistant_control": ["выключи команды", "включи команды"]
    }
    
    missing_commands = []
    
    for category, expected_commands in important_commands.items():
        if category not in commands:
            missing_commands.extend([f"{category}: {cmd}" for cmd in expected_commands])
            continue
            
        for cmd in expected_commands:
            if cmd not in commands[category]:
                missing_commands.append(f"{category}: {cmd}")
    
    if missing_commands:
        print("⚠️ Отсутствуют важные команды:")
        for cmd in missing_commands:
            print(f"  {cmd}")
        return False
    else:
        print("✅ Все важные команды присутствуют")
        return True

def test_command_descriptions(commands: Dict[str, Any]) -> bool:
    """Тестирует описания команд"""
    print("\n📝 Тестирование описаний команд...")
    
    empty_descriptions = []
    
    for category, category_commands in commands.items():
        for command, data in category_commands.items():
            description = data.get("description", "")
            if not description or description.strip() == "":
                empty_descriptions.append(f"{category}: {command}")
    
    if empty_descriptions:
        print("⚠️ Команды без описаний:")
        for cmd in empty_descriptions:
            print(f"  {cmd}")
        return False
    else:
        print("✅ Все команды имеют описания")
        return True

def test_duplicate_commands(commands: Dict[str, Any]) -> bool:
    """Тестирует дублирование команд"""
    print("\n🔄 Тестирование дублирования команд...")
    
    all_commands = []
    duplicates = []
    
    for category, category_commands in commands.items():
        for command in category_commands.keys():
            if command in all_commands:
                duplicates.append(command)
            all_commands.append(command)
    
    if duplicates:
        print("⚠️ Найдены дублирующиеся команды:")
        for cmd in set(duplicates):
            print(f"  {cmd}")
        return False
    else:
        print("✅ Дублирующихся команд не найдено")
        return True

def generate_command_summary(commands: Dict[str, Any]):
    """Генерирует сводку по командам"""
    print("\n📊 Сводка по командам:")
    
    total_commands = 0
    for category, category_commands in commands.items():
        count = len(category_commands)
        total_commands += count
        print(f"  📂 {category}: {count} команд")
    
    print(f"\n🎯 Всего команд: {total_commands}")
    
    # Показываем примеры команд
    print("\n📋 Примеры команд:")
    for category, category_commands in list(commands.items())[:3]:
        print(f"  📂 {category}:")
        for i, (cmd, data) in enumerate(list(category_commands.items())[:2]):
            action = data.get("action", "неизвестно")
            print(f"    • {cmd} → {action}")

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование команд голосового ассистента")
    print("=" * 50)
    
    # Загружаем команды
    commands = load_commands()
    if not commands:
        print("❌ Не удалось загрузить команды")
        sys.exit(1)
    
    # Запускаем тесты
    tests = [
        test_command_structure,
        test_specific_commands,
        test_command_descriptions,
        test_duplicate_commands
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        if test(commands):
            passed_tests += 1
    
    # Генерируем сводку
    generate_command_summary(commands)
    
    # Результат
    print("\n" + "=" * 50)
    print(f"📊 Результат тестирования: {passed_tests}/{total_tests} тестов пройдено")
    
    if passed_tests == total_tests:
        print("🎉 Все тесты пройдены успешно!")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 