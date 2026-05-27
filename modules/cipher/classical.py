"""古典密码"""
import re


class ClassicalCipher:
    MORSE = {
        "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
        "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
        "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
        "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
        "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
        "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
        "8": "---..", "9": "----.",
    }
    MORSE_REV = {v: k for k, v in MORSE.items()}

    BACON_A = {
        "aaaaa": "A", "aaaab": "B", "aaaba": "C", "aaabb": "D", "aabaa": "E",
        "aabab": "F", "aabba": "G", "aabbb": "H", "abaaa": "I", "abaab": "J",
        "ababa": "K", "ababb": "L", "abbaa": "M", "abbab": "N", "abbba": "O",
        "abbbb": "P", "baaaa": "Q", "baaab": "R", "baaba": "S", "baabb": "T",
        "babaa": "U", "babab": "V", "babba": "W", "babbb": "X", "bbaaa": "Y",
        "bbaab": "Z",
    }
    BACON_REV = {v: k for k, v in BACON_A.items()}

    # 标准 5x5 敲击码 (Polybius, I/J 共用 I)
    TAP_GRID = [
        list("ABCDE"),
        list("FGHIK"),
        list("LMNOP"),
        list("QRSTU"),
        list("VWXYZ"),
    ]

    @staticmethod
    def caesar(text: str, shift: int, decode: bool = False) -> str:
        if decode:
            shift = -shift
        result = []
        for c in text:
            if c.isalpha():
                base = ord("A") if c.isupper() else ord("a")
                result.append(chr((ord(c) - base + shift) % 26 + base))
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def rot13(text: str) -> str:
        return ClassicalCipher.caesar(text, 13)

    @staticmethod
    def rot5(text: str) -> str:
        """仅数字 ROT5"""
        out = []
        for c in text:
            if c.isdigit():
                out.append(str((int(c) + 5) % 10))
            else:
                out.append(c)
        return "".join(out)

    @staticmethod
    def rot18(text: str) -> str:
        return ClassicalCipher.rot13(ClassicalCipher.rot5(text))

    @staticmethod
    def atbash(text: str) -> str:
        result = []
        for c in text:
            if "A" <= c <= "Z":
                result.append(chr(ord("Z") - (ord(c) - ord("A"))))
            elif "a" <= c <= "z":
                result.append(chr(ord("z") - (ord(c) - ord("a"))))
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def morse_encode(text: str) -> str:
        parts = []
        for c in text.upper():
            if c == " ":
                parts.append("/")
            elif c in ClassicalCipher.MORSE:
                parts.append(ClassicalCipher.MORSE[c])
        return " ".join(parts)

    @staticmethod
    def morse_decode(text: str) -> str:
        text = text.strip()
        words = re.split(r"\s*/\s*|\s{2,}", text)
        out_words = []
        for word in words:
            tokens = re.split(r"[\s,;|]+", word.strip())
            letters = []
            for w in tokens:
                w = w.strip()
                if not w:
                    continue
                if w in ClassicalCipher.MORSE_REV:
                    letters.append(ClassicalCipher.MORSE_REV[w])
                elif w == "/":
                    letters.append(" ")
            out_words.append("".join(letters))
        return " ".join(out_words)

    @staticmethod
    def bacon_encode(text: str) -> str:
        t = re.sub(r"[^a-zA-Z]", "", text).upper()
        return " ".join(ClassicalCipher.BACON_REV.get(c, "") for c in t)

    @staticmethod
    def bacon_decode(text: str) -> str:
        t = re.sub(r"[^abAB01]", "", text).lower()
        t = t.replace("0", "a").replace("1", "b")
        out = []
        for i in range(0, len(t) - 4, 5):
            chunk = t[i : i + 5]
            if chunk in ClassicalCipher.BACON_A:
                out.append(ClassicalCipher.BACON_A[chunk])
        return "".join(out)

    @staticmethod
    def rail_fence_decode(cipher: str, rails: int) -> str:
        if rails <= 1:
            return cipher
        n = len(cipher)
        fence = [["\n"] * n for _ in range(rails)]
        direction, row = 1, 0
        for col in range(n):
            fence[row][col] = "*"
            row += direction
            if row == 0 or row == rails - 1:
                direction = -direction
        idx = 0
        for r in range(rails):
            for c in range(n):
                if fence[r][c] == "*" and idx < n:
                    fence[r][c] = cipher[idx]
                    idx += 1
        result, row, direction = [], 0, 1
        for col in range(n):
            result.append(fence[row][col])
            row += direction
            if row == 0 or row == rails - 1:
                direction = -direction
        return "".join(result)

    @staticmethod
    def rail_fence_encode(plain: str, rails: int) -> str:
        if rails <= 1:
            return plain
        fence = [[] for _ in range(rails)]
        row, direction = 0, 1
        for c in plain:
            fence[row].append(c)
            row += direction
            if row == 0 or row == rails - 1:
                direction = -direction
        return "".join("".join(r) for r in fence)

    @staticmethod
    def vigenere(text: str, key: str, decode: bool = False) -> str:
        key = re.sub(r"[^a-zA-Z]", "", key).upper()
        if not key:
            return text
        result, ki = [], 0
        for c in text:
            if c.isalpha():
                base = ord("A") if c.isupper() else ord("a")
                k = ord(key[ki % len(key)]) - ord("A")
                if decode:
                    k = -k
                result.append(chr((ord(c) - base + k) % 26 + base))
                ki += 1
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def affine_decode(cipher: str, a: int, b: int) -> str:
        a_inv = ClassicalCipher._mod_inv(a, 26)
        if a_inv is None:
            raise ValueError(f"a={a} 与 26 不互质，无法解密")
        result = []
        for c in cipher:
            if c.isalpha():
                base = ord("A") if c.isupper() else ord("a")
                y = ord(c) - base
                x = (a_inv * (y - b)) % 26
                result.append(chr(x + base))
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def affine_encode(plain: str, a: int, b: int) -> str:
        if ClassicalCipher._mod_inv(a, 26) is None:
            raise ValueError(f"a={a} 与 26 不互质，无法加密")
        result = []
        for c in plain:
            if c.isalpha():
                base = ord("A") if c.isupper() else ord("a")
                x = ord(c) - base
                y = (a * x + b) % 26
                result.append(chr(y + base))
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def _mod_inv(a: int, m: int = 26):
        a %= m
        for i in range(1, m):
            if (a * i) % m == 1:
                return i
        return None

    @staticmethod
    def keyboard_cipher_decode(text: str) -> str:
        """键盘密码：密文为键盘上向左/上一键偏移，解密则向右还原"""
        layout = [
            "`1234567890-=",
            "qwertyuiop[]\\",
            "asdfghjkl;' ",
            " zxcvbnm,./",
        ]
        pos = {}
        for r, row in enumerate(layout):
            for c, ch in enumerate(row):
                if ch.strip():
                    pos[ch] = (r, c)
                    pos[ch.upper()] = (r, c)
        neighbors = {}
        for ch, (r, c) in pos.items():
            for dr, dc in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(layout) and 0 <= nc < len(layout[nr]):
                    nb = layout[nr][nc]
                    if nb.strip():
                        neighbors[ch] = nb
        return "".join(neighbors.get(c, c) for c in text)

    @staticmethod
    def keyboard_cipher_encode(text: str) -> str:
        """加密：每个字符映射到键盘左侧相邻键（常见出题方式）"""
        layout = [
            "`1234567890-=",
            "qwertyuiop[]\\",
            "asdfghjkl;' ",
            " zxcvbnm,./",
        ]
        pos = {}
        for r, row in enumerate(layout):
            for c, ch in enumerate(row):
                if ch.strip():
                    pos[ch] = (r, c)
                    pos[ch.upper()] = (r, c)
        left_map = {}
        for ch, (r, c) in pos.items():
            if c > 0 and layout[r][c - 1].strip():
                left_map[ch] = layout[r][c - 1]
        return "".join(left_map.get(c, c) for c in text)

    @staticmethod
    def a1z26_decode(text: str) -> str:
        nums = re.findall(r"\d+", text)
        out = []
        for n in nums:
            v = int(n)
            if 1 <= v <= 26:
                out.append(chr(64 + v))
        return "".join(out)

    @staticmethod
    def a1z26_encode(text: str) -> str:
        return "-".join(str(ord(c.upper()) - 64) for c in text if c.isalpha())

    @staticmethod
    def tap_code_encode(text: str) -> str:
        grid = ClassicalCipher.TAP_GRID
        coords = {}
        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                coords[ch] = (r + 1, c + 1)
        coords["J"] = coords.get("I", (2, 4))
        parts = []
        for ch in text.upper():
            if ch in coords:
                r, c = coords[ch]
                parts.append(f"{r}{c}")
        return " ".join(parts)

    @staticmethod
    def tap_code_decode(text: str) -> str:
        grid = ClassicalCipher.TAP_GRID
        pairs = re.findall(r"(\d)\s*(\d)", text)
        out = []
        for r, c in pairs:
            ri, ci = int(r) - 1, int(c) - 1
            if 0 <= ri < len(grid) and 0 <= ci < len(grid[ri]):
                out.append(grid[ri][ci])
        return "".join(out)

    @staticmethod
    def xor_text(a: str, b: str) -> str:
        if not b:
            raise ValueError("密钥不能为空")
        b = (b * (len(a) // len(b) + 1))[: len(a)]
        return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(a, b))

    @staticmethod
    def xor_bytes(data: bytes, key: bytes) -> bytes:
        if not key:
            return data
        return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))

    @staticmethod
    def frequency_analysis(text: str) -> str:
        from collections import Counter
        letters = [c.upper() for c in text if c.isalpha()]
        if not letters:
            return "无字母可分析"
        cnt = Counter(letters)
        total = sum(cnt.values())
        lines = ["字符  次数  频率", "-" * 24]
        for ch, n in cnt.most_common():
            lines.append(f"  {ch}    {n:4d}   {n/total*100:5.1f}%")
        return "\n".join(lines)
