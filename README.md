# CTF Misc 牛马工具箱 🐮🐴

基于 **PyQt5** 的 CTF 杂项（Misc）综合解题工具，集成编码解码、古典密码、哈希、文件分析、图片隐写（Stegsolve）、智能链式解码等常用能力。

界面采用可爱粉色主题，左侧有动态 **牛马** mascot 为你打工加油。

## 功能模块

| 模块 | 能力 |
|------|------|
| **编解码** | Base16/32/36/58/62/64/85/91、Hex、URL、HTML、Unicode、ASCII 进制、QP、UU、Shellcode、XXencode、ROT47、Brainfuck/Ook、零宽字符 |
| **古典密码** | 凯撒、ROT5/13/18、Atbash、摩斯、培根、栅栏(2-20栏)、维吉尼亚、仿射(含暴力破解)、键盘密码(横/纵/手机)、A1Z26、敲击码、猪圈、核心价值观、XOR单字节/重复密钥、字频分析 |
| **哈希** | MD5/SHA1/SHA224/SHA256/SHA384/SHA512 计算、哈希类型识别、HMAC-SHA256 |
| **文件分析** | 魔数类型识别(30+格式)、strings提取(ASCII/UTF-8)、Hex预览(格式化)、Flag搜索(多模式)、单字节XOR/重复密钥XOR爆破、嵌入文件扫描 |
| **隐写分析** | EXIF/元数据、LSB三通道提取、RGB LSB全通道提取、Flag自动提取、尾部附加数据、零宽字符解码、**Stegsolve完整功能**(通道查看、位平面分析、颜色查找表、帧查看、数据提取、通道混合、直方图) |
| **智能解码** | 自动尝试多种编码/密码链（类 Ciphey 轻量版） |
| **杂项** | 任意进制转换、QR码生成/解码、Flag格式匹配、Base64文件传输 |

## 界面预览

```
┌─────────────────────────────────────────────────────────┐
│  🐮  CTF Misc 牛马工具箱                    [─][□][×]   │
├────────┬────────────────────────────────────────────────┤
│        │  ┌──────────────────────────────────────────┐  │
│  🐴    │  │  编码解码 │ 古典密码 │ 哈希 │ 文件分析  │  │
│        │  │  隐写分析 │ 智能解码 │ 杂项            │  │
│  牛马  │  ├──────────────────────────────────────────┤  │
│  mascot│  │                                          │  │
│        │  │         [功能界面区]                       │  │
│        │  │                                          │  │
│        │  │                                          │  │
│        │  └──────────────────────────────────────────┘  │
└────────┴────────────────────────────────────────────────┘
```

### 隐写分析 - Stegsolve 功能详情

| 标签页 | 功能说明 |
|--------|----------|
| 通道查看 | Red/Green/Blue/Gray/Magenta/Cyan/Yellow/Alpha 通道提取 |
| 位平面 | 0-7 位平面提取，分析 LSB 隐写 |
| 颜色查找表 | 反转、阈值(64/128/192)、Solarize、均衡化 |
| 帧查看 | GIF 动画帧提取，逐帧查看保存 |
| 数据提取 | LSB 二进制数据提取，支持位索引选择 |
| 通道混合 | RGB 通道权重混合，滑块控制 |
| 直方图 | RGB/灰度通道统计，差异分析 |
| 基础功能 | EXIF、LSB三通道、尾部数据、零宽解码、**RGB LSB提取**、**Flag自动提取** |

### 文件分析 - 增强功能

| 功能 | 说明 |
|------|------|
| 魔数识别 | 支持 PNG/JPEG/GIF/ZIP/RAR/ELF/PE/PDF/GZIP/BZIP2/7Z/SQLite 等30+格式 |
| strings | 支持 ASCII/UTF-8 双编码，自动去重排序 |
| Hex预览 | 格式化显示(偏移+十六进制+ASCII)，类似010 Editor |
| Flag搜索 | 支持 flag{} / ctf{} / key{} / MD5/SHA / Base64 等多模式 |
| XOR爆破 | 单字节/重复密钥，支持2-16位密钥长度 |
| 嵌入扫描 | 扫描文件内嵌的签名，定位隐藏文件 |

## 安装与运行

### 方式一：直接运行 EXE

```bash
# 解压并直接运行
dist\MiscTool.exe
```

### 方式二：从源码运行

```bash
cd CTFtools
pip install -r requirements.txt
python main.py
```

### 打包命令

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "MiscTool" --icon="logo.ico" main.py
```

## 依赖说明

- **PyQt5** — 图形界面
- **Pillow** — 图片处理/隐写
- **qrcode** — 二维码生成
- **pyzbar** — 二维码解码（Windows 需额外安装 [zbar](https://github.com/mchehab/zbar/releases)）

## 运行测试

```bash
python tests/test_modules.py
```

22 项单元测试覆盖编解码 roundtrip、古典密码、哈希、智能解码等核心逻辑。

## 项目结构

```
CTFtools/
├── main.py                 # 启动入口
├── logo.ico                # 程序图标
├── requirements.txt        # 依赖
├── MiscTool.spec           # PyInstaller 配置
├── modules/                # 后端逻辑
│   ├── encoding/           # 编解码模块
│   │   ├── base_codec.py   # Base系列/URL/Hex
│   │   ├── text_codec.py    # Unicode/HTML/ASCII
│   │   └── esoteric.py       # Brainfuck/Ook
│   ├── cipher/              # 古典密码
│   │   ├── classical.py      # 凯撒/栅栏/维吉尼亚等
│   │   └── extra.py          # 摩斯/培根/猪圈等
│   ├── hash/                # 哈希模块
│   │   └── hash_tools.py    # MD5/SHA/HMAC
│   ├── file/                # 文件分析
│   │   └── file_tools.py    # 魔数/strings/XOR/binwalk
│   ├── stego/               # 隐写分析
│   │   └── image_stego.py   # LSB/EXIF/Stegsolve
│   ├── auto/                # 智能解码
│   │   └── smart_decode.py  # Ciphey风格
│   └── misc/                # 杂项工具
│       └── utilities.py     # 进制转换/QR码
└── ui/                     # PyQt5 界面
    ├── main_window.py       # 主窗口
    ├── mascot_widget.py     # 动态牛马
    ├── styles.py            # 样式
    └── pages/               # 各功能页
        ├── encoding_page.py
        ├── cipher_page.py
        ├── hash_page.py
        ├── file_page.py
        ├── stego_page.py
        ├── auto_page.py
        └── misc_page.py
```

## 更新日志

### v2.0 (2026-05-28)
- 集成 Stegsolve 完整隐写分析功能（8个标签页）
- 新增 RGB LSB 全通道提取和 Flag 自动提取
- 优化文件分析界面和功能（魔数识别增强、格式化 Hex 预览）
- 添加 XOR 爆破可调参数（数据长度、密钥长度）
- UI 界面优化，按钮配色分组

### v1.0 (2026-05-27)
- 初始版本，包含基础编解码、古典密码、哈希、文件分析、隐写分析
- 粉色可爱主题 + 动态牛马 mascot
