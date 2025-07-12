#!/usr/bin/env python3
"""
Script for launching the graphical interface for command management
"""

import sys
import subprocess

def check_dependencies():
    """Check for required dependencies"""
    try:
        import tkinter
        import json
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        return False

def main():
    print("🎤 Запуск графического интерфейса управления командами...")
    
    if not check_dependencies():
        print("❌ Не удалось запустить GUI. Установите зависимости:")
        print("pip install -r requirements.txt")
        return
    
    try:
        from gui_commands import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Ошибка запуска GUI: {e}")
        print("Попробуйте запустить напрямую: python gui_commands.py")

if __name__ == "__main__":
    main() 