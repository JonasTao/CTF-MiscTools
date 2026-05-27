"""哈希计算与识别"""
import hashlib
import hmac
import re


class HashTools:
    PATTERNS = [
        (r"^[a-fA-F0-9]{32}$", "MD5"),
        (r"^[a-fA-F0-9]{40}$", "SHA-1"),
        (r"^[a-fA-F0-9]{56}$", "SHA-224"),
        (r"^[a-fA-F0-9]{64}$", "SHA-256 / SHA3-256 / SM3"),
        (r"^[a-fA-F0-9]{96}$", "SHA-384"),
        (r"^[a-fA-F0-9]{128}$", "SHA-512 / SHA3-512"),
        (r"^\$2[aby]\$\d{2}\$", "bcrypt"),
        (r"^\$6\$", "SHA-512 crypt"),
        (r"^\$5\$", "SHA-256 crypt"),
        (r"^\$1\$", "MD5 crypt"),
    ]

    @staticmethod
    def md5(data: bytes) -> str:
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def sha1(data: bytes) -> str:
        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: bytes) -> str:
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def sha3_256(data: bytes) -> str:
        return hashlib.sha3_256(data).hexdigest()

    @staticmethod
    def hmac_sha256(data: bytes, key: bytes) -> str:
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def identify(text: str) -> list:
        text = text.strip()
        found = []
        for pat, name in HashTools.PATTERNS:
            if re.match(pat, text):
                found.append(name)
        return found or ["未知格式"]

    @staticmethod
    def sha224(data: bytes) -> str:
        return hashlib.sha224(data).hexdigest()

    @staticmethod
    def sha384(data: bytes) -> str:
        return hashlib.sha384(data).hexdigest()

    @staticmethod
    def compute_all(text: str) -> dict:
        data = text.encode("utf-8", errors="replace")
        return {
            "MD5": HashTools.md5(data),
            "SHA-1": HashTools.sha1(data),
            "SHA-224": HashTools.sha224(data),
            "SHA-256": HashTools.sha256(data),
            "SHA-384": HashTools.sha384(data),
            "SHA-512": HashTools.sha512(data),
            "SHA3-256": HashTools.sha3_256(data),
        }
