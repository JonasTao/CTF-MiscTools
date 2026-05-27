# CTF Misc 牛马工具箱 🐮🐴

基于 **PyQt5** 的 CTF 杂项（Misc）综合解题工具，集成编码解码、古典密码、哈希、文件分析、图片隐写、智能链式解码等常用能力。

界面采用可爱粉色主题，左侧有动态 **牛马** mascot 为你打工加油。

## 功能模块

| 模块 | 能力 |
|------|------|
| 编解码 | Base16/32/36/58/62/64/85/91、Hex、URL、HTML、Unicode、ASCII 进制、QP、UU、Shellcode、XXencode、ROT47、Brainfuck/Ook |
| 古典密码 | 凯撒、ROT5/13/18、Atbash、摩斯、培根、栅栏、维吉尼亚、仿射（含暴力）、键盘密码、A1Z26、敲击码、猪圈、核心价值观、XOR、字频分析 |
| 哈希 | MD5/SHA 系列计算、哈希类型识别、HMAC-SHA256 |
| 文件分析 | 魔数类型识别、strings、Hex 预览、Flag 搜索、单字节 XOR、简易 binwalk |
| 隐写分析 | EXIF、LSB 三通道、PNG/JPEG 尾部数据、零宽字符解码 |
| 智能解码 | 自动尝试多种编码/密码链（类 Ciphey 轻量版） |
| 杂项 | 任意进制转换、QR 生成/解码、Flag 格式匹配 |

## 安装与运行

```bash
cd CTFtools
pip install -r requirements.txt
python main.py
```

## 运行测试

```bash
python tests/test_modules.py
```

22 项单元测试覆盖编解码 roundtrip、古典密码、哈希、智能解码等核心逻辑。

### 依赖说明

- **PyQt5** — 界面
- **Pillow** — 图片/隐写
- **qrcode** — 二维码生成
- **pyzbar** — 二维码解码（Windows 需额外安装 [zbar](https://github.com/mchehab/zbar/releases)）

## 项目结构

```
CTFtools/
├── main.py                 # 启动入口
├── requirements.txt
├── modules/                # 后端逻辑
│   ├── encoding/           # 编解码
│   ├── cipher/             # 古典密码
│   ├── hash/               # 哈希
│   ├── file/               # 文件分析
│   ├── stego/              # 隐写
│   ├── auto/               # 智能解码
│   └── misc/               # 杂项
└── ui/                     # PyQt5 界面
    ├── main_window.py
    ├── mascot_widget.py    # 动态牛马
    ├── styles.py
    └── pages/              # 各功能页
```

## 参考思路

本工具参考了 CyberChef、CTF-Knife、CTFCrackTools、SecToolKit 等项目的功能划分，将 Misc 高频操作整合到本地桌面端，便于离线比赛使用。

## 扩展

可在 `modules/` 下新增子模块，并在 `ui/pages/` 添加对应页面，于 `ui/main_window.py` 的 `NAV_ITEMS` 注册即可。
