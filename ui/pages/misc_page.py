from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog,
)

from ui.tool_base import ToolPage
from modules.misc.utilities import MiscUtils


class MiscPage(ToolPage):
    def __init__(self):
        super().__init__("杂项工具")
        layout = QVBoxLayout(self)

        # 进制
        g1 = __import__("PyQt5.QtWidgets", fromlist=["QGroupBox"]).QGroupBox("进制转换")
        gl = QVBoxLayout(g1)
        row = QHBoxLayout()
        self.radix_val = __import__("PyQt5.QtWidgets", fromlist=["QLineEdit"]).QLineEdit()
        self.radix_val.setPlaceholderText("数值")
        self.from_base = QSpinBox()
        self.from_base.setRange(2, 36)
        self.from_base.setValue(10)
        self.to_base = QSpinBox()
        self.to_base.setRange(2, 36)
        self.to_base.setValue(16)
        row.addWidget(self.radix_val, 1)
        row.addWidget(QLabel("从"))
        row.addWidget(self.from_base)
        row.addWidget(QLabel("到"))
        row.addWidget(self.to_base)
        b = QPushButton("转换")
        b.clicked.connect(self._radix)
        row.addWidget(b)
        gl.addLayout(row)
        layout.addWidget(g1)

        # QR
        g2 = __import__("PyQt5.QtWidgets", fromlist=["QGroupBox"]).QGroupBox("二维码")
        gl2 = QVBoxLayout(g2)
        self.qr_text = __import__("PyQt5.QtWidgets", fromlist=["QLineEdit"]).QLineEdit()
        self.qr_text.setPlaceholderText("生成 QR 的内容")
        gl2.addWidget(self.qr_text)
        qr_row = QHBoxLayout()
        b_gen = QPushButton("生成 QR 图片")
        b_gen.clicked.connect(self._qr_gen)
        b_dec = QPushButton("解码 QR 图片")
        b_dec.clicked.connect(self._qr_dec)
        qr_row.addWidget(b_gen)
        qr_row.addWidget(b_dec)
        gl2.addLayout(qr_row)
        layout.addWidget(g2)

        self.inp = self.input_box("Flag 检测 / 其他文本")
        self.out = self.output_box()
        layout.addWidget(self.inp)
        layout.addWidget(self.out)
        layout.addLayout(self.io_toolbar(self.inp, self.out))

        row = QHBoxLayout()
        b_flag = QPushButton("提取 Flag 格式")
        b_flag.clicked.connect(self._flags)
        row.addWidget(b_flag)
        row.addStretch()
        layout.addLayout(row)

    def _radix(self):
        try:
            v = self.radix_val.text()
            r = MiscUtils.radix_convert(v, self.from_base.value(), self.to_base.value())
            self.out.setPlainText(r)
        except Exception as e:
            self.show_error(self, str(e))

    def _qr_gen(self):
        text = self.qr_text.text() or self.inp.toPlainText()
        path, _ = QFileDialog.getSaveFileName(self, "保存 QR", "qr.png", "PNG (*.png)")
        if not path:
            return
        try:
            MiscUtils.qr_encode(text, path)
            self.out.setPlainText(f"已保存: {path}")
        except Exception as e:
            self.show_error(self, str(e))

    def _qr_dec(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 QR 图片")
        if not path:
            return
        try:
            self.out.setPlainText(MiscUtils.qr_decode(path))
        except Exception as e:
            self.show_error(self, str(e))

    def _flags(self):
        text = self.inp.toPlainText()
        flags = MiscUtils.check_flag(text)
        self.out.setPlainText("\n".join(flags) if flags else "未匹配常见 flag 格式")
