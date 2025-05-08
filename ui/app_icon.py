#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序图标模块

提供应用程序的主图标。
"""

from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen, QFont, QLinearGradient
from PyQt6.QtCore import Qt, QSize, QRect, QPoint

def create_app_icon():
    """
    创建应用程序图标
    
    Returns:
        QIcon对象
    """
    # 创建一个64x64的图标
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 创建渐变背景
    gradient = QLinearGradient(0, 0, 64, 64)
    gradient.setColorAt(0, QColor("#4a86e8"))
    gradient.setColorAt(1, QColor("#3a76d8"))
    
    # 绘制圆形背景
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    
    # 绘制AI文字
    painter.setPen(QPen(QColor("#ffffff"), 2))
    font = QFont("Arial", 24, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, 64, 64), Qt.AlignmentFlag.AlignCenter, "AI")
    
    # 绘制笔画
    pen = QPen(QColor("#ffffff"), 2)
    painter.setPen(pen)
    painter.drawLine(16, 44, 48, 44)
    painter.drawLine(16, 48, 48, 48)
    
    # 结束绘制
    painter.end()
    
    return QIcon(pixmap)

def set_app_icon(app):
    """
    设置应用程序图标
    
    Args:
        app: QApplication实例
    """
    app.setWindowIcon(create_app_icon())
