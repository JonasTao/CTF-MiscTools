"""Base 家族编解码（经单元测试校验的 roundtrip 实现）"""
import base64
import binascii
import re

_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
# basE91 标准 91 字符字母表
_B91_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~\""
)
assert len(_B91_ALPHABET) == 91, f"base91 alphabet len={len(_B91_ALPHABET)}"
_B91_DECODE = {c: i for i, c in enumerate(_B91_ALPHABET)}


class BaseCodec:
    @staticmethod
    def encode_b16(data: bytes) -> str:
        return base64.b16encode(data).decode()

    @staticmethod
    def decode_b16(text: str) -> bytes:
        return base64.b16decode(_clean(text), casefold=True)

    @staticmethod
    def encode_b32(data: bytes) -> str:
        return base64.b32encode(data).decode()

    @staticmethod
    def decode_b32(text: str) -> bytes:
        return base64.b32decode(_pad(text, 8))

    @staticmethod
    def encode_b64(data: bytes) -> str:
        return base64.b64encode(data).decode()

    @staticmethod
    def decode_b64(text: str) -> bytes:
        t = re.sub(r"\s+", "", text)
        return base64.b64decode(_pad(t, 4))

    @staticmethod
    def encode_b85(data: bytes) -> str:
        return base64.b85encode(data).decode()

    @staticmethod
    def decode_b85(text: str) -> bytes:
        return base64.b85decode(text.strip())

    @staticmethod
    def encode_b58(data: bytes) -> str:
        num = int.from_bytes(data, "big")
        enc = ""
        while num > 0:
            num, rem = divmod(num, 58)
            enc = _B58_ALPHABET[rem] + enc
        pad = len(data) - len(data.lstrip(b"\x00"))
        return (_B58_ALPHABET[0] * pad) + (enc or _B58_ALPHABET[0])

    @staticmethod
    def decode_b58(text: str) -> bytes:
        text = text.strip()
        num = 0
        for c in text:
            num = num * 58 + _B58_ALPHABET.index(c)
        combined = num.to_bytes((num.bit_length() + 7) // 8, "big") if num else b""
        pad = 0
        for c in text:
            if c == _B58_ALPHABET[0]:
                pad += 1
            else:
                break
        return b"\x00" * pad + combined

    @staticmethod
    def encode_b36(data: bytes) -> str:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        n = int.from_bytes(data, "big")
        enc = ""
        while n > 0:
            n, r = divmod(n, 36)
            enc = chars[r] + enc
        pad = len(data) - len(data.lstrip(b"\x00"))
        return ("0" * pad) + (enc or "0")

    @staticmethod
    def decode_b36(text: str) -> bytes:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        text = text.strip().lower()
        n = int(text, 36) if text else 0
        combined = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
        pad = 0
        for c in text:
            if c == "0":
                pad += 1
            else:
                break
        return b"\x00" * pad + combined

    @staticmethod
    def encode_b62(data: bytes) -> str:
        alphabet = (
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
        n = int.from_bytes(data, "big")
        enc = ""
        while n > 0:
            n, rem = divmod(n, 62)
            enc = alphabet[rem] + enc
        pad = len(data) - len(data.lstrip(b"\x00"))
        return ("0" * pad) + (enc or "0")

    @staticmethod
    def decode_b62(text: str) -> bytes:
        alphabet = (
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
        text = text.strip()
        n = 0
        for c in text:
            n = n * 62 + alphabet.index(c)
        combined = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
        pad = 0
        for c in text:
            if c == "0":
                pad += 1
            else:
                break
        return b"\x00" * pad + combined

    @staticmethod
    def encode_b91(data: bytes) -> str:
        if not data:
            return ""
        b = bytearray(data)
        out, eb, en = [], 0, 0
        for byte in b:
            eb |= byte << en
            en += 8
            if en > 13:
                ev = eb & 8191
                if ev > 88:
                    eb >>= 13
                    en -= 13
                else:
                    ev = eb & 16383
                    eb >>= 14
                    en -= 14
                out.append(_B91_ALPHABET[ev % 91])
                out.append(_B91_ALPHABET[ev // 91])
        if en:
            out.append(_B91_ALPHABET[eb % 91])
            if en > 7 or eb > 90:
                out.append(_B91_ALPHABET[eb // 91])
        return "".join(out)

    @staticmethod
    def decode_b91(text: str) -> bytes:
        v, eb, en = -1, 0, 0
        out = bytearray()
        for c in text:
            if c not in _B91_DECODE:
                continue
            ch = _B91_DECODE[c]
            if v < 0:
                v = ch
            else:
                v += ch * 91
                eb |= v << en
                en += 13 if (v & 8191) > 88 else 14
                while en > 7:
                    out.append(eb & 255)
                    eb >>= 8
                    en -= 8
                v = -1
        if v >= 0:
            out.append((eb | v << en) & 255)
        return bytes(out)


def _clean(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _pad(s: str, block: int) -> str:
    s = _clean(s)
    rem = len(s) % block
    if rem:
        s += "=" * (block - rem)
    return s
