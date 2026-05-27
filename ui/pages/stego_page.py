from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QTabWidget, QComboBox,
                             QSpinBox, QTextEdit, QSlider, QGroupBox, QCheckBox,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtWidgets import QMessageBox
import io

from ui.tool_base import ToolPage
from modules.stego.image_stego import ImageStego, StegsolveAnalyzer


class ImageViewer(QLabel):
    """图像查看器控件"""
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        self.setMinimumSize(400, 300)
        self.current_pixmap = None

    def set_image(self, img):
        """设置要显示的图像"""
        if img is None:
            self.clear()
            return

        width, height = img.size
        if width > 800 or height > 600:
            ratio = min(800/width, 600/height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size)

        if img.mode == 'L':
            qimg = QImage(img.tobytes(), width, height, width, QImage.Format_Grayscale8)
        elif img.mode == 'RGB':
            qimg = QImage(img.tobytes(), width, height, width * 3, QImage.Format_RGB888)
        elif img.mode == 'RGBA':
            qimg = QImage(img.tobytes(), width, height, width * 4, QImage.Format_RGBA8888)
        else:
            img = img.convert('RGB')
            qimg = QImage(img.tobytes(), width, height, width * 3, QImage.Format_RGB888)

        self.current_pixmap = QPixmap.fromImage(qimg)
        self.setPixmap(self.current_pixmap)


