"""图片隐写分析 - Stegsolve功能集成"""
import io
import re
import struct
from typing import List, Tuple, Optional

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
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

    @staticmethod
    def lsb_extract_all_channels(path: str, max_bytes: int = 10000) -> dict:
        """提取RGB三个通道的LSB位，合并后提取隐藏数据

        Args:
            path: 图片路径
            max_bytes: 最大提取字节数

        Returns:
            dict: 包含提取的bits、bytes和字符串内容
        """
        ImageStego.require_pil()
        img = Image.open(path).convert("RGB")
        pixels = list(img.getdata())

        bits = []
        for pixel in pixels:
            bits.append(pixel[0] & 1)
            bits.append(pixel[1] & 1)
            bits.append(pixel[2] & 1)

        bytes_data = bytes(
            int(''.join(map(str, bits[i:i+8])), 2)
            for i in range(0, min(len(bits) // 8, max_bytes) * 8, 8)
        )

        try:
            hex_output = bytes_data.hex()
            ascii_output = bytes_data.decode('ascii', errors='replace')
        except:
            hex_output = bytes_data.hex()
            ascii_output = ""

        return {
            'bits': bits,
            'bytes': bytes_data,
            'hex': hex_output,
            'ascii': ascii_output,
            'total_bits': len(bits),
            'total_bytes': len(bytes_data)
        }

    @staticmethod
    def lsb_extract_flag(path: str) -> str:
        """提取flag格式的数据"""
        result = ImageStego.lsb_extract_all_channels(path)
        bytes_data = result['bytes']

        try:
            hex_str = bytes_data.hex()
            if 'flag{' in hex_str:
                start = hex_str.index('flag{')
                end = hex_str.index('}', start) + 1
                flag_hex = hex_str[start:end]
                return bytes.fromhex(flag_hex).decode('ascii', errors='replace')
        except:
            pass

        try:
            ascii_str = bytes_data.decode('ascii', errors='replace')
            if 'flag{' in ascii_str:
                return ascii_str.split('flag{')[1].split('}')[0]
        except:
            pass

        return ""


class StegsolveAnalyzer:
    """Stegsolve风格的分析器"""

    CHANNEL_MODES = {
        "Red": 0,
        "Green": 1,
        "Blue": 2,
        "Gray": 3,
        "Magenta": 4,
        "Cyan": 5,
        "Yellow": 6,
        "Alpha": 7
    }

    LUT_PRESETS = {
        "Reverse": "invert",
        "Threshold 128": "threshold_128",
        "Threshold 64": "threshold_64",
        "Threshold 32": "threshold_32",
        "Threshold 16": "threshold_16",
        "Threshold 8": "threshold_8",
        "Threshold 4": "threshold_4",
        "Threshold 2": "threshold_2",
        "Threshold 1": "threshold_1",
        "Hue Rotate 90": "hue_90",
        "Hue Rotate 180": "hue_180",
        "Hue Rotate 270": "hue_270",
        "Solarize": "solarize",
        "Equalize": "equalize"
    }

    @staticmethod
    def require_pil():
        if not HAS_PIL:
            raise RuntimeError("请安装 Pillow: pip install Pillow")

    @staticmethod
    def load_image(path: str) -> Image.Image:
        StegsolveAnalyzer.require_pil()
        return Image.open(path)

    @staticmethod
    def get_channel_image(img: Image.Image, mode: str) -> Image.Image:
        """提取指定通道的图像"""
        StegsolveAnalyzer.require_pil()

        if img.mode == 'RGBA':
            r, g, b, a = img.split()
        elif img.mode == 'RGB':
            r, g, b = img.split()
            a = None
        else:
            gray = img.convert('L')
            return gray

        mode_lower = mode.lower()

        if mode_lower == "red":
            return r
        elif mode_lower == "green":
            return g
        elif mode_lower == "blue":
            return b
        elif mode_lower == "alpha":
            return a if a else Image.new('L', img.size, 255)
        elif mode_lower == "gray":
            return Image.merge('RGB', (r, g, b)).convert('L')
        elif mode_lower == "magenta":
            merged = Image.merge('RGB', (r, g, Image.new('L', img.size, 0)))
            return merged.convert('L')
        elif mode_lower == "cyan":
            merged = Image.merge('RGB', (Image.new('L', img.size, 0), g, b))
            return merged.convert('L')
        elif mode_lower == "yellow":
            merged = Image.merge('RGB', (r, g, Image.new('L', img.size, 0)))
            return merged.convert('L')
        else:
            return img.convert('L')

    @staticmethod
    def get_bit_plane(img: Image.Image, bit: int) -> Image.Image:
        """提取指定位平面 (0-7)"""
        StegsolveAnalyzer.require_pil()

        if img.mode not in ('L', 'RGB', 'RGBA'):
            img = img.convert('RGB')

        if img.mode == 'L':
            channels = [img]
        else:
            channels = list(img.split())

        result_channels = []
        for channel in channels:
            channel_array = list(channel.getdata())
            bit_mask = 1 << bit
            new_values = []
            for val in channel_array:
                if isinstance(val, tuple):
                    val = val[0]
                new_val = 255 if (val & bit_mask) else 0
                new_values.append(new_val)

            new_channel = Image.new('L', channel.size)
            new_channel.putdata(new_values)
            result_channels.append(new_channel)

        if len(result_channels) == 1:
            return result_channels[0]
        return Image.merge('RGB', result_channels[:3])

    @staticmethod
    def apply_lut(img: Image.Image, lut_name: str) -> Image.Image:
        """应用颜色查找表"""
        StegsolveAnalyzer.require_pil()

        if lut_name == "invert":
            return ImageOps.invert(img.convert('RGB')).convert('L')
        elif lut_name.startswith("threshold"):
            threshold = int(lut_name.split("_")[1])
            return ImageOps.autocontrast(img, cutoff=(0, 100-threshold))
        elif lut_name == "solarize":
            return ImageOps.solarize(img, threshold=128)
        elif lut_name == "equalize":
            return ImageOps.equalize(img)
        elif lut_name == "hue_90":
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(0.5)
        elif lut_name == "hue_180":
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(0.0)
        elif lut_name == "hue_270":
            return img
        else:
            return img

    @staticmethod
    def extract_frames(path: str) -> List[Image.Image]:
        """提取GIF的所有帧"""
        StegsolveAnalyzer.require_pil()
        img = Image.open(path)

        if img.format != 'GIF':
            return [img]

        frames = []
        try:
            while True:
                frames.append(img.copy())
                img.seek(img.tell() + 1)
        except EOFError:
            pass

        return frames

    @staticmethod
    def extract_lsb_data(path: str, plane: int = 0, bit_index: int = 0) -> str:
        """提取LSB数据"""
        StegsolveAnalyzer.require_pil()
        img = Image.open(path).convert('RGB')
        pixels = list(img.getdata())

        bits = []
        for pixel in pixels:
            byte_val = pixel[plane % 3]
            bit = (byte_val >> bit_index) & 1
            bits.append(str(bit))

        result = []
        for i in range(0, len(bits) - 7, 8):
            byte = bits[i:i+8]
            int_val = int(''.join(byte), 2)
            if int_val == 0:
                break
            if 32 <= int_val < 127:
                result.append(chr(int_val))
            else:
                result.append(f'\\x{int_val:02x}')

        return ''.join(result)

    @staticmethod
    def get_lsb_binary_data(path: str, bit_index: int = 0) -> str:
        """获取LSB二进制数据表示"""
        StegsolveAnalyzer.require_pil()
        img = Image.open(path).convert('RGB')
        width, height = img.size
        pixels = list(img.getdata())

        lines = []
        bits_per_line = width * 8

        all_bits = []
        for pixel in pixels:
            byte_val = pixel[0]
            bit = (byte_val >> bit_index) & 1
            all_bits.append(str(bit))

        for i in range(0, len(all_bits), bits_per_line):
            line_bits = all_bits[i:i+bits_per_line]
            if len(line_bits) < bits_per_line:
                line_bits.extend(['0'] * (bits_per_line - len(line_bits)))
            hex_line = f"{int(''.join(line_bits[:8]), 2):02x} {int(''.join(line_bits[8:16]), 2):02x} {int(''.join(line_bits[16:24]), 2):02x} {int(''.join(line_bits[24:32]), 2):02x}..."
            ascii_repr = ''.join(chr(int(''.join(line_bits[j:j+8]), 2)) if 32 <= int(''.join(line_bits[j:j+8]), 2) < 127 else '.' for j in range(0, min(32, len(line_bits)), 8))
            lines.append(f"{hex_line}  {ascii_repr}")

        return '\n'.join(lines)

    @staticmethod
    def mix_channels(img: Image.Image, r_weight: float = 1.0, g_weight: float = 0.0, b_weight: float = 0.0) -> Image.Image:
        """通道混合"""
        StegsolveAnalyzer.require_pil()

        if img.mode != 'RGB':
            img = img.convert('RGB')

        r, g, b = img.split()

        r_data = list(r.getdata())
        g_data = list(g.getdata())
        b_data = list(b.getdata())

        mixed = []
        for i in range(len(r_data)):
            val = int(r_data[i] * r_weight + g_data[i] * g_weight + b_data[i] * b_weight)
            val = max(0, min(255, val))
            mixed.append(val)

        result = Image.new('L', img.size)
        result.putdata(mixed)
        return result

    @staticmethod
    def calculate_histogram(img: Image.Image) -> dict:
        """计算直方图"""
        StegsolveAnalyzer.require_pil()

        if img.mode == 'RGBA':
            img = img.convert('RGB')
        elif img.mode == 'L':
            img = img.convert('RGB')

        r, g, b = img.split()

        hist_r = r.histogram()
        hist_g = g.histogram()
        hist_b = b.histogram()

        return {
            'r': hist_r,
            'g': hist_g,
            'b': hist_b,
            'gray': ImageOps.grayscale(img).histogram()
        }

    @staticmethod
    def hough_line_detection(img: Image.Image) -> List[Tuple[int, int, int]]:
        """霍夫变换检测直线 - 简化版"""
        StegsolveAnalyzer.require_pil()

        if img.mode != 'L':
            img = img.convert('L')

        edges = img.filter(ImageFilter.FIND_EDGES)

        lines = []
        width, height = img.size

        pixels = list(edges.getdata())
        edge_points = [(i % width, i // width) for i, p in enumerate(pixels) if isinstance(p, int) and p > 50 or not isinstance(p, int) and p[0] > 50]

        accumulator = {}

        for x, y in edge_points[:1000]:
            for theta in range(0, 180, 2):
                rho = int(x * (theta / 180.0 * 3.14159) + y * (1 - theta / 180.0 * 3.14159))
                key = (rho, theta)
                accumulator[key] = accumulator.get(key, 0) + 1

        sorted_lines = sorted(accumulator.items(), key=lambda x: x[1], reverse=True)
        return [(rho, theta, votes) for (rho, theta), votes in sorted_lines[:10]]

    @staticmethod
    def zoom_image(img: Image.Image, factor: float) -> Image.Image:
        """缩放图像"""
        StegsolveAnalyzer.require_pil()
        width, height = img.size
        new_size = (int(width * factor), int(height * factor))
        return img.resize(new_size, Image.Resampling.LANCZOS)

    @staticmethod
    def compare_channels(img: Image.Image) -> dict:
        """比较RGB通道差异"""
        StegsolveAnalyzer.require_pil()

        if img.mode != 'RGB' and img.mode != 'RGBA':
            img = img.convert('RGB')

        r, g, b = img.split()

        r_data = list(r.getdata())
        g_data = list(g.getdata())
        b_data = list(b.getdata())

        diff_rg = sum(1 for i in range(len(r_data)) if abs(r_data[i] - g_data[i]) > 10)
        diff_rb = sum(1 for i in range(len(r_data)) if abs(r_data[i] - b_data[i]) > 10)
        diff_gb = sum(1 for i in range(len(g_data)) if abs(g_data[i] - b_data[i]) > 10)

        return {
            'diff_rg': diff_rg,
            'diff_rb': diff_rb,
            'diff_gb': diff_gb,
            'total_pixels': len(r_data)
        }
