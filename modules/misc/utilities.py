"""杂项工具：进制、QR、Flag"""
import io
import re

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False


class MiscUtils:
    @staticmethod
    def radix_convert(value: str, from_base: int, to_base: int) -> str:
        if from_base < 2 or to_base < 2 or to_base > 36:
            raise ValueError("进制范围 2-36")
        n = int(value.strip(), from_base)
        if to_base == 10:
            return str(n)
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        if n == 0:
            return "0"
        out = []
        while n:
            n, r = divmod(n, to_base)
            out.append(digits[r])
        return "".join(reversed(out))

    @staticmethod
    def qr_encode(text: str, save_path: str = None) -> bytes:
        if not HAS_QR:
            raise RuntimeError("请安装 qrcode: pip install qrcode")
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#FF9EC7", back_color="#FFF5F8")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()
        if save_path:
            with open(save_path, "wb") as f:
                f.write(data)
        return data

    @staticmethod
    def qr_decode(path: str) -> str:
        if not HAS_PYZBAR:
            raise RuntimeError("请安装 pyzbar 及 zbar 库")
        from PIL import Image
        img = Image.open(path)
        codes = pyzbar.decode(img)
        return "\n".join(c.data.decode("utf-8", errors="replace") for c in codes)

    @staticmethod
    def check_flag(text: str, patterns: list = None) -> list:
        patterns = patterns or [
            r"flag\{[^{}]+\}",
            r"FLAG\{[^{}]+\}",
            r"ctf\{[^{}]+\}",
            r"CTF\{[^{}]+\}",
            r"[A-Za-z0-9_]{32}",
        ]
        found = []
        for p in patterns:
            found.extend(re.findall(p, text, re.IGNORECASE))
        return list(dict.fromkeys(found))
