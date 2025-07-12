#!/usr/bin/env python3
"""
Graphical interface for managing voice assistant commands
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import json
import os
import sys
import threading
import subprocess
import queue
import time
import signal
from typing import Dict, Any

class CommandsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Ассистент (by Лонер | @i_o_ekobo)")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        self.commands = self.load_commands()
        
        self.assistant_process = None
        self.assistant_running = False
        self.log_queue = queue.Queue()
        self.listening_animation = False
        self.animation_dots = 0
        
        self.available_actions = [
            "open_app",
            "kill_process", 
            "open_url",
            "system_command",
            "move_mouse",
            "click_mouse",
            "take_screenshot",
            "focus_mode",
            "say",
            "disable_commands",
            "enable_commands"
        ]
        
        self.available_categories = [
            "applications",
            "close_applications", 
            "websites",
            "system",
            "music",
            "mouse",
            "special",
            "assistant_control"
        ]
        
        self.setup_ui()
        self.refresh_commands_list()
        
        self.process_logs()
    
    def load_commands(self) -> Dict[str, Any]:
        """Load commands from JSON file"""
        try:
            with open('commands.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showwarning("Предупреждение", "Файл commands.json не найден. Будет создан новый файл.")
            return {}
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка", f"Ошибка чтения JSON файла: {e}")
            return {}
    
    def save_commands(self):
        """Save commands to JSON file"""
        try:
            with open('commands.json', 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Команды сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def setup_ui(self):
        """Setup user interface"""
        main_frame = ttk.Frame(self.root, padding="8")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        banner_frame = ttk.Frame(main_frame)
        banner_frame.grid(row=0, column=0, columnspan=3, pady=(10, 10), sticky="ew")
        banner_frame.columnconfigure(0, weight=1)
        
        banner_label = ttk.Label(
            banner_frame,
            text="👋 Добро пожаловать в голосовой ассистент!\n\nНажмите ▶️ чтобы запустить ассистента.\nДобавляйте, редактируйте и тестируйте команды справа.",
            font=("Arial", 15, "bold"),
            anchor="center",
            justify="center"
        )
        banner_label.grid(row=0, column=0, sticky="ew")
        
        title_label = ttk.Label(main_frame, text="Управление командами голосового ассистента", font=("Arial", 12, "bold"))
        title_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        left_frame = ttk.LabelFrame(main_frame, text="📋 Команды", padding="8")
        left_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="🔍:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_commands)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        
        self.commands_tree = ttk.Treeview(left_frame, columns=("category", "action"), 
                                         show="tree headings", height=22)
        self.commands_tree.grid(row=1, column=0, sticky="nsew")
        
        self.commands_tree.heading("#0", text="Команда")
        self.commands_tree.heading("category", text="Категория")
        self.commands_tree.heading("action", text="Действие")
        
        self.commands_tree.column("#0", width=200)
        self.commands_tree.column("category", width=100)
        self.commands_tree.column("action", width=80)
        
        commands_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.commands_tree.yview)
        commands_scrollbar.grid(row=1, column=1, sticky="ns")
        self.commands_tree.configure(yscrollcommand=commands_scrollbar.set)
        
        list_buttons_frame = ttk.Frame(left_frame)
        list_buttons_frame.grid(row=2, column=0, columnspan=2, pady=(8, 0))
        list_buttons_frame.columnconfigure(0, weight=1)
        list_buttons_frame.columnconfigure(1, weight=1)
        list_buttons_frame.columnconfigure(2, weight=1)
        list_buttons_frame.columnconfigure(3, weight=1)
        
        ttk.Button(list_buttons_frame, text="➕", command=self.add_command_dialog, width=3).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(list_buttons_frame, text="✏️", command=self.edit_command_dialog, width=3).grid(row=0, column=1, padx=(0, 2))
        ttk.Button(list_buttons_frame, text="🗑️", command=self.delete_command, width=3).grid(row=0, column=2, padx=(0, 2))
        ttk.Button(list_buttons_frame, text="🔄", command=self.refresh_commands_list, width=3).grid(row=0, column=3)
        
        center_frame = ttk.LabelFrame(main_frame, text="📝 Редактирование команды", padding="10")
        center_frame.grid(row=2, column=1, sticky="nsew", padx=(0, 8))
        center_frame.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(center_frame, text="Команда:").grid(row=row, column=0, sticky="w", pady=8)
        self.command_var = tk.StringVar()
        ttk.Entry(center_frame, textvariable=self.command_var, width=60, font=("Arial", 12)).grid(row=row, column=1, sticky="ew", pady=8)
        row += 1
        ttk.Label(center_frame, text="Категория:").grid(row=row, column=0, sticky="w", pady=8)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(center_frame, textvariable=self.category_var, values=self.available_categories, width=57, font=("Arial", 12))
        category_combo.grid(row=row, column=1, sticky="ew", pady=8)
        row += 1
        ttk.Label(center_frame, text="Действие:").grid(row=row, column=0, sticky="w", pady=8)
        self.action_var = tk.StringVar()
        action_combo = ttk.Combobox(center_frame, textvariable=self.action_var, values=self.available_actions, width=57, font=("Arial", 12))
        action_combo.grid(row=row, column=1, sticky="ew", pady=8)
        row += 1
        ttk.Label(center_frame, text="Параметры:").grid(row=row, column=0, sticky="w", pady=8)
        self.params_var = tk.StringVar()
        ttk.Entry(center_frame, textvariable=self.params_var, width=60, font=("Arial", 12)).grid(row=row, column=1, sticky="ew", pady=8)
        row += 1
        ttk.Label(center_frame, text="Описание:").grid(row=row, column=0, sticky="w", pady=8)
        self.description_var = tk.StringVar()
        ttk.Entry(center_frame, textvariable=self.description_var, width=60, font=("Arial", 12)).grid(row=row, column=1, sticky="ew", pady=8)
        row += 1
        
        buttons_frame = ttk.Frame(center_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        ttk.Button(buttons_frame, text="💾 Сохранить команду", command=self.save_current_command).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Отменить", command=self.clear_form).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(buttons_frame, text="💾 Сохранить файл", command=self.save_commands).grid(row=0, column=2)
        
        right_frame = ttk.LabelFrame(main_frame, text="🎛️ Управление ассистентом", padding="10")
        right_frame.grid(row=2, column=2, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(right_frame, text="Статус: Остановлен", font=("Arial", 12, "bold"))
        self.status_label.grid(row=0, column=0, pady=(0, 10))
        
        assistant_buttons_frame = ttk.Frame(right_frame)
        assistant_buttons_frame.grid(row=1, column=0, pady=(0, 10))
        assistant_buttons_frame.columnconfigure(0, weight=1)
        assistant_buttons_frame.columnconfigure(1, weight=1)
        assistant_buttons_frame.columnconfigure(2, weight=1)
        
        self.start_button = ttk.Button(assistant_buttons_frame, text="▶️ Запустить", command=self.start_assistant)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(assistant_buttons_frame, text="⏹️ Остановить", command=self.stop_assistant, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 5))
        
        self.restart_button = ttk.Button(assistant_buttons_frame, text="🔄 Перезапустить", command=self.restart_assistant, state="disabled")
        self.restart_button.grid(row=0, column=2)
        
        ttk.Button(right_frame, text="🗑️ Очистить терминал", command=self.clear_terminal).grid(row=2, column=0, pady=(0, 10))
        
        self.stats_label = ttk.Label(right_frame, text="Команд: 0 | Категорий: 0", font=("Arial", 10))
        self.stats_label.grid(row=3, column=0, pady=(0, 10))
        
        terminal_frame = ttk.LabelFrame(right_frame, text="📊 Терминал", padding="5")
        terminal_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        terminal_frame.columnconfigure(0, weight=1)
        terminal_frame.rowconfigure(0, weight=1)
        
        self.terminal_text = scrolledtext.ScrolledText(terminal_frame, width=50, height=15, font=("Consolas", 9))
        self.terminal_text.grid(row=0, column=0, sticky="nsew")
        
        self.commands_tree.bind('<<TreeviewSelect>>', self.on_command_select)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.update_stats()
        self.update_assistant_controls()
    
    def update_assistant_controls(self):
        """Update assistant control buttons state"""
        if self.assistant_running:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.restart_button.config(state="normal")
            self.status_label.config(text="Статус: Работает", foreground="green")
        else:
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.restart_button.config(state="disabled")
            self.status_label.config(text="Статус: Остановлен", foreground="red")
    
    def start_assistant(self):
        """Start assistant process"""
        if self.assistant_running:
            return
        
        try:
            self.assistant_process = subprocess.Popen(
                [sys.executable, 'assistant.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.assistant_running = True
            self.update_assistant_controls()
            self.start_listening_animation()
            
            output_thread = threading.Thread(target=self.read_assistant_output, daemon=True)
            output_thread.start()
            
            self.log_to_terminal("🎤 Ассистент запущен!", "green")
        except Exception as e:
            self.log_to_terminal(f"❌ Ошибка запуска ассистента: {e}", "red")
    
    def restart_assistant(self):
        """Restart assistant process"""
        self.stop_assistant()
        time.sleep(1)
        self.start_assistant()
    
    def stop_assistant(self, force=False):
        """Stop assistant process"""
        if not self.assistant_running or not self.assistant_process:
            return
        
        try:
            if force:
                self.assistant_process.kill()
            else:
                self.assistant_process.terminate()
                
            try:
                self.assistant_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.assistant_process.kill()
                self.assistant_process.wait()
                
        except Exception as e:
            self.log_to_terminal(f"❌ Ошибка остановки ассистента: {e}", "red")
        finally:
            self.assistant_running = False
            self.assistant_process = None
            self.update_assistant_controls()
            self.stop_listening_animation()
            self.log_to_terminal("🛑 Ассистент остановлен", "orange")
    
    def read_assistant_output(self):
        """Read assistant process output"""
        try:
            for line in iter(self.assistant_process.stdout.readline, ''):
                if line:
                    self.log_queue.put(line.strip())
                if self.assistant_process.poll() is not None:
                    break
        except Exception as e:
            self.log_to_terminal(f"❌ Ошибка чтения вывода: {e}", "red")
        finally:
            self.assistant_running = False
            self.root.after(0, self.update_assistant_controls)
            self.root.after(0, self.stop_listening_animation)
    
    def start_listening_animation(self):
        """Start listening animation"""
        self.listening_animation = True
        self.animate_listening()
    
    def stop_listening_animation(self):
        """Stop listening animation"""
        self.listening_animation = False
        self.animation_dots = 0
    
    def animate_listening(self):
        """Animate listening indicator"""
        if self.listening_animation:
            dots = "." * self.animation_dots
            self.status_label.config(text=f"Статус: Слушает{dots}")
            self.animation_dots = (self.animation_dots + 1) % 4
            self.root.after(500, self.animate_listening)
    
    def log_to_terminal(self, message, color="white", force=False):
        """Log message to terminal"""
        if not force and not self.assistant_running:
            return
            
        color_tags = {
            "green": "green",
            "red": "red", 
            "orange": "orange",
            "blue": "blue"
        }
        
        tag = color_tags.get(color, "white")
        timestamp = time.strftime("%H:%M:%S")
        
        self.terminal_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.terminal_text.see(tk.END)
        
        if tag != "white":
            self.terminal_text.tag_config(tag, foreground=tag)
    
    def clear_terminal(self):
        """Clear terminal output"""
        try:
            self.terminal_text.delete(1.0, tk.END)
            self.log_to_terminal("🗑️ Терминал очищен", "blue", force=True)
        except Exception as e:
            self.log_to_terminal(f"❌ Ошибка очистки терминала: {e}", "red", force=True)
    
    def process_logs(self):
        """Process log queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_to_terminal(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_logs)
    
    def refresh_commands_list(self):
        """Refresh commands list"""
        for item in self.commands_tree.get_children():
            self.commands_tree.delete(item)
        
        for category, commands in self.commands.items():
            category_item = self.commands_tree.insert("", "end", text=category, values=("", ""))
            for command, data in commands.items():
                action = data.get("action", "")
                self.commands_tree.insert(category_item, "end", text=command, values=(category, action))
        
        self.update_stats()
    
    def filter_commands(self, *args):
        """Filter commands by search term"""
        search_term = self.search_var.get().lower()
        
        for item in self.commands_tree.get_children():
            self.commands_tree.delete(item)
        
        for category, commands in self.commands.items():
            if search_term in category.lower():
                category_item = self.commands_tree.insert("", "end", text=category, values=("", ""))
                for command, data in commands.items():
                    action = data.get("action", "")
                    description = data.get("description", "")
                    if (search_term in command.lower() or 
                        search_term in action.lower() or 
                        search_term in description.lower()):
                        self.commands_tree.insert(category_item, "end", text=command, values=(category, action))
            else:
                category_item = None
                for command, data in commands.items():
                    action = data.get("action", "")
                    description = data.get("description", "")
                    if (search_term in command.lower() or 
                        search_term in action.lower() or 
                        search_term in description.lower()):
                        if category_item is None:
                            category_item = self.commands_tree.insert("", "end", text=category, values=("", ""))
                        self.commands_tree.insert(category_item, "end", text=command, values=(category, action))
    
    def on_command_select(self, event):
        """Handle command selection"""
        selection = self.commands_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        parent = self.commands_tree.parent(item)
        
        if parent:
            category = self.commands_tree.item(parent)["text"]
            command = self.commands_tree.item(item)["text"]
            
            if category in self.commands and command in self.commands[category]:
                data = self.commands[category][command]
                
                self.command_var.set(command)
                self.category_var.set(category)
                self.action_var.set(data.get("action", ""))
                
                params = data.get("params", [])
                if isinstance(params, list):
                    self.params_var.set(", ".join(map(str, params)))
                else:
                    self.params_var.set(str(params))
                
                self.description_var.set(data.get("description", ""))
    
    def add_command_dialog(self):
        """Show add command dialog"""
        self.clear_form()
        self.command_var.set("")
        self.category_var.set("applications")
        self.action_var.set("open_app")
        self.params_var.set("")
        self.description_var.set("")
    
    def edit_command_dialog(self):
        """Show edit command dialog"""
        selection = self.commands_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите команду для редактирования")
            return
        self.on_command_select(None)
    
    def delete_command(self):
        """Delete selected command"""
        selection = self.commands_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите команду для удаления")
            return
        
        item = selection[0]
        parent = self.commands_tree.parent(item)
        
        if parent:
            category = self.commands_tree.item(parent)["text"]
            command = self.commands_tree.item(item)["text"]
            
            if messagebox.askyesno("Подтверждение", f"Удалить команду '{command}'?"):
                if category in self.commands and command in self.commands[category]:
                    del self.commands[category][command]
                    if not self.commands[category]:
                        del self.commands[category]
                    self.refresh_commands_list()
                    self.clear_form()
                    messagebox.showinfo("Успех", "Команда удалена!")
    
    def save_current_command(self):
        """Save current command"""
        command = self.command_var.get().strip()
        category = self.category_var.get().strip()
        action = self.action_var.get().strip()
        params_str = self.params_var.get().strip()
        description = self.description_var.get().strip()
        
        if not command or not category or not action:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return
        
        if category not in self.commands:
            self.commands[category] = {}
        
        params = []
        if params_str:
            params = [p.strip() for p in params_str.split(",")]
        
        self.commands[category][command] = {
            "action": action,
            "params": params,
            "description": description
        }
        
        self.refresh_commands_list()
        messagebox.showinfo("Успех", "Команда сохранена!")
    
    def clear_form(self):
        """Clear form fields"""
        self.command_var.set("")
        self.category_var.set("")
        self.action_var.set("")
        self.params_var.set("")
        self.description_var.set("")
    
    def update_stats(self):
        """Update statistics"""
        total_commands = sum(len(commands) for commands in self.commands.values())
        total_categories = len(self.commands)
        self.stats_label.config(text=f"Команд: {total_commands} | Категорий: {total_categories}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.assistant_running:
            self.stop_assistant(force=True)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = CommandsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 