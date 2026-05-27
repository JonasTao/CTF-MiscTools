"""猪圈密码、核心价值观等 CTF 常见编码"""
import re

# 猪圈密码 (Pigpen / Masonic)
_PIGPEN = {
    "A": "⌈⌉", "B": "⌈⌋", "C": "⌈⌊", "D": "⌈⌈",
    "E": "⌈⌉", "F": "⌈⌋", "G": "⌈⌊", "H": "⌈⌈",
}
# 简化：使用标准 Unicode 区块映射表
_PIGPEN_ENCODE = {}
_PIGPEN_DECODE = {}

# 标准 pigpen 符号分组
_P1 = "ABCD"
_P2 = "EFGHI"
_P3 = "JKLMN"
_P4 = "OPQR"
_P5 = "STUV"
_P6 = "WXYZ"
_SYMS = [
    ["⌈", "⌉", "⌊", "⌋"],
    ["⊏", "⊐", "⊑", "⊒"],
    ["╱", "╲", "╳", "╴"],
    ["◸", "◹", "◺", "◻"],
    ["⬒", "⬓", "⬔", "⬕"],
    ["⬖", "⬗", "⬘", "⬙"],
]

for idx, letters in enumerate([_P1, _P2, _P3, _P4, _P5, _P6]):
    syms = _SYMS[idx % len(_SYMS)]
    for i, ch in enumerate(letters):
        if i < len(syms):
            _PIGPEN_ENCODE[ch] = syms[i % len(syms)]
            _PIGPEN_DECODE[syms[i % len(syms)]] = ch

# 使用更常见的 ASCII 猪圈表示
_PIGPEN_ASCII = {
    "A": "X>", "B": "<X", "C": "X-", "D": "-X",
    "E": ">X", "F": "X<", "G": "-X", "H": "X|",
    "I": "|X", "J": "X^", "K": "^X", "L": "vX",
    "M": "Xv", "N": "<>", "O": "[]", "P": "][",
    "Q": "{}", "R": "}{", "S": "()", "T": ")(",
    "U": "/\\", "V": "\\/", "W": "<>", "X": "><",
    "Y": "8", "Z": "8",
}
_PIGPEN_DECODE_ASCII = {v: k for k, v in _PIGPEN_ASCII.items()}


# 社会主义核心价值观编码
_CORE_VALUES = [
    "富强", "民主", "文明", "和谐", "自由", "平等", "公正", "法治",
    "爱国", "敬业", "诚信", "友善",
]
_CORE_BITS = {}
for i, w in enumerate(_CORE_VALUES):
    _CORE_BITS[w] = format(i, "04b")


class ExtraCipher:
    @staticmethod
    def pigpen_encode(text: str) -> str:
        return " ".join(
            _PIGPEN_ASCII.get(c.upper(), c) for c in text if c.isalpha()
        )

    @staticmethod
    def pigpen_decode(text: str) -> str:
        tokens = re.findall(r"[X<>|\-\^v8\[\]\{\}\(\)/\\]+|.", text)
        out = []
        buf = ""
        for t in text.split():
            if t in _PIGPEN_DECODE_ASCII:
                out.append(_PIGPEN_DECODE_ASCII[t])
            else:
                buf += t
        if buf:
            for k, v in _PIGPEN_DECODE_ASCII.items():
                buf = buf.replace(k, v)
            out.append(buf)
        return "".join(out) if out else text

    @staticmethod
    def _parse_core_words(text: str) -> list:
        """从左到右解析核心价值观词序列"""
        indices = []
        i = 0
        sorted_words = sorted(_CORE_VALUES, key=len, reverse=True)
        while i < len(text):
            matched = False
            for w in sorted_words:
                if text[i:].startswith(w):
                    indices.append(_CORE_VALUES.index(w))
                    i += len(w)
                    matched = True
                    break
            if not matched:
                i += 1
        return indices

    @staticmethod
    def core_values_encode(text: str) -> str:
        """文本 -> 核心价值观（每字节用 12 进制 3 词表示，支持 roundtrip）"""
        out = []
        for c in text:
            v = ord(c)
            d2, rem = divmod(v, 144)
            d1, d0 = divmod(rem, 12)
            out.append(_CORE_VALUES[d2])
            out.append(_CORE_VALUES[d1])
            out.append(_CORE_VALUES[d0])
        return "".join(out)

    @staticmethod
    def core_values_decode(text: str) -> str:
        indices = ExtraCipher._parse_core_words(text)
        chars = []
        for i in range(0, len(indices) - 2, 3):
            v = indices[i] * 144 + indices[i + 1] * 12 + indices[i + 2]
            if v < 256:
                chars.append(chr(v))
        return "".join(chars)
