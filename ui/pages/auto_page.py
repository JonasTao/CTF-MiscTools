from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from ui.tool_base import ToolPage
from modules.auto.smart_decode import SmartDecoder


class AutoPage(ToolPage):
    def __init__(self):
        super().__init__("智能解码")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("类似 Ciphey：自动尝试 Base64/Hex/ROT/Caesar/Morse 等链式解码"))
        self.inp = self.input_box("粘贴可疑密文...")
        self.out = self.output_box()
        layout.addWidget(self.inp)
        layout.addWidget(self.out)
        layout.addLayout(self.io_toolbar(self.inp, self.out))

        row = QHBoxLayout()
        b = QPushButton("开始智能爆破")
        b.clicked.connect(self._run)
        row.addWidget(b)
        c = QPushButton("清空")
        c.clicked.connect(lambda: (self.inp.clear(), self.out.clear()))
        row.addWidget(c)
        row.addStretch()
        layout.addLayout(row)

    def _run(self):
        text = self.inp.toPlainText().strip()
        if not text:
            return
        results = SmartDecoder.try_all(text)
        if not results:
            self.out.setPlainText("未能识别有效解码路径，请尝试手动工具或检查输入。")
            return
        lines = []
        for score, chain, result in results:
            lines.append(f"得分 {score:.1f} | {chain}")
            lines.append(f"  → {result[:300]}{'...' if len(result)>300 else ''}")
            lines.append("")
        self.out.setPlainText("\n".join(lines))
