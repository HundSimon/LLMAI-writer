#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
样式表模块

提供应用程序的样式定义，包括明亮主题和深色主题。
"""

# 通用样式
COMMON_STYLE = """
/* 全局样式 */
QWidget {
    font-family: "SourceHanSansCN-Normal", "Source Han Sans CN";
    font-size: 10pt;
}

/* 按钮样式 */
QPushButton {
    padding: 6px 12px;
    border-radius: 4px;
    border: 1px solid #cccccc;
    min-height: 24px;
}

QPushButton:hover {
    border: 1px solid #aaaaaa;
}

QPushButton:pressed {
    background-color: #e0e0e0;
}

QPushButton:disabled {
    color: #888888;
    border: 1px solid #dddddd;
    background-color: #f5f5f5;
}

/* 主要按钮样式 */
QPushButton[primary="true"] {
    background-color: #4a86e8;
    color: white;
    border: 1px solid #3a76d8;
}

QPushButton[primary="true"]:hover {
    background-color: #5a96f8;
    border: 1px solid #4a86e8;
}

QPushButton[primary="true"]:pressed {
    background-color: #3a76d8;
}

QPushButton[primary="true"]:disabled {
    background-color: #a0c0f0;
    border: 1px solid #90b0e0;
}

/* 输入框样式 */
QLineEdit, QTextEdit, QPlainTextEdit {
    padding: 4px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: white;
    selection-background-color: #4a86e8;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #4a86e8;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #f5f5f5;
    color: #888888;
}

/* 下拉框样式 */
QComboBox {
    padding: 4px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    min-height: 24px;
}

QComboBox:hover {
    border: 1px solid #aaaaaa;
}

QComboBox:focus {
    border: 1px solid #4a86e8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #cccccc;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
    top: -1px;
}

QTabBar::tab {
    padding: 6px 12px;
    margin-right: 2px;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    background-color: #f5f5f5;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 1px solid white;
}

QTabBar::tab:hover:!selected {
    background-color: #e8e8e8;
}

/* 分组框样式 */
QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}

/* 列表样式 */
QListWidget {
    border: 1px solid #cccccc;
    border-radius: 4px;
    alternate-background-color: #f5f5f5;
}

QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #eeeeee;
}

QListWidget::item:selected {
    background-color: #4a86e8;
    color: white;
}

QListWidget::item:hover:!selected {
    background-color: #e8e8e8;
}

/* 滚动条样式 */
QScrollBar:vertical {
    border: none;
    background: #f0f0f0;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #f0f0f0;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #c0c0c0;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #a0a0a0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 工具栏样式 */
QToolBar {
    border: none;
    background-color: transparent;
    spacing: 6px;
    padding: 3px;
}

QToolBar::separator {
    width: 1px;
    background-color: #cccccc;
    margin: 0 6px;
}

/* 状态栏样式 */
QStatusBar {
    border-top: 1px solid #cccccc;
    background-color: #f5f5f5;
    padding: 2px;
    font-size: 9pt;
}

QStatusBar QLabel {
    padding: 0 4px;
}

/* 进度条样式 */
QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
    background-color: #f5f5f5;
}

QProgressBar::chunk {
    background-color: #4a86e8;
    border-radius: 3px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #cccccc;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #4a86e8;
    border: 1px solid #4a86e8;
}

QCheckBox::indicator:hover {
    border: 1px solid #aaaaaa;
}

/* 单选框样式 */
QRadioButton {
    spacing: 5px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #cccccc;
    border-radius: 8px;
}

QRadioButton::indicator:checked {
    background-color: #4a86e8;
    border: 1px solid #4a86e8;
}

QRadioButton::indicator:hover {
    border: 1px solid #aaaaaa;
}

/* 菜单样式 */
QMenu {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 5px;
}

QMenu::item {
    padding: 5px 25px 5px 20px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #4a86e8;
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #cccccc;
    margin: 5px 0;
}

/* 主窗口样式 */
QMainWindow {
    background-color: white;
}

QMainWindow::separator {
    width: 1px;
    background-color: #cccccc;
}

/* 提示框样式 */
QToolTip {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffcc;
    padding: 5px;
    color: black;
}
"""

# 深色主题样式
DARK_STYLE = """
/* 全局样式 */
QWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    font-family: "SourceHanSansCN-Normal", "Source Han Sans CN";
    font-size: 10pt;
}

