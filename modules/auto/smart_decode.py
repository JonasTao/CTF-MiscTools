"""智能链式解码（轻量 Ciphey）"""
import re

from modules.encoding.base_codec import BaseCodec
from modules.encoding.text_codec import TextCodec
from modules.encoding.esoteric import EsotericCodec
from modules.cipher.classical import ClassicalCipher


class SmartDecoder:
    @staticmethod
    def try_all(text: str, max_depth: int = 4) -> list:
        seen = set()
        results = []

        def _score(s: str) -> float:
            if not s:
                return 0
            printable = sum(1 for c in s if c.isprintable() or c in "\n\r\t")
            ratio = printable / max(len(s), 1) * 100
            flag_bonus = 80 if re.search(r"(flag|ctf)\{[^}]+\}", s, re.I) else 0
            word_bonus = 10 if re.search(r"\bthe\b|\band\b|\bflag\b", s, re.I) else 0
            return ratio + flag_bonus + word_bonus

        def _decode(s: str, depth: int, chain: list):
            if depth > max_depth:
                return
            key = (s[:200], depth, tuple(chain))
            if key in seen:
                return
            seen.add(key)
            sc = _score(s)
            if sc >= 55 and len(s) >= 2:
                results.append((sc, " -> ".join(chain), s))
            for name, out in SmartDecoder._one_step(s):
                if out and out != s and len(out) < 50000:
                    _decode(out, depth + 1, chain + [name])

        _decode(text.strip(), 0, ["原文"])
        uniq = {}
        for sc, chain, result in results:
            if result not in uniq or sc > uniq[result][0]:
                uniq[result] = (sc, chain, result)
        results = sorted(uniq.values(), key=lambda x: -x[0])
        return results[:20]

    @staticmethod
    def _one_step(s: str) -> list:
        out = []
        seen_out = set()

        def add(name, val):
            if val and val != s and val not in seen_out:
                if _mostly_printable(val):
                    seen_out.add(val)
                    out.append((name, val))

        # Base64
        if re.match(r"^[A-Za-z0-9+/=\s]+$", s) and len(s) >= 4:
            try:
                d = BaseCodec.decode_b64(s).decode("utf-8", errors="strict")
                add("Base64", d)
            except Exception:
                try:
                    d = BaseCodec.decode_b64(s).decode("latin-1")
                    add("Base64(latin)", d)
                except Exception:
                    pass
        # Base32
        if re.match(r"^[A-Z2-7=]+$", s.strip(), re.I):
            try:
                d = BaseCodec.decode_b32(s).decode("utf-8", errors="replace")
                add("Base32", d)
            except Exception:
                pass
        # Hex
        if re.fullmatch(r"[0-9a-fA-F\s]+", s.strip()) and len(s.strip()) >= 4:
            try:
                d = TextCodec.hex_decode(s).decode("utf-8", errors="replace")
                add("Hex", d)
            except Exception:
                pass
        # URL
        if "%" in s:
            try:
                add("URL", TextCodec.url_decode(s))
            except Exception:
                pass
        # HTML
        if "&" in s and ";" in s:
            try:
                add("HTML", TextCodec.html_decode(s))
            except Exception:
                pass
        # Unicode escape
        if "\\u" in s or "\\x" in s:
            try:
                add("Unicode", TextCodec.unicode_escape_decode(s))
            except Exception:
                pass
        # ROT13 / Atbash / ROT47（仅对可打印 ASCII 文本）
        if _is_ascii_letters(s):
            d13 = ClassicalCipher.rot13(s)
            if d13 != s:
                add("ROT13", d13)
            d_at = ClassicalCipher.atbash(s)
            if d_at != s:
                add("Atbash", d_at)
        if all(33 <= ord(c) <= 126 for c in s):
            d47 = EsotericCodec.rot47(s)
            if d47 != s:
                add("ROT47", d47)
        # Caesar — 尝试所有偏移，保留看起来像英文的
        for shift in range(1, 26):
            d = ClassicalCipher.caesar(s, shift, decode=True)
            if _looks_english(d):
                add(f"Caesar-{shift}", d)
        # Morse
        if re.search(r"\.|/", s) and re.match(r"[\s.\-/A-Za-z]+", s):
            try:
                d = ClassicalCipher.morse_decode(s)
                if d:
                    add("Morse", d)
            except Exception:
                pass
        # Bacon (a/b)
        if re.search(r"[abAB]{5,}", s):
            d = ClassicalCipher.bacon_decode(s)
            if d:
                add("Bacon", d)
        # ASCII decimal
        if re.fullmatch(r"[\d\s,;]+", s.strip()) and len(s) > 6:
            try:
                add("ASCII-dec", TextCodec.ascii_decimal_decode(s))
            except Exception:
                pass
        return out


def _mostly_printable(s: str) -> bool:
    if not s:
        return False
    ok = sum(1 for c in s if c.isprintable() or c in "\n\r\t")
    return ok / len(s) > 0.85


def _is_ascii_letters(s: str) -> bool:
    if not s or len(s) > 5000:
        return False
    return all(c.isascii() and (c.isalpha() or c.isspace() or c in ".,!?'-{}[]") for c in s)


def _looks_english(s: str) -> bool:
    if len(s) < 4:
        return False
    letters = sum(1 for c in s if c.isalpha())
    if letters / len(s) < 0.5:
        return False
    common = sum(1 for w in ("the", "and", "flag", "ctf", "is", "to") if w in s.lower())
    return common > 0 or letters / len(s) > 0.7
