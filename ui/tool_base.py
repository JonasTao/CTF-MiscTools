"""工具页基类与通用 IO 组件"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QMessageBox, QApplication,
)


class ToolPage(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title

    def input_box(self, placeholder="输入密文/原文..."):
        te = QTextEdit()
        te.setPlaceholderText(placeholder)
        te.setMinimumHeight(100)
        return te

    def output_box(self, placeholder="输出结果..."):
        te = QTextEdit()
        te.setPlaceholderText(placeholder)
        te.setMinimumHeight(100)
        return te

    def io_toolbar(self, inp: QTextEdit, out: QTextEdit) -> QHBoxLayout:
        """输入/输出快捷操作栏"""
        row = QHBoxLayout()

        def copy_out():
            QApplication.clipboard().setText(out.toPlainText())

        def copy_in():
            QApplication.clipboard().setText(inp.toPlainText())

        def swap():
            inp.setPlainText(out.toPlainText())

        def clear_all():
            inp.clear()
            out.clear()

        for label, fn in [
            ("复制输出", copy_out),
            ("复制输入", copy_in),
            ("输出→输入", swap),
            ("清空", clear_all),
        ]:
            b = QPushButton(label)
            b.setObjectName("secondaryBtn")
            b.clicked.connect(fn)
            row.addWidget(b)
        row.addStretch()
        return row

    @staticmethod
    def show_error(parent, msg: str):
        QMessageBox.warning(parent, "提示", msg)

    @staticmethod
    def bytes_display(data: bytes) -> str:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")
