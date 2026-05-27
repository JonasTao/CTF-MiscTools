"""文本类编解码"""
import binascii
import html
import re
import urllib.parse
import codecs


class TextCodec:
    @staticmethod
    def hex_encode(data: bytes) -> str:
        return binascii.hexlify(data).decode()

    @staticmethod
    def hex_decode(text: str) -> bytes:
        t = re.sub(r"[^0-9a-fA-F]", "", text)
        if len(t) % 2:
            t = "0" + t
        return binascii.unhexlify(t)

    @staticmethod
    def url_encode(s: str) -> str:
        return urllib.parse.quote(s)

    @staticmethod
    def url_decode(s: str) -> str:
        return urllib.parse.unquote(s)

    @staticmethod
    def url_encode_all(s: str) -> str:
        return urllib.parse.quote(s, safe="")

    @staticmethod
    def html_encode(s: str) -> str:
        return html.escape(s)

    @staticmethod
    def html_decode(s: str) -> str:
        return html.unescape(s)

    @staticmethod
    def unicode_escape_encode(s: str) -> str:
        return s.encode("unicode_escape").decode()

    @staticmethod
    def unicode_escape_decode(s: str) -> str:
        return codecs.decode(s, "unicode_escape")

    @staticmethod
    def ascii_decimal_encode(s: str) -> str:
        return " ".join(str(ord(c)) for c in s)

    @staticmethod
    def ascii_decimal_decode(s: str) -> str:
        nums = re.findall(r"\d+", s)
        return "".join(chr(int(n)) for n in nums)

    @staticmethod
    def ascii_binary_encode(s: str) -> str:
        return " ".join(format(ord(c), "08b") for c in s)

    @staticmethod
    def ascii_binary_decode(s: str) -> str:
        bits = re.findall(r"[01]+", s)
        return "".join(chr(int(b, 2)) for b in bits)

    @staticmethod
    def ascii_octal_encode(s: str) -> str:
        return " ".join(format(ord(c), "o") for c in s)

    @staticmethod
    def ascii_octal_decode(s: str) -> str:
        nums = re.findall(r"[0-7]+", s)
        return "".join(chr(int(n, 8)) for n in nums)

    @staticmethod
    def quoted_printable_encode(s: str) -> str:
        import quopri
        return quopri.encodestring(s.encode()).decode()

    @staticmethod
    def quoted_printable_decode(s: str) -> str:
        import quopri
        return quopri.decodestring(s.encode()).decode()

    @staticmethod
    def uu_encode(data: bytes) -> str:
        import uu
        import io
        out = io.BytesIO()
        uu.encode(io.BytesIO(data), out)
        return out.getvalue().decode("latin-1")

    @staticmethod
    def uu_decode(text: str) -> bytes:
        import uu
        import io
        inp = io.BytesIO(text.encode("latin-1"))
        out = io.BytesIO()
        uu.decode(inp, out)
        return out.getvalue()

    @staticmethod
    def shellcode_encode(s: str) -> str:
        """C 风格 \\x 十六进制 shellcode"""
        data = s.encode("utf-8", errors="replace")
        return "".join(f"\\x{b:02x}" for b in data)

    @staticmethod
    def shellcode_decode(s: str) -> bytes:
        import re
        parts = re.findall(r"\\x([0-9a-fA-F]{2})", s)
        if parts:
            return bytes(int(p, 16) for p in parts)
        parts = re.findall(r"[0-9a-fA-F]{2}", s)
        return bytes(int(p, 16) for p in parts)

    @staticmethod
    def xxencode(data: bytes) -> str:
        """XXencode (简化实现)"""
        import base64
        b64 = base64.b64encode(data).decode()
        trans = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            "+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        )
        return "XX" + b64.translate(trans) + "XX"

    @staticmethod
    def xxdecode(text: str) -> bytes:
        import base64
        text = text.strip()
        if text.startswith("XX"):
            text = text[2:]
        if text.endswith("XX"):
            text = text[:-2]
        trans = str.maketrans(
            "+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
        )
        return base64.b64decode(text.translate(trans))