class StegoPage(ToolPage):
    def __init__(self):
        super().__init__("隐写分析")
        self._path = ""
        self.current_image = None
        self.current_frames = []

        main_layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        self.path_label = QLabel("未选择图片")
        file_layout.addWidget(self.path_label)
        b = QPushButton("选择图片")
        b.clicked.connect(self._pick)
        file_layout.addWidget(b)
        main_layout.addLayout(file_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tabs.addTab(self._create_channel_tab(), "通道查看")
        self.tabs.addTab(self._create_bitplane_tab(), "位平面")
        self.tabs.addTab(self._create_lut_tab(), "颜色查找表")
        self.tabs.addTab(self._create_frame_tab(), "帧查看")
        self.tabs.addTab(self._create_extract_tab(), "数据提取")
        self.tabs.addTab(self._create_mixer_tab(), "通道混合")
        self.tabs.addTab(self._create_histogram_tab(), "直方图")
        self.tabs.addTab(self._create_basic_tab(), "基础功能")

        self.image_viewer = ImageViewer()
        main_layout.addWidget(self.image_viewer)

    def _create_channel_tab(self) -> QWidget:
        """创建通道查看标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("通道模式:"))

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["Red", "Green", "Blue", "Gray",
                                     "Magenta", "Cyan", "Yellow", "Alpha"])
        controls.addWidget(self.channel_combo)

        b = QPushButton("应用")
        b.clicked.connect(self._apply_channel)
        controls.addWidget(b)
        controls.addStretch()

        layout.addLayout(controls)
        return widget

    def _create_bitplane_tab(self) -> QWidget:
        """创建位平面标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("位平面:"))

        self.bitplane_spin = QSpinBox()
        self.bitplane_spin.setRange(0, 7)
        self.bitplane_spin.setValue(0)
        controls.addWidget(self.bitplane_spin)

        b = QPushButton("提取位平面")
        b.clicked.connect(self._extract_bitplane)
        controls.addWidget(b)

        layout.addLayout(controls)
        return widget

    def _create_lut_tab(self) -> QWidget:
        """创建颜色查找表标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("LUT预设:"))

        self.lut_combo = QComboBox()
        self.lut_combo.addItems([
            "Reverse", "Threshold 128", "Threshold 64", "Threshold 32",
            "Threshold 16", "Threshold 8", "Threshold 4", "Threshold 2", "Threshold 1",
            "Solarize", "Equalize"
        ])
        controls.addWidget(self.lut_combo)

        b = QPushButton("应用LUT")
        b.clicked.connect(self._apply_lut)
        controls.addWidget(b)
        controls.addStretch()

        layout.addLayout(controls)
        return widget

    def _create_frame_tab(self) -> QWidget:
        """创建帧查看标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("帧:"))

        self.frame_spin = QSpinBox()
        self.frame_spin.setRange(0, 0)
        self.frame_spin.valueChanged.connect(self._show_frame)
        controls.addWidget(self.frame_spin)

        b = QPushButton("提取所有帧")
        b.clicked.connect(self._extract_frames)
        controls.addWidget(b)

        b2 = QPushButton("保存当前帧")
        b2.clicked.connect(self._save_current_frame)
        controls.addWidget(b2)
        controls.addStretch()

        layout.addLayout(controls)
        return widget

    def _create_extract_tab(self) -> QWidget:
        """创建数据提取标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("位索引:"))

        self.extract_bit_spin = QSpinBox()
        self.extract_bit_spin.setRange(0, 7)
        self.extract_bit_spin.setValue(0)
        controls.addWidget(self.extract_bit_spin)

        controls.addWidget(QLabel("通道:"))
        self.extract_channel_combo = QComboBox()
        self.extract_channel_combo.addItems(["Red", "Green", "Blue"])
        controls.addWidget(self.extract_channel_combo)

        b = QPushButton("提取LSB数据")
        b.clicked.connect(self._extract_lsb_data)
        controls.addWidget(b)

        controls.addStretch()
        layout.addLayout(controls)

        self.extract_output = QTextEdit()
        self.extract_output.setMaximumHeight(150)
        layout.addWidget(self.extract_output)

        return widget

    def _create_mixer_tab(self) -> QWidget:
        """创建通道混合标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("R:"))
        self.mixer_r = QSlider(Qt.Horizontal)
        self.mixer_r.setRange(0, 100)
        self.mixer_r.setValue(100)
        controls.addWidget(self.mixer_r)
        controls.addWidget(QLabel("0"))

        controls.addWidget(QLabel("G:"))
        self.mixer_g = QSlider(Qt.Horizontal)
        self.mixer_g.setRange(0, 100)
        self.mixer_g.setValue(0)
        controls.addWidget(self.mixer_g)
        controls.addWidget(QLabel("0"))

        controls.addWidget(QLabel("B:"))
        self.mixer_b = QSlider(Qt.Horizontal)
        self.mixer_b.setRange(0, 100)
        self.mixer_b.setValue(0)
        controls.addWidget(self.mixer_b)
        controls.addWidget(QLabel("0"))

        b = QPushButton("混合")
        b.clicked.connect(self._mix_channels)
        controls.addWidget(b)
        controls.addStretch()

        layout.addLayout(controls)
        return widget

    def _create_histogram_tab(self) -> QWidget:
        """创建直方图标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        b = QPushButton("计算直方图")
        b.clicked.connect(self._calculate_histogram)
        controls.addWidget(b)

        controls.addStretch()
        layout.addLayout(controls)

        self.histogram_output = QTextEdit()
        self.histogram_output.setReadOnly(True)
        layout.addWidget(self.histogram_output)

        return widget

    def _create_basic_tab(self) -> QWidget:
        """创建基础功能标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.text_inp = self.input_box("零宽字符文本 / 或留空使用图片分析")
        layout.addWidget(QLabel("文本隐写 / 图片路径"))
        layout.addWidget(self.text_inp)

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

        row3 = QHBoxLayout()
        b = QPushButton("RGB LSB 提取")
        b.clicked.connect(self._lsb_all_channels)
        row3.addWidget(b)

        b = QPushButton("提取 Flag")
        b.clicked.connect(self._lsb_extract_flag)
        row3.addWidget(b)
        row3.addStretch()
        layout.addLayout(row3)

        self.out = self.output_box()
        layout.addWidget(self.out)
        layout.addLayout(self.io_toolbar(self.text_inp, self.out))

        return widget

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff)"
        )
        if path:
            self._path = path
            self.path_label.setText(path)
            self._load_image()

    def _load_image(self):
        try:
            self.current_image = StegsolveAnalyzer.load_image(self._path)
            self.image_viewer.set_image(self.current_image)

            if self.current_image.format == 'GIF':
                self.current_frames = StegsolveAnalyzer.extract_frames(self._path)
                self.frame_spin.setRange(0, len(self.current_frames) - 1)
        except Exception as e:
            self.show_error(self, f"加载图片失败: {str(e)}")

    def _apply_channel(self):
        if not self.current_image:
            self.show_error(self, "请先选择图片")
            return
        try:
            mode = self.channel_combo.currentText()
            channel_img = StegsolveAnalyzer.get_channel_image(self.current_image, mode)
            self.image_viewer.set_image(channel_img)
        except Exception as e:
            self.show_error(self, str(e))

    def _extract_bitplane(self):
        if not self.current_image:
            self.show_error(self, "请先选择图片")
            return
        try:
            bit = self.bitplane_spin.value()
            bitplane_img = StegsolveAnalyzer.get_bit_plane(self.current_image, bit)
            self.image_viewer.set_image(bitplane_img)
        except Exception as e:
            self.show_error(self, str(e))

    def _apply_lut(self):
        if not self.current_image:
            self.show_error(self, "请先选择图片")
            return
        try:
            lut_name = self.lut_combo.currentText()
            lut_img = StegsolveAnalyzer.apply_lut(self.current_image, lut_name)
            self.image_viewer.set_image(lut_img)
        except Exception as e:
            self.show_error(self, str(e))

    def _extract_frames(self):
        if not self._path:
            self.show_error(self, "请先选择图片")
            return
        try:
            self.current_frames = StegsolveAnalyzer.extract_frames(self._path)
            self.frame_spin.setRange(0, len(self.current_frames) - 1)
            if self.current_frames:
                self.image_viewer.set_image(self.current_frames[0])
            QMessageBox.information(self, "成功", f"已提取 {len(self.current_frames)} 帧")
        except Exception as e:
            self.show_error(self, str(e))

    def _show_frame(self):
        if not self.current_frames:
            return
        idx = self.frame_spin.value()
        if 0 <= idx < len(self.current_frames):
            self.image_viewer.set_image(self.current_frames[idx])

    def _save_current_frame(self):
        if not self.current_frames:
            self.show_error(self, "请先提取帧")
            return
        idx = self.frame_spin.value()
        path, _ = QFileDialog.getSaveFileName(
            self, "保存帧", f"frame_{idx}.png", "PNG (*.png)"
        )
        if path:
            self.current_frames[idx].save(path)

    def _extract_lsb_data(self):
        if not self._path:
            self.show_error(self, "请先选择图片")
            return
        try:
            bit_idx = self.extract_bit_spin.value()
            channel = self.extract_channel_combo.currentIndex()
            data = StegsolveAnalyzer.get_lsb_binary_data(self._path, bit_idx)
            self.extract_output.setPlainText(data[:2000])
        except Exception as e:
            self.extract_output.setPlainText(str(e))

    def _mix_channels(self):
        if not self.current_image:
            self.show_error(self, "请先选择图片")
            return
        try:
            r_w = self.mixer_r.value() / 100.0
            g_w = self.mixer_g.value() / 100.0
            b_w = self.mixer_b.value() / 100.0
            mixed = StegsolveAnalyzer.mix_channels(self.current_image, r_w, g_w, b_w)
            self.image_viewer.set_image(mixed)
        except Exception as e:
            self.show_error(self, str(e))

    def _calculate_histogram(self):
        if not self.current_image:
            self.show_error(self, "请先选择图片")
            return
        try:
            hist = StegsolveAnalyzer.calculate_histogram(self.current_image)

            lines = ["颜色直方图统计:", ""]
            for ch, name in [('gray', '灰度'), ('r', '红色'), ('g', '绿色'), ('b', '蓝色')]:
                data = hist[ch]
                if data:
                    max_val = max(data)
                    mean_val = sum(i * v for i, v in enumerate(data)) / sum(data) if sum(data) > 0 else 0
                    lines.append(f"{name}通道:")
                    lines.append(f"  最大值索引: {data.index(max_val)}")
                    lines.append(f"  均值: {mean_val:.2f}")
                    lines.append(f"  像素总数: {sum(data)}")
                    lines.append("")

            diff = StegsolveAnalyzer.compare_channels(self.current_image)
            lines.append("通道差异分析:")
            lines.append(f"  R-G差异像素: {diff['diff_rg']} ({diff['diff_rg']/diff['total_pixels']*100:.2f}%)")
            lines.append(f"  R-B差异像素: {diff['diff_rb']} ({diff['diff_rb']/diff['total_pixels']*100:.2f}%)")
            lines.append(f"  G-B差异像素: {diff['diff_gb']} ({diff['diff_gb']/diff['total_pixels']*100:.2f}%)")

            self.histogram_output.setPlainText('\n'.join(lines))
        except Exception as e:
            self.histogram_output.setPlainText(str(e))

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

    def _lsb_all_channels(self):
        if not self._path:
            self.show_error(self, "请选择图片")
            return
        try:
            result = ImageStego.lsb_extract_all_channels(self._path)
            lines = [
                f"总位数: {result['total_bits']}",
                f"总字节: {result['total_bytes']}",
                "",
                "=== ASCII 可读内容 ===",
                result['ascii'][:1000] if result['ascii'] else "(无可读ASCII)",
                "",
                "=== Hex 内容 ===",
                result['hex'][:2000],
            ]
            self.out.setPlainText('\n'.join(lines))
        except Exception as e:
            self.out.setPlainText(f"提取失败: {str(e)}")

    def _lsb_extract_flag(self):
        if not self._path:
            self.show_error(self, "请选择图片")
            return
        try:
            flag = ImageStego.lsb_extract_flag(self._path)
            if flag:
                self.out.setPlainText(f"flag{{{flag}}}")
            else:
                self.out.setPlainText("未找到 flag 格式数据")
        except Exception as e:
            self.out.setPlainText(f"提取失败: {str(e)}")
