from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSpinBox, QLineEdit,
    QPushButton, QWidget,
)

from ui.tool_base import ToolPage
from modules.cipher.classical import ClassicalCipher
from modules.cipher.extra import ExtraCipher


class CipherPage(ToolPage):
    def __init__(self):
        super().__init__("古典密码")
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("密码:"))
        self.algo = QComboBox()
        self.algo.addItems([
            "凯撒", "ROT13", "ROT5", "ROT18", "Atbash", "摩斯电码", "培根",
            "栅栏密码", "维吉尼亚", "仿射", "键盘密码", "A1Z26", "敲击码",
            "猪圈密码", "社会主义核心价值观", "XOR文本", "字频分析",
        ])
        self.algo.currentTextChanged.connect(self._on_algo_change)
        row.addWidget(self.algo, 1)
        layout.addLayout(row)

        param_row = QHBoxLayout()
        self.param_label = QLabel("偏移/栏数:")
        self.param_spin = QSpinBox()
        self.param_spin.setRange(1, 25)
        self.param_spin.setValue(3)
        self.key_label = QLabel("密钥:")
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("维吉尼亚密钥 / XOR密钥 / 仿射 a,b 如 5,8")
        param_row.addWidget(self.param_label)
        param_row.addWidget(self.param_spin)
        param_row.addWidget(self.key_label)
        param_row.addWidget(self.key_edit, 1)
        layout.addLayout(param_row)

        split = QHBoxLayout()
        self.inp = self.input_box()
        self.out = self.output_box()
        split.addWidget(self._wrap("明文/密文", self.inp))
        split.addWidget(self._wrap("结果", self.out))
        layout.addLayout(split)
        layout.addLayout(self.io_toolbar(self.inp, self.out))

        btns = QHBoxLayout()
        for label, fn in [
            ("加密 →", lambda: self._run(False)),
            ("← 解密", lambda: self._run(True)),
            ("暴力凯撒(1-25)", self._brute_caesar),
            ("仿射暴力(a,b)", self._brute_affine),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            btns.addWidget(b)
        btns.addStretch()
        layout.addLayout(btns)

    def _wrap(self, title, widget):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(QLabel(title))
        v.addWidget(widget)
        return w

    def _on_algo_change(self, name):
        self.key_label.setVisible(
            name in ("维吉尼亚", "XOR文本", "仿射", "猪圈密码")
        )
        self.key_edit.setVisible(
            name in ("维吉尼亚", "XOR文本", "仿射", "猪圈密码")
        )
        self.param_label.setVisible(name in ("凯撒", "栅栏密码"))
        self.param_spin.setVisible(name in ("凯撒", "栅栏密码"))

    def _run(self, decode=False):
        text = self.inp.toPlainText()
        algo = self.algo.currentText()
        shift = self.param_spin.value()
        key = self.key_edit.text()
        try:
            if algo == "凯撒":
                r = ClassicalCipher.caesar(text, shift, decode)
            elif algo == "ROT13":
                r = ClassicalCipher.rot13(text)
            elif algo == "ROT5":
                r = ClassicalCipher.rot5(text)
            elif algo == "ROT18":
                r = ClassicalCipher.rot18(text)
            elif algo == "Atbash":
                r = ClassicalCipher.atbash(text)
            elif algo == "摩斯电码":
                r = (
                    ClassicalCipher.morse_decode(text)
                    if decode
                    else ClassicalCipher.morse_encode(text)
                )
            elif algo == "培根":
                r = (
                    ClassicalCipher.bacon_decode(text)
                    if decode
                    else ClassicalCipher.bacon_encode(text)
                )
            elif algo == "栅栏密码":
                r = (
                    ClassicalCipher.rail_fence_decode(text, shift)
                    if decode
                    else ClassicalCipher.rail_fence_encode(text, shift)
                )
            elif algo == "维吉尼亚":
                r = ClassicalCipher.vigenere(text, key, decode)
            elif algo == "仿射":
                parts = key.replace("，", ",").split(",")
                a = int(parts[0].strip()) if parts and parts[0].strip() else 5
                b = int(parts[1].strip()) if len(parts) > 1 else 8
                r = (
                    ClassicalCipher.affine_decode(text, a, b)
                    if decode
                    else ClassicalCipher.affine_encode(text, a, b)
                )
            elif algo == "键盘密码":
                r = (
                    ClassicalCipher.keyboard_cipher_decode(text)
                    if decode
                    else ClassicalCipher.keyboard_cipher_encode(text)
                )
            elif algo == "A1Z26":
                r = (
                    ClassicalCipher.a1z26_decode(text)
                    if decode
                    else ClassicalCipher.a1z26_encode(text)
                )
            elif algo == "敲击码":
                r = (
                    ClassicalCipher.tap_code_decode(text)
                    if decode
                    else ClassicalCipher.tap_code_encode(text)
                )
            elif algo == "猪圈密码":
                r = (
                    ExtraCipher.pigpen_decode(text)
                    if decode
                    else ExtraCipher.pigpen_encode(text)
                )
            elif algo == "社会主义核心价值观":
                r = (
                    ExtraCipher.core_values_decode(text)
                    if decode
                    else ExtraCipher.core_values_encode(text)
                )
            elif algo == "XOR文本":
                r = ClassicalCipher.xor_text(text, key or "key")
            elif algo == "字频分析":
                r = ClassicalCipher.frequency_analysis(text)
            else:
                r = "未实现"
            self.out.setPlainText(r)
        except Exception as e:
            self.show_error(self, str(e))

    def _brute_caesar(self):
        text = self.inp.toPlainText()
        lines = [
            f"[{i:2d}] {ClassicalCipher.caesar(text, i, True)}"
            for i in range(1, 26)
        ]
        self.out.setPlainText("\n".join(lines))

    def _brute_affine(self):
        text = self.inp.toPlainText()
        valid_a = [a for a in range(1, 26) if ClassicalCipher._mod_inv(a, 26)]
        lines = []
        for a in valid_a:
            for b in range(26):
                try:
                    dec = ClassicalCipher.affine_decode(text, a, b)
                    lines.append(f"a={a}, b={b}: {dec}")
                except Exception:
                    pass
        self.out.setPlainText("\n".join(lines[:100]) + (
            f"\n\n...共 {len(lines)} 组" if len(lines) > 100 else ""
        ))
