"""可爱牛马 mascot 动画组件"""
import math
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtWidgets import QWidget


class MascotWidget(QWidget):
    """手绘风格动态牛马 — CTF 打工仔"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 220)
        self._frame = 0
        self._blink = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(80)
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._do_blink)
        self._blink_timer.start(2800)

    def _tick(self):
        self._frame = (self._frame + 1) % 60
        self.update()

    def _do_blink(self):
        self._blink = True
        self.update()
        QTimer.singleShot(150, self._unblink)

    def _unblink(self):
        self._blink = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # 背景气泡
        p.setBrush(QBrush(QColor("#FFE0F0")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(10, 30, w - 20, h - 50)

        t = self._frame / 60.0 * 2 * math.pi
        bounce = math.sin(t * 2) * 4
        leg_swing = math.sin(t * 4) * 12

        cx, cy = w / 2, h / 2 + bounce - 10

        # 尾巴
        p.setPen(QPen(QColor("#8B6914"), 3))
        p.drawArc(int(cx + 35), int(cy - 5), 30, 25, 30 * 16, 120 * 16)

        # 身体（牛马棕）
        p.setBrush(QBrush(QColor("#C49A3C")))
        p.setPen(QPen(QColor("#8B6914"), 2))
        p.drawEllipse(QRectF(cx - 42, cy - 20, 84, 70))

        # 肚皮
        p.setBrush(QBrush(QColor("#E8C878")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(cx - 28, cy - 5, 56, 45))

        # 腿（四腿小跑）
        p.setPen(QPen(QColor("#8B6914"), 3))
        for i, side in enumerate([-1, 1]):
            for j, phase in enumerate([0, math.pi]):
                angle = leg_swing * side + phase
                lx = cx + side * (18 + j * 8)
                ly = cy + 38
                ex = lx + math.sin(math.radians(angle)) * 8
                ey = ly + 22 + abs(math.cos(math.radians(angle))) * 4
                p.drawLine(int(lx), int(ly), int(ex), int(ey))
                p.setBrush(QBrush(QColor("#6B4A10")))
                p.drawEllipse(QRectF(ex - 6, ey - 4, 12, 8))

        # 头（马头 + 牛耳）
        p.setBrush(QBrush(QColor("#D4AA48")))
        p.setPen(QPen(QColor("#8B6914"), 2))
        p.drawEllipse(QRectF(cx - 38, cy - 58, 76, 62))

        # 牛耳
        p.setBrush(QBrush(QColor("#E8B84A")))
        for side in [-1, 1]:
            ear = QPointF(cx + side * 32, cy - 52)
            p.drawEllipse(QRectF(ear.x() - 10, ear.y() - 18, 18, 28))

        # 马鬃
        p.setPen(QPen(QColor("#5C4010"), 2))
        for i in range(5):
            px = cx - 20 + i * 10
            py = cy - 55 - math.sin(t * 3 + i) * 3
            p.drawLine(int(px), int(py), int(px + 2), int(py - 14))

        # 眼睛
        eye_y = cy - 32
        for side in [-1, 1]:
            ex = cx + side * 14
            p.setBrush(QBrush(QColor("#FFFFFF")))
            p.setPen(QPen(QColor("#333"), 1))
            p.drawEllipse(QRectF(ex - 9, eye_y - 9, 18, 18))
            if self._blink:
                p.setPen(QPen(QColor("#333"), 2))
                p.drawLine(int(ex - 7), int(eye_y), int(ex + 7), int(eye_y))
            else:
                p.setBrush(QBrush(QColor("#333")))
                p.drawEllipse(QRectF(ex - 4, eye_y - 4, 8, 8))
                p.setBrush(QBrush(QColor("#FFF")))
                p.drawEllipse(QRectF(ex - 1, eye_y - 5, 3, 3))

        # 腮红
        p.setBrush(QBrush(QColor(255, 150, 180, 120)))
        p.setPen(Qt.NoPen)
        for side in [-1, 1]:
            p.drawEllipse(QRectF(cx + side * 26 - 10, cy - 18, 20, 12))

        # 鼻子
        p.setBrush(QBrush(QColor("#FF9EC7")))
        p.drawEllipse(QRectF(cx - 8, cy - 18, 16, 12))

        # 嘴巴
        p.setPen(QPen(QColor("#8B4513"), 2))
        p.drawArc(int(cx - 12), int(cy - 12), 24, 14, 200 * 16, 140 * 16)

        # 角（小牛叉）— 牛马特色
        p.setPen(QPen(QColor("#DDD"), 2))
        p.setBrush(QBrush(QColor("#F0E8D8")))
        for side in [-1, 1]:
            p.drawEllipse(QRectF(cx + side * 8 - 3, cy - 68, 6, 14))

        # 汗滴（打工象征）
        if self._frame % 30 < 15:
            p.setBrush(QBrush(QColor(120, 180, 255, 180)))
            p.drawEllipse(QRectF(cx + 42, cy - 45, 8, 12))

        # 对话框
        p.setBrush(QBrush(QColor("#FFFFFF")))
        p.setPen(QPen(QColor("#FFB8D9"), 2))
        bubble = QRectF(8, 4, w - 16, 36)
        p.drawRoundedRect(bubble, 10, 10)
        p.setPen(QColor("#D44A8A"))
        p.setFont(QFont("Microsoft YaHei UI", 9, QFont.Bold))
        msgs = [
            "冲啊拿 flag! 🚩",
            "Misc 全能打工马~",
            "解码中...别催!",
            "牛马出征,寸草不生",
            "CyberChef? 有我快!",
        ]
        p.drawText(bubble, Qt.AlignCenter, msgs[(self._frame // 12) % len(msgs)])

        p.end()
