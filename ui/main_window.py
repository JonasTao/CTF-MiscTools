"""主窗口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QStatusBar,
)

from ui.styles import CUTE_STYLE
from ui.mascot_widget import MascotWidget
from ui.pages.encoding_page import EncodingPage
from ui.pages.cipher_page import CipherPage
from ui.pages.hash_page import HashPage
from ui.pages.file_page import FilePage
from ui.pages.stego_page import StegoPage
from ui.pages.auto_page import AutoPage
from ui.pages.misc_page import MiscPage


NAV_ITEMS = [
    ("🔤", "编解码", EncodingPage),
    ("🔐", "古典密码", CipherPage),
    ("#️⃣", "哈希工具", HashPage),
    ("📁", "文件分析", FilePage),
    ("🖼️", "隐写分析", StegoPage),
    ("🤖", "智能解码", AutoPage),
    ("🧰", "杂项工具", MiscPage),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTF Misc 牛马工具箱 🐮🐴")
        self.setMinimumSize(1050, 720)
        self.resize(1180, 780)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(16)
        root.setContentsMargins(16, 16, 16, 16)

        # 左侧导航 + 牛马
        left = QVBoxLayout()
        title = QLabel("牛马 Misc 箱")
        title.setObjectName("titleLabel")
        sub = QLabel("CTF 杂项全能打工工具")
        sub.setObjectName("subtitleLabel")
        left.addWidget(title)
        left.addWidget(sub)

        self.mascot = MascotWidget()
        left.addWidget(self.mascot, 0, Qt.AlignHCenter)

        self.nav = QListWidget()
        self.nav.setFixedWidth(200)
        for icon, name, _ in NAV_ITEMS:
            item = QListWidgetItem(f" {icon}  {name}")
            self.nav.addItem(item)
        self.nav.setCurrentRow(0)
        left.addWidget(self.nav)
        root.addLayout(left)

        # 右侧内容
        right = QVBoxLayout()
        self.stack = QStackedWidget()
        for _, _, page_cls in NAV_ITEMS:
            self.stack.addWidget(page_cls())
        right.addWidget(self.stack)
        root.addLayout(right, 1)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("牛马已就绪 — 选一个工具开始打工吧!")

        self.setStyleSheet(CUTE_STYLE)
