from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QSpinBox,
    QComboBox, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt

from ui.tool_base import ToolPage
from modules.file.file_tools import FileTools


class FilePage(ToolPage):
    def __init__(self):
        super().__init__("文件分析")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_group)
        
        b_open = QPushButton("选择文件")
        b_open.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        b_open.clicked.connect(self._pick)
        file_layout.addWidget(b_open)

        self.path_label = QLabel("未选择文件")
        self.path_label.setStyleSheet("color: #666; font-style: italic;")
        file_layout.addWidget(self.path_label)
        file_layout.addStretch()
        layout.addWidget(file_group)

        # 参数设置区域
        param_group = QGroupBox("参数设置")
        param_layout = QHBoxLayout(param_group)
        
        param_layout.addWidget(QLabel("strings 最小长度:"))
        self.min_len = QSpinBox()
        self.min_len.setRange(3, 30)
        self.min_len.setValue(4)
        self.min_len.setFixedWidth(80)
        param_layout.addWidget(self.min_len)
        
        param_layout.addWidget(QLabel("XOR 数据长度:"))
        self.xor_limit = QSpinBox()
        self.xor_limit.setRange(128, 2048)
        self.xor_limit.setValue(512)
        self.xor_limit.setFixedWidth(100)
        param_layout.addWidget(self.xor_limit)
        
        param_layout.addWidget(QLabel("重复密钥最大长度:"))
        self.key_len = QSpinBox()
        self.key_len.setRange(2, 16)
        self.key_len.setValue(8)
        self.key_len.setFixedWidth(80)
        param_layout.addWidget(self.key_len)
        
        param_layout.addStretch()
        layout.addWidget(param_group)

        # 输出区域
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        self.out.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.out)

        # 功能按钮区域 - 第一行
        row1 = QHBoxLayout()
        buttons1 = [
            ("文件类型", self._ftype, "#2196F3"),
            ("提取 Strings", self._strings, "#1976D2"),
            ("Hex 预览", self._hex, "#1565C0"),
            ("搜索 Flag", self._flags, "#9C27B0"),
        ]
        for label, fn, color in buttons1:
            b = QPushButton(label)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            b.clicked.connect(fn)
            row1.addWidget(b)
        row1.addStretch()
        layout.addLayout(row1)

        # 功能按钮区域 - 第二行
        row2 = QHBoxLayout()
        buttons2 = [
            ("单字节 XOR", self._xor, "#F44336"),
            ("重复 XOR", self._xor_rep, "#E91E63"),
            ("嵌入扫描", self._binwalk, "#FF9800"),
        ]
        for label, fn, color in buttons2:
            b = QPushButton(label)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            b.clicked.connect(fn)
            row2.addWidget(b)
        
        # 快速操作按钮
        b_clear = QPushButton("清空输出")
        b_clear.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        b_clear.clicked.connect(lambda: self.out.clear())
        row2.addWidget(b_clear)
        
        row2.addStretch()
        layout.addLayout(row2)

        self._path = ""

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*.*)"
        )
        if path:
            self._path = path
            # 只显示文件名部分
            if len(path) > 50:
                self.path_label.setText("..." + path[-47:])
            else:
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
        lines = [f"{i+1}. {line}" for i, line in enumerate(s)]
        self.out.setPlainText("\n".join(lines[:500]) + 
                              (f"\n\n...共 {len(s)} 条，显示前500条" if len(s) > 500 else ""))

    def _hex(self):
        if not self._ensure():
            return
        hex_view = FileTools.file_to_hex(self._path, limit=4096)
        self.out.setPlainText(hex_view)

    def _flags(self):
        if not self._ensure():
            return
        flags = FileTools.search_flag(self._path)
        if flags:
            lines = [f"发现 {len(flags)} 个候选:" ]
            for i, flag in enumerate(flags, 1):
                lines.append(f"{i}. {flag}")
            self.out.setPlainText("\n".join(lines))
        else:
            self.out.setPlainText("未发现 flag 格式字符串")

    def _xor(self):
        if not self._ensure():
            return
        results = FileTools.xor_bruteforce_single(self._path, limit=self.xor_limit.value())
        if results:
            lines = [f"发现 {len(results)} 个候选密钥:" ]
            for k, p in results:
                lines.append(f"Key=0x{k:02X}: {p}")
            self.out.setPlainText("\n".join(lines))
        else:
            self.out.setPlainText("未发现可读明文")

    def _xor_rep(self):
        if not self._ensure():
            return
        results = FileTools.xor_bruteforce_repeating(
            self._path, 
            max_key_len=self.key_len.value(),
            limit=self.xor_limit.value()
        )
        if results:
            lines = [f"发现 {len(results)} 个候选密钥:" ]
            for k, p in results:
                lines.append(f"密钥='{k}': {p}")
            self.out.setPlainText("\n".join(lines))
        else:
            self.out.setPlainText("未发现可读明文")

    def _binwalk(self):
        if not self._ensure():
            return
        hits = FileTools.binwalk_simple(self._path)
        if hits:
            lines = [f"发现 {len(hits)} 个嵌入签名:" ]
            lines.extend(hits)
            self.out.setPlainText("\n".join(lines))
        else:
            self.out.setPlainText("未发现额外嵌入签名")
