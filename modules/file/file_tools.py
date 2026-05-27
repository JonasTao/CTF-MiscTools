"""文件分析工具"""
import binascii
import os
import re
import struct


MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "PNG 图片"),
    (b"\xff\xd8\xff", "JPEG 图片"),
    (b"GIF87a", "GIF 图片"),
    (b"GIF89a", "GIF 图片"),
    (b"PK\x03\x04", "ZIP 压缩包"),
    (b"Rar!\x1a\x07", "RAR 压缩包"),
    (b"\x7fELF", "ELF 可执行"),
    (b"MZ", "PE/DOS 可执行"),
    (b"%PDF", "PDF 文档"),
    (b"\x1f\x8b", "GZIP"),
    (b"BM", "BMP 图片"),
    (b"RIFF", "RIFF (WAV/AVI)"),
    (b"\x00\x00\x01\x00", "ICO"),
    (b"flag{", "内嵌 flag 文本"),
    (b"FLAG{", "内嵌 FLAG 文本"),
]


class FileTools:
    @staticmethod
    def detect_type(path: str) -> list:
        with open(path, "rb") as f:
            head = f.read(512)
        found = []
        for sig, name in MAGIC:
            if head.startswith(sig) or sig in head[:64]:
                found.append(name)
        ext = os.path.splitext(path)[1].lower()
        if ext and not found:
            found.append(f"扩展名: {ext}")
        return found or ["未知类型"]

    @staticmethod
    def extract_strings(path: str, min_len: int = 4) -> list:
        with open(path, "rb") as f:
            data = f.read()
        pattern = rb"[\x20-\x7e]{%d,}" % min_len
        return [m.decode("ascii", errors="replace") for m in re.findall(pattern, data)]

    @staticmethod
    def file_to_hex(path: str, limit: int = 4096) -> str:
        with open(path, "rb") as f:
            data = f.read(limit)
        return binascii.hexlify(data).decode()

    @staticmethod
    def xor_bruteforce_single(path: str, limit: int = 512) -> list:
        with open(path, "rb") as f:
            data = f.read(limit)
        results = []
        for key in range(256):
            dec = bytes(b ^ key for b in data)
            score = sum(1 for b in dec if 32 <= b < 127)
            if score > len(data) * 0.65:
                preview = dec[:120].decode("ascii", errors="replace")
                results.append((key, score / len(data), preview))
        results.sort(key=lambda x: -x[1])
        return [(k, p) for k, _, p in results[:12]]

    @staticmethod
    def xor_bruteforce_repeating(path: str, key_len: int = 4, limit: int = 256) -> list:
        """重复密钥 XOR 爆破（短密钥）"""
        with open(path, "rb") as f:
            data = f.read(limit)
        if len(data) < key_len * 2:
            return []
        best = []
        for k1 in range(32, 127):
            key = bytes([k1] * key_len)
            dec = bytes(b ^ key[i % key_len] for i, b in enumerate(data))
            score = sum(1 for b in dec if 32 <= b < 127) / len(data)
            if score > 0.7:
                best.append((chr(k1) * key_len, dec[:80].decode("ascii", errors="replace")))
        return best[:5]

    @staticmethod
    def search_flag(path: str) -> list:
        strings = FileTools.extract_strings(path, 5)
        flags = []
        for s in strings:
            for m in re.finditer(
                r"(flag|FLAG|ctf|CTF)\{[^}]+\}", s, re.IGNORECASE
            ):
                flags.append(m.group())
        return flags

    @staticmethod
    def binwalk_simple(path: str) -> list:
        """简易嵌入文件扫描（不依赖 binwalk）"""
        with open(path, "rb") as f:
            data = f.read()
        hits = []
        for sig, name in MAGIC:
            idx = 0
            while True:
                pos = data.find(sig, idx)
                if pos == -1:
                    break
                if pos > 0:
                    hits.append(f"偏移 0x{pos:X}: 可能的 {name}")
                idx = pos + 1
        return hits[:20]
