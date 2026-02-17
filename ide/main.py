import sys
import json
import os
import platform
import subprocess
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget, QLabel
from PyQt6.QtGui import QAction, QKeySequence
from ui import ZegaUI, ZegaSplash

class ZegaController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # ZEGA Core Registry Paths
        self.settings_path = "settings.json"
        self.keywords_path = "keywords.json"

        # Initialize Registry with ZEGA Standards
        default_settings = {
            "font_size": 13, 
            "theme": "system", # dark, light, system, dyslexic
            "type": "regular"   # regular, bold, italics
        }
        
        self.settings = self.load_registry(self.settings_path, default_settings)
        self.keywords = self.load_registry(self.keywords_path, {"tiers": {}})
        
        self.show_splash()

    # --- REGISTRY ENGINE ---

    def load_registry(self, path, default_data):
        """High-performance JSON Read with Auto-Recovery"""
        if not os.path.exists(path):
            self.write_registry(path, default_data)
            return default_data
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Recovery protocol if JSON is corrupted
            return default_data

    def write_registry(self, path, data):
        """Thread-safe JSON Write"""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"ZEGA REGISTRY ERROR: {e}")

    # --- BOOT & PROJECT LOGIC ---

    def show_splash(self):
        self.splash = ZegaSplash()
        self.splash.btn_new.clicked.connect(self.new_project)
        self.splash.btn_open.clicked.connect(self.open_project)
        self.splash.exec()

    def new_project(self):
        path = QFileDialog.getExistingDirectory(None, "Select New Project Folder")
        if path:
            self.boot_ide(path)

    def open_project(self):
        path = QFileDialog.getExistingDirectory(None, "Open Existing Project Folder")
        if path:
            self.boot_ide(path)

    def apply_theme_logic(self):
        """Calculates dynamic settings before UI boot"""
        theme = self.settings.get("theme", "system").lower()
        if theme == "dyslexic":
            self.settings["font_size"] = max(14, self.settings.get("font_size", 14))
        return theme

    def boot_ide(self, project_path):
        self.splash.close()
        self.current_file = None
        self.apply_theme_logic()
        
        # Initialize UI with Registry Data
        self.window = ZegaUI(self.keywords, self.settings)
        self.window.model.setRootPath(project_path)
        self.window.explorer.setRootIndex(self.window.model.index(project_path))
        
        # Signal Mapping
        if "⚙️" in self.window.btns:
            self.window.btns["⚙️"].clicked.connect(self.open_settings_external)
        
        self.window.explorer.doubleClicked.connect(self.open_file)
        
        # Keyboard Shortcut: Ctrl+S for Pro-Saving
        save_act = QAction("Save", self.window)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self.save_file)
        self.window.addAction(save_act)

        self.window.show()

    # --- FILE I/O OPERATIONS ---

    def open_file(self, index):
        path = self.window.model.filePath(index)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.window.editor.setPlainText(f.read())
                self.current_file = path
                # Update ZEGA Title bar
                filename = os.path.basename(path).upper()
                self.window.title_label.setText(f"ZEGA :: {filename}")
            except Exception as e:
                QMessageBox.warning(self.window, "ZEGA IO ERROR", f"Read Failed: {e}")

    def save_file(self):
        if self.current_file:
            try:
                content = self.window.editor.toPlainText()
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"ZEGA CORE: Saved {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self.window, "ZEGA WRITE ERROR", str(e))
        else:
            self.save_as()

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self.window, "Save As", "", "Z# Files (*.zs);;All Files (*)")
        if path:
            self.current_file = path
            self.save_file()

    def open_settings_external(self):
        """Triggers system 'Open With' as seen in ZEGA diagnostics"""
        try:
            if platform.system() == 'Windows':
                os.startfile(self.settings_path)
            elif platform.system() == 'Darwin':
                subprocess.call(('open', self.settings_path))
            else:
                subprocess.call(('xdg-open', self.settings_path))
        except Exception:
            QMessageBox.information(self.window, "ZEGA REGISTRY", "Please edit settings.json manually.")

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = ZegaController()
    controller.run()