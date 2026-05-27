from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog

from ui.tool_base import ToolPage
from modules.stego.image_stego import ImageStego


class StegoPage(ToolPage):
    def __init__(self):
        super().__init__("隐写分析")
        layout = QVBoxLayout(self)
        self.path_label = QLabel("未选择图片")
        layout.addWidget(self.path_label)

        row = QHBoxLayout()
        b = QPushButton("选择图片")
        b.clicked.connect(self._pick)
        row.addWidget(b)
        row.addStretch()
        layout.addLayout(row)

        self.text_inp = self.input_box("零宽字符文本 / 或留空使用图片分析")
        layout.addWidget(QLabel("文本隐写 / 图片路径"))
        layout.addWidget(self.text_inp)

        self.out = self.output_box()
        layout.addWidget(self.out)
        layout.addLayout(self.io_toolbar(self.text_inp, self.out))

        row2 = QHBoxLayout()
        for label, fn in [
            ("EXIF/元数据", self._exif),
            ("LSB 三通道", self._lsb),
            ("尾部附加数据", self._trailing),
            ("零宽解码", self._zw),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            row2.addWidget(b)
        layout.addLayout(row2)
        self._path = ""

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            self._path = path
            self.path_label.setText(path)

    def _exif(self):
        if not self._path:
            self.show_error(self, "请选择图片")
            return
        try:
            info = ImageStego.read_exif(self._path)
            lines = [f"尺寸: {info['size']}", f"模式: {info['mode']}", "", "EXIF:"]
            for k, v in info.get("exif", {}).items():
                lines.append(f"  {k}: {v}")
            lines.append("\nInfo:")
            for k, v in info.get("info", {}).items():
                lines.append(f"  {k}: {v}")
            self.out.setPlainText("\n".join(lines))
        except Exception as e:
            self.show_error(self, str(e))

    def _lsb(self):
        if not self._path:
            self.show_error(self, "请选择图片")
            return
        try:
            prev = ImageStego.lsb_preview(self._path)
            lines = [f"=== {ch} ===\n{t}\n" for ch, t in prev.items()]
            self.out.setPlainText("\n".join(lines))
        except Exception as e:
            self.show_error(self, str(e))

    def _trailing(self):
        if not self._path:
            self.show_error(self, "请选择图片")
            return
        try:
            data = ImageStego.extract_trailing_data(self._path)
            if not data:
                self.out.setPlainText("无尾部附加数据")
            else:
                try:
                    self.out.setPlainText(data.decode("utf-8", errors="replace"))
                except Exception:
                    self.out.setPlainText(data.hex())
        except Exception as e:
            self.show_error(self, str(e))

    def _zw(self):
        text = self.text_inp.toPlainText()
        r = ImageStego.zero_width_decode(text)
        self.out.setPlainText(r if r else "未检测到零宽字符隐写")
