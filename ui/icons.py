#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图标模块

提供应用程序的图标资源。
"""

from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen, QFont
from PyQt6.QtCore import Qt, QSize, QRect, QPoint

def create_colored_icon(color, size=24):
    """
    创建纯色图标

    Args:
        color: 颜色
        size: 图标大小

    Returns:
        QIcon对象
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)

def get_new_icon():
    """获取新建图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制新建文档图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.drawRect(4, 4, 16, 16)
    painter.drawLine(8, 10, 16, 10)
    painter.drawLine(8, 14, 16, 14)

    # 结束绘制
    painter.end()

    return QIcon(pixmap)

def get_open_icon():
    """获取打开图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制文件夹图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#e0e0e0")))
    painter.drawRect(3, 6, 18, 14)
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.drawRect(6, 4, 8, 4)

    # 结束绘制
    painter.end()

    return QIcon(pixmap)

def get_save_icon():
    """获取保存图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制保存图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#4a86e8")))
    painter.drawRect(4, 4, 16, 16)
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.drawRect(8, 8, 8, 8)
    painter.drawRect(10, 4, 4, 6)

    # 结束绘制
    painter.end()

    return QIcon(pixmap)

def get_stats_icon():
    """获取统计图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制统计图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#4a86e8")))
    painter.drawRect(4, 14, 4, 6)
    painter.drawRect(10, 10, 4, 10)
    painter.drawRect(16, 6, 4, 14)

    # 结束绘制
    painter.end()

    return QIcon(pixmap)

def get_theme_icon():
    """获取主题图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制主题图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#4a86e8")))
    painter.drawEllipse(4, 4, 16, 16)
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.drawEllipse(4, 4, 8, 8)

    # 结束绘制
    painter.end()

    return QIcon(pixmap)

def get_help_icon():
    """获取帮助图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制帮助图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#4a86e8")))
    painter.drawEllipse(4, 4, 16, 16)
    painter.setPen(QPen(QColor("#ffffff"), 1))
    painter.setBrush(QBrush(QColor("#ffffff")))

    # 设置字体
    font = QFont("Arial", 12, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRect(4, 4, 16, 16), Qt.AlignmentFlag.AlignCenter, "?")

    # 结束绘制
    painter.end()

    return QIcon(pixmap)

def get_about_icon():
    """获取关于图标"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制关于图标
    painter.setPen(QPen(QColor("#4a86e8"), 1))
    painter.setBrush(QBrush(QColor("#4a86e8")))
    painter.drawEllipse(4, 4, 16, 16)
    painter.setPen(QPen(QColor("#ffffff"), 1))
    painter.setBrush(QBrush(QColor("#ffffff")))

    # 设置字体
    font = QFont("Arial", 12, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRect(4, 4, 16, 16), Qt.AlignmentFlag.AlignCenter, "i")

    # 结束绘制
    painter.end()

    return QIcon(pixmap)
