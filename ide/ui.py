import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFrame, QPushButton, QLabel, QTreeView, 
                             QSplitter, QDialog, QScrollBar)
from PyQt6.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont, 
                         QPainter, QFileSystemModel, QTextBlockFormat)
from PyQt6.QtCore import Qt, QRegularExpression, QRect, QSize

class ZegaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, keywords):
        super().__init__(parent)
        self.rules = []
        if keywords:
            tiers = keywords.get("tiers", {})
            for tier in tiers.values():
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(tier["color"]))
                fmt.setFontWeight(QFont.Weight.Bold)
                for cmd in tier["commands"]:
                    pattern = QRegularExpression(fr"\b{cmd}\b")
                    self.rules.append((pattern, fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class ZegaSplash(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(500, 320)
        self.setStyleSheet("background-color: #050505; border: 2px solid #58f01b;")
        layout = QVBoxLayout(self)
        title = QLabel("ZEGA CORE ENGINE")
        title.setStyleSheet("color: #58f01b; font-family: 'Comic Sans MS'; font-size: 26px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        ver = QLabel("v2.0.0.6 STABLE :: BOOTLOADER")
        ver.setStyleSheet("color: #666; font-family: 'Comic Sans MS'; font-size: 10px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)
        layout.addStretch()

        self.btn_new = QPushButton("NEW PROJECT")
        self.btn_open = QPushButton("OPEN PROJECT")
        for b in [self.btn_new, self.btn_open]:
            b.setFixedSize(350, 45)
            b.setStyleSheet("QPushButton { background-color: #111; color: #58f01b; font-family: 'Comic Sans MS'; font-weight: bold; border: 1px solid #333; } QPushButton:hover { background-color: #58f01b; color: black; }")
            layout.addWidget(b, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class ZegaEditor(QTextEdit):
    def __init__(self, keywords, settings):
        super().__init__()
        self.settings = settings
        self.line_number_area = LineNumberArea(self)
        self.apply_settings()
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.highlighter = ZegaHighlighter(self.document(), keywords)
        
        self.setStyleSheet("""
            QTextEdit {
                background-color: #050505;
                color: #ffffff;
                border: none;
                padding-left: 10px;
                selection-background-color: #58f01b;
                selection-color: #000;
            }
        """)
        
        self.document().blockCountChanged.connect(self.update_line_number_area_width)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)
        self.textChanged.connect(self.line_number_area.update)
        self.update_line_number_area_width()

    def apply_settings(self):
        size = self.settings.get("font_size", 13)
        style_type = self.settings.get("type", "regular").lower()
        theme = self.settings.get("theme", "system").lower()

        font = QFont("Comic Sans MS", size)
        
        if style_type == "bold":
            font.setBold(True)
        elif style_type == "italics":
            font.setItalic(True)
        
        self.setFont(font)

        if theme == "dyslexic":
            fmt = QTextBlockFormat()
            fmt.setLineHeight(150, 1) 
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.Document)
            cursor.mergeBlockFormat(fmt)

    def line_number_area_width(self):
        digits = len(str(max(1, self.document().blockCount())))
        return 25 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#080808"))
        block = self.document().begin()
        block_number = block.blockNumber()
        top = int(self.viewportMargins().top())
        bottom = top + int(self.viewport().height())
        
        painter.setFont(QFont("Comic Sans MS", 10))
        
        while block.isValid() and top <= bottom:
            if block.isVisible():
                number = str(block_number + 1)
                painter.setPen(QColor("#58f01b" if self.textCursor().blockNumber() == block_number else "#444"))
                painter.drawText(0, top, self.line_number_area.width() - 8, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top += int(self.document().documentLayout().blockBoundingRect(block).height())
            block_number += 1

class ZegaUI(QMainWindow):
    def __init__(self, keywords, settings):
        super().__init__()
        self.keywords = keywords
        self.settings = settings
        self.setWindowTitle("ZEGA Z# IDE - v2.0.0.6 [STABLE]")
        self.resize(1400, 900)
        self.init_interface()

    def init_interface(self):
        self.setStyleSheet("background-color: #050505; color: white; font-family: 'Comic Sans MS';")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ZEGA Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(65)
        sidebar.setStyleSheet("background-color: #0a0a0a; border-right: 1px solid #1a1a1a;")
        s_layout = QVBoxLayout(sidebar)
        self.btns = {}
        for icon in ["Z", "📂", "🚀", "🛠️", "⚙️"]:
            btn = QPushButton(icon)
            btn.setFixedSize(55, 55)
            btn.setStyleSheet("QPushButton { background: transparent; color: #444; font-size: 22px; border: none; } QPushButton:hover { color: #58f01b; }")
            s_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)
            self.btns[icon] = btn
        s_layout.addStretch()
        layout.addWidget(sidebar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1a1a1a; width: 1px; }")

        # File Explorer
        self.explorer = QTreeView()
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        self.explorer.setModel(self.model)
        self.explorer.setRootIndex(self.model.index(os.getcwd()))
        self.explorer.setHeaderHidden(True)
        for i in range(1, 4): self.explorer.hideColumn(i)
        self.explorer.setStyleSheet("QTreeView { background-color: #080808; border: none; color: #888; font-family: 'Comic Sans MS'; font-size: 13px; } QTreeView::item:hover { color: #58f01b; }")
        splitter.addWidget(self.explorer)

        # Editor Area
        editor_container = QWidget()
        e_layout = QVBoxLayout(editor_container)
        e_layout.setContentsMargins(0, 0, 0, 0)
        e_layout.setSpacing(0)

        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(40)
        self.header_frame.setStyleSheet("background-color: #0a0a0a; border-bottom: 1px solid #1a1a1a;")
        h_layout = QHBoxLayout(self.header_frame)
        self.title_label = QLabel("ZEGA :: SYSTEM_READY")
        self.title_label.setStyleSheet("color: #58f01b; font-size: 11px; font-weight: bold;")
        h_layout.addWidget(self.title_label)
        e_layout.addWidget(self.header_frame)

        self.editor = ZegaEditor(self.keywords, self.settings)
        e_layout.addWidget(self.editor)

        footer = QFrame()
        footer.setFixedHeight(30)
        footer.setStyleSheet("background-color: #0a0a0a; border-top: 1px solid #1a1a1a;")
        f_layout = QHBoxLayout(footer)
        status = QLabel(f"● THEME: {self.settings.get('theme', 'system').upper()} | MODE: {self.settings.get('type', 'regular').upper()}")
        status.setStyleSheet("color: #58f01b; font-size: 10px; font-weight: bold;")
        f_layout.addWidget(status)
        e_layout.addWidget(footer)

        splitter.addWidget(editor_container)
        splitter.setSizes([250, 1150])
        layout.addWidget(splitter)