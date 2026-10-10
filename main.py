import argparse
import os
import shlex
import tkinter as tk
from tkinter import scrolledtext

DEFAULT_VFS_NAME = "VFS_Emulator"

class VFSNode:
    def __init__(self, name, is_dir=False, content=b"", parent=None):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}
        self.parent = parent

class VFS:
    def __init__(self, name=DEFAULT_VFS_NAME):
        self.name = name
        self.root = VFSNode("/", is_dir=True)

    def load_from_dir(self, path):
        if not os.path.exists(path):
            raise ValueError(f"директория VFS не найдена: {path}")
        if not os.path.isdir(path):
            raise ValueError(f"не директория: {path}")

        self.name = os.path.basename(os.path.abspath(path)) or DEFAULT_VFS_NAME
        self.root = VFSNode("/", is_dir=True)
        self._load_recursive(path, self.root)

    def _load_recursive(self, fs_path, node):
        try:
            entries = os.listdir(fs_path)
        except OSError as e:
            raise ValueError(f"ошибка чтения директории {fs_path}: {e}")

        for entry in sorted(entries):
            full = os.path.join(fs_path, entry)
            if os.path.isdir(full):
                child = VFSNode(entry, is_dir=True, parent=node)
                node.children[entry] = child
                self._load_recursive(full, child)
            else:
                try:
                    with open(full, "rb") as f:
                        content = f.read()
                except OSError:
                    content = b""
                child = VFSNode(entry, is_dir=False, content=content, parent=node)
                node.children[entry] = child

    def resolve(self, cwd_node, path):
        if not path or path == ".":
            return cwd_node
        if path.startswith("/"):
            node = self.root
        else:
            node = cwd_node
        parts = [p for p in path.split("/") if p]
        for part in parts:
            if part == "..":
                if node.parent is not None:
                    node = node.parent
            elif part == ".":
                continue
            else:
                if not node.is_dir or part not in node.children:
                    raise ValueError(f"путь не найден: {path}")
                node = node.children[part]
        return node

    def list_dir(self, node):
        if not node.is_dir:
            raise ValueError(f"'{node.name}' — не каталог")
        return sorted(node.children.values(), key=lambda n: n.name)
        
class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.exit_requested = False

        self.vfs = VFS()

        self.debug_config = (
            f"vfs = {self.vfs_path}\n"
            f"script = {self.script_path}\n"
        )

        self.output_area = scrolledtext.ScrolledText(root)
        self.output_area.pack(fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X)

        self.prompt_label = tk.Label(self.input_frame, text=f"{self.vfs_name}:$ ")
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.focus_set()

        self.cwd = self.vfs.root
        self.cwd_path = "/"

        if self.vfs_path:
            try:
                self.vfs.load_from_dir(self.vfs_path)
                self.cwd = self.vfs.root
                self.cwd_path = "/"
                self.print_line(f"[vfs] VFS загружена из: {self.vfs_path}")
            except ValueError as e:
                self.print_line(f"Ошибка загрузки VFS: {e}")
        else:
            self.print_line("[vfs] VFS в памяти (пустая)")

        self.root.title(f"Эмулятор - [{self.vfs.name}]")
        
        self.print_line("Добро пожаловать в эмулятор!")
        self.print_line("[debug] Параметры запуска:")
        self.print_line(self.debug_config)
        self.print_line("Доступные команды: ls, cd, exit\n")

        self.update_prompt()
        
        if self.script_path:
            self.run_script(self.script_path)

    def print_line(self, text=""):
        self.output_area.configure(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state=tk.DISABLED)

    def update_prompt(self):
        self.prompt_label.config(text=f"{self.vfs.name}:{self.cwd_path}$ ")
        
    def parse_command(self, line):
        try:
            parts = shlex.split(line)
        except ValueError:
            raise ValueError("незакрытая кавычка в строке")
        if not parts:
            return None, []
        return parts[0], parts[1:]

    def on_enter(self, event=None):
        line = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.print_line(f"{self.vfs_name}:$ {line}")
        if not line.strip():
            return
        self.process_line(line)

    def process_line(self, line):
        try:
            command, args = self.parse_command(line)
        except ValueError as e:
            self.print_line(f"Ошибка: {e}")
            return False
        if command is None:
            return True
        return self.execute_command(command, args)

    def execute_command(self, command, args):
        if command == "exit":
            return self.cmd_exit(args)
        elif command == "ls":
            return self.cmd_ls(args)
        elif command == "cd":
            return self.cmd_cd(args)
        else:
            self.print_line(f"Ошибка: неизвестная команда '{command}'")
            return False

    def cmd_exit(self, args):
        if args:
            self.print_line("Ошибка: команда 'exit' не принимает аргументов")
            return False
        self.print_line("Завершение работы эмулятора")
        self.exit_requested = True
        return True

    def cmd_ls(self, args):
        self.print_line(f"ls: {args}")
        return True
        
    def cmd_cd(self, args):
        self.print_line(f"cd: {args}")
        return True
        
    def run_script(self, path):
        self.print_line(f"\n[script] Запуск стартового скрипта: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as e:
            self.print_line(f"Ошибка: не удалось открыть скрипт '{path}': {e}")
            return

        for raw in lines:
            if self.exit_requested:
                break
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            self.print_line(f"{self.vfs_name}:$ {line}")
            ok = self.process_line(line)
            if self.exit_requested:
                break
            if not ok:
                self.print_line(f"[script] Ошибка при выполнении: {line}")

        if not self.exit_requested:
            self.print_line("[script] Скрипт выполнен.")

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки"
    )
    parser.add_argument("--vfs", dest="vfs_path", default=None, help="Путь к физическому расположению VFS.")
    parser.add_argument("--script", dest="script_path", default=None, help="Путь к стартовому скрипту.")
    return parser.parse_args(argv)
    
def main():
    args = parse_args()
    root = tk.Tk()
    emu = ShellEmulator(root,vfs_path=args.vfs_path, script_path=args.script_path)
    root.mainloop()
    if emu.exit_requested:
        try:
            root.destroy()
        except tk.TclError:
            pass

if __name__ == "__main__":
    main()
