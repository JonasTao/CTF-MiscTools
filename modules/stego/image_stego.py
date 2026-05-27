"""图片隐写基础分析"""
import io
import re
import struct

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageStego:
    @staticmethod
    def require_pil():
        if not HAS_PIL:
            raise RuntimeError("请安装 Pillow: pip install Pillow")

    @staticmethod
    def read_exif(path: str) -> dict:
        ImageStego.require_pil()
        img = Image.open(path)
        exif = {}
        if hasattr(img, "_getexif") and img._getexif():
            from PIL.ExifTags import TAGS
            for k, v in img._getexif().items():
                exif[TAGS.get(k, k)] = v
        info = dict(img.info) if img.info else {}
        return {"exif": exif, "info": info, "size": img.size, "mode": img.mode}

    @staticmethod
    def lsb_extract_text(path: str, channel: int = 0, max_bits: int = 32000) -> str:
        ImageStego.require_pil()
        img = Image.open(path).convert("RGB")
        pixels = list(img.getdata())
        bits = [px[channel] & 1 for px in pixels[: max_bits // 8 + 8]]
        if len(bits) > max_bits:
            bits = bits[:max_bits]
        chars = []
        for i in range(0, len(bits) - 7, 8):
            byte = int("".join(str(b) for b in bits[i:i + 8]), 2)
            if byte == 0:
                break
            if 32 <= byte < 127 or byte in (10, 13):
                chars.append(chr(byte))
            else:
                break
        return "".join(chars)

    @staticmethod
    def lsb_preview(path: str) -> dict:
        ImageStego.require_pil()
        result = {}
        for ch, name in enumerate(["R", "G", "B"]):
            try:
                result[name] = ImageStego.lsb_extract_text(path, ch, 4000)[:200]
            except Exception as e:
                result[name] = str(e)
        return result

    @staticmethod
    def extract_trailing_data(path: str) -> bytes:
        ImageStego.require_pil()
        with open(path, "rb") as f:
            data = f.read()
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            pos = data.find(b"IEND")
            if pos != -1:
                end = pos + 8
                trailing = data[end:]
                if trailing:
                    return trailing
        if data[:2] == b"\xff\xd8":
            idx = data.rfind(b"\xff\xd9")
            if idx != -1:
                trailing = data[idx + 2:]
                if trailing:
                    return trailing
        return b""

    @staticmethod
    def zero_width_decode(text: str) -> str:
        zw = {"\u200b": "0", "\u200c": "1", "\u200d": "", "\ufeff": ""}
        bits = []
        for c in text:
            if c in zw and zw[c] in ("0", "1"):
                bits.append(zw[c])
        if not bits:
            return ""
        out = []
        for i in range(0, len(bits) - 7, 8):
            out.append(chr(int("".join(bits[i:i + 8]), 2)))
        return "".join(out)
