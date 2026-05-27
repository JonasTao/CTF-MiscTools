from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QSpinBox,
)

from ui.tool_base import ToolPage
from modules.file.file_tools import FileTools


class FilePage(ToolPage):
    def __init__(self):
        super().__init__("文件分析")
        layout = QVBoxLayout(self)
        self.path_label = QLabel("未选择文件")
        layout.addWidget(self.path_label)

        row = QHBoxLayout()
        b_open = QPushButton("选择文件")
        b_open.clicked.connect(self._pick)
        row.addWidget(b_open)
        row.addWidget(QLabel("strings 最小长度:"))
        self.min_len = QSpinBox()
        self.min_len.setRange(3, 20)
        self.min_len.setValue(4)
        row.addWidget(self.min_len)
        row.addStretch()
        layout.addLayout(row)

        self.out = self.output_box()
        layout.addWidget(self.out)

        row2 = QHBoxLayout()
        for label, fn in [
            ("文件类型", self._ftype),
            ("提取 Strings", self._strings),
            ("Hex 预览", self._hex),
            ("搜索 Flag", self._flags),
            ("单字节 XOR", self._xor),
            ("重复 XOR", self._xor_rep),
            ("嵌入扫描", self._binwalk),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            row2.addWidget(b)
        layout.addLayout(row2)
        self._path = ""

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if path:
            self._path = path
            self.path_label.setText(path)

    def _ensure(self):
        if not self._path:
            self.show_error(self, "请先选择文件")
            return False
        return True

    def _ftype(self):
        if not self._ensure():
            return
        types = FileTools.detect_type(self._path)
        self.out.setPlainText("\n".join(types))

    def _strings(self):
        if not self._ensure():
            return
        s = FileTools.extract_strings(self._path, self.min_len.value())
        self.out.setPlainText("\n".join(s[:500]) + (f"\n\n...共 {len(s)} 条" if len(s) > 500 else ""))

    def _hex(self):
        if not self._ensure():
            return
        self.out.setPlainText(FileTools.file_to_hex(self._path))

    def _flags(self):
        if not self._ensure():
            return
        flags = FileTools.search_flag(self._path)
        self.out.setPlainText("\n".join(flags) if flags else "未发现 flag 格式字符串")

    def _xor(self):
        if not self._ensure():
            return
        results = FileTools.xor_bruteforce_single(self._path)
        lines = [f"Key=0x{k:02X}: {p}" for k, p in results]
        self.out.setPlainText("\n".join(lines) if lines else "未发现可读明文")

    def _xor_rep(self):
        if not self._ensure():
            return
        results = FileTools.xor_bruteforce_repeating(self._path)
        lines = [f"密钥={k}: {p}" for k, p in results]
        self.out.setPlainText("\n".join(lines) if lines else "未发现可读明文")

    def _binwalk(self):
        if not self._ensure():
            return
        hits = FileTools.binwalk_simple(self._path)
        self.out.setPlainText("\n".join(hits) if hits else "未发现额外嵌入签名")
