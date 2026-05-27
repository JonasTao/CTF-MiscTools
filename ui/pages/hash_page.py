from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from ui.tool_base import ToolPage
from modules.hash.hash_tools import HashTools


class HashPage(ToolPage):
    def __init__(self):
        super().__init__("哈希")
        layout = QVBoxLayout(self)
        self.inp = self.input_box("输入文本或粘贴哈希值...")
        self.out = self.output_box()
        layout.addWidget(QLabel("输入"))
        layout.addWidget(self.inp)
        layout.addWidget(QLabel("输出"))
        layout.addWidget(self.out)
        layout.addLayout(self.io_toolbar(self.inp, self.out))

        row = QHBoxLayout()
        for label, fn in [
            ("计算全部哈希", self._compute),
            ("识别哈希类型", self._identify),
            ("HMAC-SHA256", self._hmac),
            ("清空", self._clear),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            row.addWidget(b)
        row.addStretch()
        layout.addLayout(row)

        self.key_inp = __import__("PyQt5.QtWidgets", fromlist=["QLineEdit"]).QLineEdit()
        self.key_inp.setPlaceholderText("HMAC 密钥")
        layout.addWidget(self.key_inp)

    def _compute(self):
        text = self.inp.toPlainText()
        results = HashTools.compute_all(text)
        lines = [f"{k}: {v}" for k, v in results.items()]
        self.out.setPlainText("\n".join(lines))

    def _identify(self):
        text = self.inp.toPlainText().strip()
        types = HashTools.identify(text)
        self.out.setPlainText("可能类型:\n" + "\n".join(f"  • {t}" for t in types))

    def _hmac(self):
        text = self.inp.toPlainText()
        key = self.key_inp.text().encode()
        r = HashTools.hmac_sha256(text.encode(), key)
        self.out.setPlainText(f"HMAC-SHA256: {r}")

    def _clear(self):
        self.inp.clear()
        self.out.clear()
