"""可爱粉色主题 QSS"""

CUTE_STYLE = """
QMainWindow, QWidget {
    background-color: #FFF8FC;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #5C4A5E;
}

QListWidget {
    background-color: #FFE8F3;
    border: 2px solid #FFB8D9;
    border-radius: 14px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    padding: 12px 16px;
    border-radius: 10px;
    margin: 3px 0;
}

QListWidget::item:selected {
    background-color: #FF9EC7;
    color: white;
    font-weight: bold;
}

QListWidget::item:hover:!selected {
    background-color: #FFD4E8;
}

QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #FFFFFF;
    border: 2px solid #FFD0E8;
    border-radius: 10px;
    padding: 8px;
    selection-background-color: #FF9EC7;
}

QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {
    border-color: #FF7EB8;
}

QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB8D9, stop:1 #FF8EC4);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 8px 18px;
    font-weight: bold;
    min-height: 28px;
}

QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFC8E3, stop:1 #FF9ED0);
}

QPushButton:pressed {
    background-color: #FF6EAE;
}

QPushButton#secondaryBtn {
    background-color: #E8D4FF;
    color: #6B4A8A;
}

QComboBox, QSpinBox {
    background-color: white;
    border: 2px solid #FFD0E8;
    border-radius: 8px;
    padding: 4px 8px;
    min-height: 26px;
}

QTabWidget::pane {
    border: 2px solid #FFD0E8;
    border-radius: 12px;
    background: white;
    top: -1px;
}

QTabBar::tab {
    background: #FFE8F3;
    border: 2px solid #FFD0E8;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 8px 16px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background: white;
    color: #D44A8A;
    font-weight: bold;
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: bold;
    color: #D44A8A;
}

QLabel#subtitleLabel {
    color: #A87A9A;
    font-size: 12px;
}

QGroupBox {
    border: 2px dashed #FFD0E8;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #C45A8A;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QStatusBar {
    background: #FFE8F3;
    color: #A87A9A;
}
"""
