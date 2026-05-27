from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QPushButton

from ui.tool_base import ToolPage
from modules.encoding.base_codec import BaseCodec
from modules.encoding.text_codec import TextCodec
from modules.encoding.esoteric import EsotericCodec


class EncodingPage(ToolPage):
    def __init__(self):
        super().__init__("编解码")
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("算法:"))
        self.algo = QComboBox()
        self.algo.addItems([
            "Base16", "Base32", "Base36", "Base58", "Base62", "Base64",
            "Base85", "Base91",
            "Hex", "URL", "URL(全编码)", "HTML", "Unicode转义",
            "ASCII十进制", "ASCII二进制", "ASCII八进制",
            "Quoted-Printable", "UUencode", "Shellcode", "XXencode",
            "ROT47", "Brainfuck执行", "Ook→Brainfuck", "文本→Brainfuck",
        ])
        row.addWidget(self.algo, 1)
        layout.addLayout(row)

        split = QHBoxLayout()
        self.inp = self.input_box()
        self.out = self.output_box()
        left = QVBoxLayout()
        right = QVBoxLayout()
        left.addWidget(QLabel("输入"))
        left.addWidget(self.inp)
        right.addWidget(QLabel("输出"))
        right.addWidget(self.out)
        split.addLayout(left)
        split.addLayout(right)
        layout.addLayout(split)
        layout.addLayout(self.io_toolbar(self.inp, self.out))

        btns = QHBoxLayout()
        for label, fn in [
            ("编码/加密 →", self._encode),
            ("← 解码/解密", self._decode),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            btns.addWidget(b)
        btns.addStretch()
        layout.addLayout(btns)

    def _get_text_bytes(self):
        t = self.inp.toPlainText()
        return t, t.encode("utf-8", errors="replace")

    def _encode(self):
        self._run(True)

    def _decode(self):
        self._run(False)

    def _run(self, encode: bool):
        text, data = self._get_text_bytes()
        algo = self.algo.currentText()
        try:
            self.out.setPlainText(self._exec(algo, text, data, encode))
        except Exception as e:
            self.show_error(self, str(e))

    def _exec(self, algo, text, data, encode=True):
        bc, tc, es = BaseCodec(), TextCodec(), EsotericCodec()
        ops = {
            "Base16": (bc.encode_b16, bc.decode_b16),
            "Base32": (bc.encode_b32, bc.decode_b32),
            "Base36": (bc.encode_b36, bc.decode_b36),
            "Base58": (bc.encode_b58, bc.decode_b58),
            "Base62": (bc.encode_b62, bc.decode_b62),
            "Base64": (bc.encode_b64, bc.decode_b64),
            "Base85": (bc.encode_b85, bc.decode_b85),
            "Base91": (bc.encode_b91, bc.decode_b91),
            "Hex": (tc.hex_encode, tc.hex_decode),
            "URL": (tc.url_encode, tc.url_decode),
            "URL(全编码)": (tc.url_encode_all, tc.url_decode),
            "HTML": (tc.html_encode, tc.html_decode),
            "Unicode转义": (tc.unicode_escape_encode, tc.unicode_escape_decode),
            "ASCII十进制": (tc.ascii_decimal_encode, tc.ascii_decimal_decode),
            "ASCII二进制": (tc.ascii_binary_encode, tc.ascii_binary_decode),
            "ASCII八进制": (tc.ascii_octal_encode, tc.ascii_octal_decode),
            "Quoted-Printable": (tc.quoted_printable_encode, tc.quoted_printable_decode),
            "UUencode": (tc.uu_encode, tc.uu_decode),
            "Shellcode": (tc.shellcode_encode, tc.shellcode_decode),
            "XXencode": (tc.xxencode, tc.xxdecode),
        }
        if algo in ops:
            enc_fn, dec_fn = ops[algo]
            if encode:
                text_algos = {
                    "URL", "URL(全编码)", "HTML", "Unicode转义",
                    "ASCII十进制", "ASCII二进制", "ASCII八进制",
                    "Quoted-Printable", "Shellcode",
                }
                r = enc_fn(text if algo in text_algos else data)
            else:
                r = dec_fn(text)
            if isinstance(r, bytes):
                return self.bytes_display(r)
            return r
        if algo == "ROT47":
            return es.rot47(text)
        if algo == "Brainfuck执行":
            return es.brainfuck_run(text)
        if algo == "Ook→Brainfuck":
            bf = es.ook_to_brainfuck(text)
            return f"Brainfuck:\n{bf}\n\n执行结果:\n{es.brainfuck_run(bf)}"
        if algo == "文本→Brainfuck":
            return es.text_to_brainfuck(text)
        raise ValueError("未知算法")
