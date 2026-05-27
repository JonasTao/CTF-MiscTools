"""文件分析工具"""
import binascii
import os
import re
import struct


MAGIC = [
    # 图片格式
    (b"\x89PNG\r\n\x1a\n", "PNG 图片"),
    (b"\xff\xd8\xff", "JPEG 图片"),
    (b"GIF87a", "GIF 图片"),
    (b"GIF89a", "GIF 图片"),
    (b"BM", "BMP 图片"),
    (b"\x00\x00\x01\x00", "ICO 图标"),
    (b"RIFF....WEBP", "WebP 图片"),
    (b"\x52\x49\x46\x46....\x57\x41\x56\x45", "WAV 音频"),
    
    # 压缩格式
    (b"PK\x03\x04", "ZIP 压缩包"),
    (b"PK\x05\x06", "ZIP 空压缩包"),
    (b"Rar!\x1a\x07", "RAR 压缩包"),
    (b"\x1f\x8b\x08", "GZIP 压缩"),
    (b"\x42\x5a\x68", "BZIP2 压缩"),
    (b"\x37\x7a\xbc\xaf\x27\x1c", "7Z 压缩"),
    (b"\x50\x4b\x03\x04", "ZIP (PK)"),
    
    # 可执行文件
    (b"\x7fELF", "ELF 可执行"),
    (b"MZ", "PE/DOS 可执行"),
    (b"\x4d\x5a", "PE/DOS 可执行"),
    
    # 文档
    (b"%PDF", "PDF 文档"),
    (b"OggS", "OGG 音频"),
    (b"\x25\x50\x44\x46", "PDF"),
    (b"<?xml", "XML 文件"),
    (b"\xef\xbb\xbf", "UTF-8 BOM"),
    
    # CTF 相关
    (b"flag{", "内嵌 flag 文本"),
    (b"FLAG{", "内嵌 FLAG 文本"),
    (b"ctf{", "内嵌 ctf 文本"),
    (b"CTF{", "内嵌 CTF 文本"),
    (b"key{", "内嵌 key 文本"),
    (b"KEY{", "内嵌 KEY 文本"),
    (b"secret{", "内嵌 secret 文本"),
    (b"SECRET{", "内嵌 SECRET 文本"),
    
    # Base64 特征
    (b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=", "Base64 数据"),
    
    # 其他
    (b"SQLite format 3", "SQLite 数据库"),
    (b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00", "SQLite"),
]


class FileTools:
    @staticmethod
    def detect_type(path: str) -> list:
        """检测文件类型，支持更多格式"""
        with open(path, "rb") as f:
            head = f.read(512)
        found = []
        
        # 精确匹配头部
        for sig, name in MAGIC:
            if head.startswith(sig):
                found.append(name)
        
        # 搜索内部签名（如内嵌文件）
        for sig, name in MAGIC:
            if len(sig) <= 32 and sig in head[:256] and sig not in head[:16]:
                found.append(f"内嵌 {name}")
        
        # 添加扩展名信息
        ext = os.path.splitext(path)[1].lower()
        if ext:
            found.append(f"扩展名: {ext}")
        
        # 文件大小信息
        try:
            size = os.path.getsize(path)
            if size < 1024:
                found.append(f"大小: {size} 字节")
            elif size < 1024 * 1024:
                found.append(f"大小: {size / 1024:.1f} KB")
            else:
                found.append(f"大小: {size / (1024 * 1024):.1f} MB")
        except:
            pass
        
        return found or ["未知类型"]

    @staticmethod
    def extract_strings(path: str, min_len: int = 4, max_count: int = 500) -> list:
        """提取可打印字符串，支持ASCII和UTF-8"""
        with open(path, "rb") as f:
            data = f.read()
        
        results = []
        
        # ASCII 字符串
        ascii_pattern = rb"[\x20-\x7e]{%d,}" % min_len
        for m in re.findall(ascii_pattern, data):
            try:
                s = m.decode("ascii")
                if len(s) >= min_len:
                    results.append(s)
            except:
                pass
        
        # UTF-8 字符串（尝试）
        try:
            utf8_data = data.decode("utf-8", errors="ignore")
            utf8_pattern = r"[\w\u4e00-\u9fa5]{3,}"
            for m in re.findall(utf8_pattern, utf8_data):
                if len(m) >= min_len and m not in results:
                    results.append(m)
        except:
            pass
        
        # 去重并排序
        results = sorted(set(results), key=lambda x: (-len(x), x))
        
        return results[:max_count]

    @staticmethod
    def file_to_hex(path: str, limit: int = 4096, cols: int = 16) -> str:
        """格式化的十六进制预览，带偏移和ASCII"""
        with open(path, "rb") as f:
            data = f.read(limit)
        
        lines = []
        for i in range(0, len(data), cols):
            chunk = data[i:i+cols]
            offset = f"{i:08X}"
            
            # 十六进制部分
            hex_str = " ".join(f"{b:02X}" for b in chunk)
            # 补齐到固定宽度
            hex_str = hex_str.ljust(cols * 3)
            
            # ASCII 部分
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            
            lines.append(f"{offset}  {hex_str}  |{ascii_str}|")
        
        return "\n".join(lines)

    @staticmethod
    def xor_bruteforce_single(path: str, limit: int = 512, top_n: int = 12) -> list:
        """单字节 XOR 爆破，优化评分算法"""
        with open(path, "rb") as f:
            data = f.read(limit)
        
        if not data:
            return []
        
        results = []
        
        for key in range(256):
            dec = bytes(b ^ key for b in data)
            
            # 评分：可打印字符比例 + 空格比例 + 常见字符奖励
            printable = sum(1 for b in dec if 32 <= b < 127)
            spaces = sum(1 for b in dec if b == 32)
            letters = sum(1 for b in dec if 65 <= b <= 90 or 97 <= b <= 122)
            
            # 综合评分
            score = (printable / len(data)) * 0.6 + \
                    (spaces / len(data)) * 0.2 + \
                    (letters / len(data)) * 0.2
            
            if score > 0.5:  # 降低阈值，显示更多候选
                preview = dec[:150].decode("ascii", errors="replace")
                # 清理预览中的控制字符
                preview = re.sub(r"[\x00-\x1f\x7f]", ".", preview)
                results.append((key, score, preview))
        
        results.sort(key=lambda x: -x[1])
        return [(k, p) for k, _, p in results[:top_n]]

    @staticmethod
    def xor_bruteforce_repeating(path: str, max_key_len: int = 8, limit: int = 512) -> list:
        """重复密钥 XOR 爆破，支持更长密钥"""
        with open(path, "rb") as f:
            data = f.read(limit)
        
        if len(data) < 8:
            return []
        
        best = []
        
        for key_len in range(2, min(max_key_len + 1, len(data) // 2)):
            for k1 in range(32, 127):
                for k2 in range(32, 127):
                    if key_len == 2:
                        key = bytes([k1, k2])
                    elif key_len == 3:
                        key = bytes([k1, k2, k1])  # 简单模式
                    elif key_len == 4:
                        key = bytes([k1, k2, k1, k2])
                    else:
                        key = bytes([k1, k2] * ((key_len + 1) // 2))[:key_len]
                    
                    dec = bytes(b ^ key[i % key_len] for i, b in enumerate(data))
                    
                    # 评分
                    printable = sum(1 for b in dec if 32 <= b < 127) / len(data)
                    if printable > 0.6:
                        preview = dec[:100].decode("ascii", errors="replace")
                        preview = re.sub(r"[\x00-\x1f\x7f]", ".", preview)
                        best.append((key.decode("ascii"), preview, printable))
        
        best.sort(key=lambda x: -x[2])
        return [(k, p) for k, p, _ in best[:8]]

    @staticmethod
    def search_flag(path: str) -> list:
        """搜索各种 flag 格式，支持更多模式"""
        strings = FileTools.extract_strings(path, 4)
        flags = []
        
        # 标准 flag 格式
        patterns = [
            r"(flag|FLAG|ctf|CTF)\{[^}]+\}",
            r"(flag|FLAG|ctf|CTF)[=_: ]([^}]+)",
            r"[0-9a-fA-F]{32,}",  # MD5/SHA256 等哈希值
            r"[A-Za-z0-9+/=]{20,}",  # Base64
            r"(key|KEY|secret|SECRET|token|TOKEN)\{[^}]+\}",
            r"(pass|passwd|password|PASS|PASSWORD)[=_: ](.+?)\s",
        ]
        
        for s in strings:
            for pattern in patterns:
                for m in re.finditer(pattern, s):
                    result = m.group()
                    if result not in flags:
                        flags.append(result)
        
        return sorted(flags, key=len, reverse=True)

    @staticmethod
    def binwalk_simple(path: str, max_hits: int = 30) -> list:
        """简易嵌入文件扫描，增强版本"""
        with open(path, "rb") as f:
            data = f.read()
        
        hits = []
        seen_positions = set()
        
        for sig, name in MAGIC:
            idx = 0
            while True:
                pos = data.find(sig, idx)
                if pos == -1:
                    break
                
                # 跳过已记录的位置附近
                is_new = True
                for seen in seen_positions:
                    if abs(pos - seen) < 8:
                        is_new = False
                        break
                
                if is_new and pos > 0:
                    # 检查前一个字节是否为换行或空白
                    prev_byte = data[pos-1] if pos > 0 else 0
                    if prev_byte not in (0, 10, 13, 32):
                        hits.append(f"偏移 0x{pos:08X}: {name}")
                        seen_positions.add(pos)
                
                idx = pos + 1
        
        # 按偏移排序
        hits.sort(key=lambda x: int(x.split()[1], 16))
        
        return hits[:max_hits]