/* 按钮样式 */
QPushButton {
    padding: 6px 12px;
    border-radius: 4px;
    border: 1px solid #555555;
    background-color: #3d3d3d;
    color: #e0e0e0;
    min-height: 24px;
}

QPushButton:hover {
    border: 1px solid #777777;
    background-color: #4d4d4d;
}

QPushButton:pressed {
    background-color: #2d2d2d;
}

QPushButton:disabled {
    color: #777777;
    border: 1px solid #444444;
    background-color: #333333;
}

/* 主要按钮样式 */
QPushButton[primary="true"] {
    background-color: #3a76d8;
    color: white;
    border: 1px solid #2a66c8;
}

QPushButton[primary="true"]:hover {
    background-color: #4a86e8;
    border: 1px solid #3a76d8;
}

QPushButton[primary="true"]:pressed {
    background-color: #2a66c8;
}

QPushButton[primary="true"]:disabled {
    background-color: #304878;
    border: 1px solid #203868;
}

/* 输入框样式 */
QLineEdit, QTextEdit, QPlainTextEdit {
    padding: 4px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #1d1d1d;
    color: #e0e0e0;
    selection-background-color: #3a76d8;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3a76d8;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #252525;
    color: #777777;
}

/* 下拉框样式 */
QComboBox {
    padding: 4px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #3d3d3d;
    color: #e0e0e0;
    min-height: 24px;
}

QComboBox:hover {
    border: 1px solid #777777;
}

QComboBox:focus {
    border: 1px solid #3a76d8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #555555;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    selection-background-color: #3a76d8;
    selection-color: white;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid #555555;
    border-radius: 4px;
    top: -1px;
}

QTabBar::tab {
    padding: 6px 12px;
    margin-right: 2px;
    border: 1px solid #555555;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    background-color: #3d3d3d;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    border-bottom: 1px solid #2d2d2d;
}

QTabBar::tab:hover:!selected {
    background-color: #4d4d4d;
}

/* 分组框样式 */
QGroupBox {
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #e0e0e0;
}

/* 列表样式 */
QListWidget {
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #1d1d1d;
    alternate-background-color: #252525;
}

QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #333333;
}

QListWidget::item:selected {
    background-color: #3a76d8;
    color: white;
}

QListWidget::item:hover:!selected {
    background-color: #3d3d3d;
}

/* 滚动条样式 */
QScrollBar:vertical {
    border: none;
    background: #1d1d1d;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #555555;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #777777;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #1d1d1d;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #555555;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #777777;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 工具栏样式 */
QToolBar {
    border: none;
    background-color: #2d2d2d;
    spacing: 6px;
    padding: 3px;
}

QToolBar::separator {
    width: 1px;
    background-color: #555555;
    margin: 0 6px;
}

/* 状态栏样式 */
QStatusBar {
    border-top: 1px solid #555555;
    background-color: #2d2d2d;
    padding: 2px;
    font-size: 9pt;
}

QStatusBar QLabel {
    padding: 0 4px;
}

/* 进度条样式 */
QProgressBar {
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    background-color: #1d1d1d;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #3a76d8;
    border-radius: 3px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #1d1d1d;
}

QCheckBox::indicator:checked {
    background-color: #3a76d8;
    border: 1px solid #3a76d8;
}

QCheckBox::indicator:hover {
    border: 1px solid #777777;
}

/* 单选框样式 */
QRadioButton {
    spacing: 5px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555555;
    border-radius: 8px;
    background-color: #1d1d1d;
}

QRadioButton::indicator:checked {
    background-color: #3a76d8;
    border: 1px solid #3a76d8;
}

QRadioButton::indicator:hover {
    border: 1px solid #777777;
}

/* 菜单样式 */
QMenu {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
}

QMenu::item {
    padding: 5px 25px 5px 20px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #3a76d8;
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #555555;
    margin: 5px 0;
}

/* 主窗口样式 */
QMainWindow {
    background-color: #2d2d2d;
}

QMainWindow::separator {
    width: 1px;
    background-color: #555555;
}

/* 提示框样式 */
QToolTip {
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #3d3d3d;
    padding: 5px;
    color: #e0e0e0;
}
"""

def get_style(theme):
    """
    获取指定主题的样式表

    Args:
        theme: 主题名称，可以是 "light" 或 "dark"

    Returns:
        样式表字符串
    """
    if theme == "dark":
        return DARK_STYLE
    else:
        return COMMON_STYLE
