import json
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QMessageBox, QSplitter, QDialog, QListWidget, QListWidgetItem,
    QTabWidget, QInputDialog, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QCursor

# 使用通用组件
from utils.async_utils import GenerationThread, ProgressIndicator
from ui.components import AIGenerateDialog


class ChapterOutlineTab(QWidget):
    """章节大纲编辑标签页"""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.outline = None
        self.current_volume_index = -1
        self.current_chapter_index = -1

        # 初始化UI
        self._init_ui()

        # 加载大纲
        self._load_outline()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 创建左侧面板（卷和章节列表）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 卷列表
        volume_group = QGroupBox("卷列表")
        volume_layout = QVBoxLayout()

        self.volume_list = QListWidget()
        self.volume_list.currentRowChanged.connect(self._on_volume_selected)
        self.volume_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.volume_list.customContextMenuRequested.connect(self._show_volume_context_menu)
        # 启用拖放功能
        self.volume_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.volume_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.volume_list.setDragEnabled(True)
        self.volume_list.setAcceptDrops(True)
        self.volume_list.setDropIndicatorShown(True)
        # 连接拖放信号
        self.volume_list.model().rowsMoved.connect(self._on_volume_moved)
        volume_layout.addWidget(self.volume_list)

        # 卷操作按钮
        volume_button_layout = QHBoxLayout()

        self.add_volume_button = QPushButton("添加卷")
        self.add_volume_button.clicked.connect(self._add_volume)
        volume_button_layout.addWidget(self.add_volume_button)

        volume_layout.addLayout(volume_button_layout)
        volume_group.setLayout(volume_layout)
        left_layout.addWidget(volume_group)

        # 章节列表
        chapter_group = QGroupBox("章节列表")
        chapter_layout = QVBoxLayout()

        self.chapter_list = QListWidget()
        self.chapter_list.currentRowChanged.connect(self._on_chapter_selected)
        self.chapter_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chapter_list.customContextMenuRequested.connect(self._show_chapter_context_menu)
        # 启用拖放功能
        self.chapter_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.chapter_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.chapter_list.setDragEnabled(True)
        self.chapter_list.setAcceptDrops(True)
        self.chapter_list.setDropIndicatorShown(True)
        # 连接拖放信号
        self.chapter_list.model().rowsMoved.connect(self._on_chapter_moved)
        chapter_layout.addWidget(self.chapter_list)

        # 章节操作按钮
        chapter_button_layout = QHBoxLayout()

        self.add_chapter_button = QPushButton("添加章节")
        self.add_chapter_button.clicked.connect(self._add_chapter)
        self.add_chapter_button.setEnabled(False)
        chapter_button_layout.addWidget(self.add_chapter_button)

        chapter_layout.addLayout(chapter_button_layout)
        chapter_group.setLayout(chapter_layout)
        left_layout.addWidget(chapter_group)

        # 添加左侧面板到分割器
        splitter.addWidget(left_panel)

        # 创建右侧面板（编辑区域）
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)

        # 卷编辑区域
        self.volume_edit_group = QGroupBox("卷编辑")
        volume_edit_layout = QVBoxLayout()

        # 卷标题
        volume_title_layout = QHBoxLayout()
        volume_title_layout.addWidget(QLabel("卷标题:"))

        self.volume_title_edit = QLineEdit()
        volume_title_layout.addWidget(self.volume_title_edit)

        self.volume_title_ai_button = QPushButton("AI生成")
        self.volume_title_ai_button.clicked.connect(lambda: self._generate_with_ai("卷标题", self.volume_title_edit.text(), self.volume_title_edit.setText))
        volume_title_layout.addWidget(self.volume_title_ai_button)

        volume_edit_layout.addLayout(volume_title_layout)

        # 卷简介
        volume_edit_layout.addWidget(QLabel("卷简介:"))

        self.volume_intro_edit = QTextEdit()
        self.volume_intro_edit.setMinimumHeight(100)
        volume_edit_layout.addWidget(self.volume_intro_edit)

        volume_intro_button_layout = QHBoxLayout()
        volume_intro_button_layout.addStretch()

        self.volume_intro_ai_button = QPushButton("AI生成")
        self.volume_intro_ai_button.clicked.connect(lambda: self._generate_with_ai("卷简介", self.volume_intro_edit.toPlainText(), self.volume_intro_edit.setPlainText))
        volume_intro_button_layout.addWidget(self.volume_intro_ai_button)

        volume_edit_layout.addLayout(volume_intro_button_layout)

        self.volume_edit_group.setLayout(volume_edit_layout)
        right_layout.addWidget(self.volume_edit_group)

        # 章节编辑区域
        self.chapter_edit_group = QGroupBox("章节编辑")
        chapter_edit_layout = QVBoxLayout()

        # 章节标题
        chapter_title_layout = QHBoxLayout()
        chapter_title_layout.addWidget(QLabel("章节标题:"))

        self.chapter_title_edit = QLineEdit()
        chapter_title_layout.addWidget(self.chapter_title_edit)

        self.chapter_title_ai_button = QPushButton("AI生成")
        self.chapter_title_ai_button.clicked.connect(lambda: self._generate_with_ai("章节标题", self.chapter_title_edit.text(), self.chapter_title_edit.setText))
        chapter_title_layout.addWidget(self.chapter_title_ai_button)

        chapter_edit_layout.addLayout(chapter_title_layout)

        # 章节摘要
        chapter_edit_layout.addWidget(QLabel("章节摘要:"))

        self.chapter_summary_edit = QTextEdit()
        self.chapter_summary_edit.setMinimumHeight(150)
        chapter_edit_layout.addWidget(self.chapter_summary_edit)

        chapter_summary_button_layout = QHBoxLayout()
        chapter_summary_button_layout.addStretch()

        # 添加选择角色按钮
        self.chapter_summary_select_characters_button = QPushButton("选择角色")
        self.chapter_summary_select_characters_button.clicked.connect(lambda: self._select_characters_for_summary())
        chapter_summary_button_layout.addWidget(self.chapter_summary_select_characters_button)

        self.chapter_summary_ai_button = QPushButton("AI生成")
        self.chapter_summary_ai_button.clicked.connect(lambda: self._generate_with_ai("章节摘要", self.chapter_summary_edit.toPlainText(), self.chapter_summary_edit.setPlainText))
        chapter_summary_button_layout.addWidget(self.chapter_summary_ai_button)

        chapter_edit_layout.addLayout(chapter_summary_button_layout)

        self.chapter_edit_group.setLayout(chapter_edit_layout)
        right_layout.addWidget(self.chapter_edit_group)

        # 保存按钮
        save_layout = QHBoxLayout()
        save_layout.addStretch()

        self.save_button = QPushButton("保存修改")
        self.save_button.clicked.connect(self._save_outline)
        save_layout.addWidget(self.save_button)

        right_layout.addLayout(save_layout)

        # 设置右侧面板
        right_panel.setWidget(right_content)
        splitter.addWidget(right_panel)

        # 设置分割器比例
        splitter.setSizes([300, 700])

        # 初始禁用编辑区域
        self.volume_edit_group.setEnabled(False)
        self.chapter_edit_group.setEnabled(False)

    def _load_outline(self):
        """加载大纲"""
        self.outline = self.main_window.get_outline()
        if not self.outline:
            return

        # 清空列表
        self.volume_list.clear()
        self.chapter_list.clear()

        # 加载卷列表
        volumes = self.outline.get("volumes", [])
        for i, volume in enumerate(volumes):
            title = volume.get("title", f"第{i+1}卷")
            self.volume_list.addItem(title)

    def _on_volume_selected(self, index):
        """卷选择事件"""
        self.current_volume_index = index
        self.current_chapter_index = -1

        # 清空章节列表
        self.chapter_list.clear()

        # 禁用章节编辑区域
        self.chapter_edit_group.setEnabled(False)

        if index < 0:
            # 禁用卷编辑区域
            self.volume_edit_group.setEnabled(False)
            self.add_chapter_button.setEnabled(False)
            return

        # 启用卷编辑区域和添加章节按钮
        self.volume_edit_group.setEnabled(True)
        self.add_chapter_button.setEnabled(True)

        # 加载卷信息
        volumes = self.outline.get("volumes", [])
        if index < len(volumes):
            volume = volumes[index]
            self.volume_title_edit.setText(volume.get("title", f"第{index+1}卷"))
            # 使用description字段作为卷简介
            self.volume_intro_edit.setPlainText(volume.get("description", ""))

            # 加载章节列表
            chapters = volume.get("chapters", [])
            for i, chapter in enumerate(chapters):
                title = chapter.get("title", f"第{i+1}章")
                self.chapter_list.addItem(title)

    def _on_chapter_selected(self, index):
        """章节选择事件"""
        self.current_chapter_index = index

        if index < 0:
            # 禁用章节编辑区域
            self.chapter_edit_group.setEnabled(False)
            return

        # 启用章节编辑区域
        self.chapter_edit_group.setEnabled(True)

        # 加载章节信息
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volume = volumes[self.current_volume_index]
            chapters = volume.get("chapters", [])
            if index < len(chapters):
                chapter = chapters[index]
                self.chapter_title_edit.setText(chapter.get("title", f"第{index+1}章"))
                self.chapter_summary_edit.setPlainText(chapter.get("summary", ""))

    def _add_volume(self):
        """添加卷"""
        if not self.outline:
            QMessageBox.warning(self, "错误", "请先生成大纲")
            return

        # 获取卷标题
        title, ok = QInputDialog.getText(self, "添加卷", "请输入卷标题:")
        if not ok or not title:
            return

        # 添加卷
        if "volumes" not in self.outline:
            self.outline["volumes"] = []

        new_volume = {
            "title": title,
            "description": "",  # 卷简介
            "chapters": []
        }

        self.outline["volumes"].append(new_volume)

        # 更新卷列表
        self.volume_list.addItem(title)

        # 选择新添加的卷
        self.volume_list.setCurrentRow(self.volume_list.count() - 1)

    def _add_chapter(self):
        """添加章节"""
        if self.current_volume_index < 0:
            return

        # 获取章节标题
        title, ok = QInputDialog.getText(self, "添加章节", "请输入章节标题:")
        if not ok or not title:
            return

        # 添加章节
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volume = volumes[self.current_volume_index]
            if "chapters" not in volume:
                volume["chapters"] = []

            # 获取当前章节数量，用于生成章节序号
            chapter_count = len(volume["chapters"])
            chapter_number = chapter_count + 1

            # 如果标题中没有包含章节序号，自动添加
            if not title.startswith(f"第{chapter_number}章") and not title.startswith(f"第{chapter_number} 章"):
                title = f"第{chapter_number}章：{title}"

            new_chapter = {
                "title": title,
                "summary": ""
            }

            volume["chapters"].append(new_chapter)

            # 更新章节列表
            self.chapter_list.addItem(title)

            # 选择新添加的章节
            self.chapter_list.setCurrentRow(self.chapter_list.count() - 1)

    def _show_volume_context_menu(self, position):
        """显示卷右键菜单"""
        if self.volume_list.count() == 0:
            return

        menu = QMenu()

        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self._edit_volume_title())
        menu.addAction(edit_action)

        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_volume())
        menu.addAction(delete_action)

        menu.exec(QCursor.pos())

    def _show_chapter_context_menu(self, position):
        """显示章节右键菜单"""
        if self.chapter_list.count() == 0:
            return

        menu = QMenu()

        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self._edit_chapter_title())
        menu.addAction(edit_action)

        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_chapter())
        menu.addAction(delete_action)

        menu.exec(QCursor.pos())

    def _edit_volume_title(self):
        """编辑卷标题"""
        current_item = self.volume_list.currentItem()
        if not current_item:
            return

        current_title = current_item.text()
        new_title, ok = QInputDialog.getText(self, "编辑卷标题", "请输入新的卷标题:", text=current_title)
        if not ok or not new_title:
            return

        # 更新卷标题
        current_item.setText(new_title)
        self.volume_title_edit.setText(new_title)

        # 更新大纲数据
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volumes[self.current_volume_index]["title"] = new_title

    def _edit_chapter_title(self):
        """编辑章节标题"""
        current_item = self.chapter_list.currentItem()
        if not current_item:
            return

        current_title = current_item.text()
        new_title, ok = QInputDialog.getText(self, "编辑章节标题", "请输入新的章节标题:", text=current_title)
        if not ok or not new_title:
            return

        # 更新章节标题
        current_item.setText(new_title)
        self.chapter_title_edit.setText(new_title)

        # 更新大纲数据
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volume = volumes[self.current_volume_index]
            chapters = volume.get("chapters", [])
            if self.current_chapter_index < len(chapters):
                chapters[self.current_chapter_index]["title"] = new_title

    def _delete_volume(self):
        """删除卷"""
        if self.current_volume_index < 0:
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个卷吗？这将同时删除卷中的所有章节。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 删除卷
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volumes.pop(self.current_volume_index)

            # 更新卷列表
            self.volume_list.takeItem(self.current_volume_index)

            # 清空章节列表
            self.chapter_list.clear()

            # 禁用编辑区域
            self.volume_edit_group.setEnabled(False)
            self.chapter_edit_group.setEnabled(False)
            self.add_chapter_button.setEnabled(False)

    def _delete_chapter(self):
        """删除章节"""
        if self.current_volume_index < 0 or self.current_chapter_index < 0:
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个章节吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 删除章节
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volume = volumes[self.current_volume_index]
            chapters = volume.get("chapters", [])
            if self.current_chapter_index < len(chapters):
                chapters.pop(self.current_chapter_index)

                # 更新章节列表
                self.chapter_list.takeItem(self.current_chapter_index)

                # 禁用章节编辑区域
                self.chapter_edit_group.setEnabled(False)

    def _on_volume_moved(self, parent, start, end, destination, row):
        """处理卷拖放事件"""
        # 计算源和目标索引
        from_index = start
        to_index = row
        if to_index > from_index:
            to_index -= 1

        # 如果源和目标相同，不需要处理
        if from_index == to_index:
            return

        # 移动大纲中的卷
        volumes = self.outline.get("volumes", [])
        volume = volumes.pop(from_index)
        volumes.insert(to_index, volume)

        # 更新当前选中的卷
        self.current_volume_index = to_index

    def _on_chapter_moved(self, parent, start, end, destination, row):
        """处理章节拖放事件"""
        # 如果没有选中卷，不需要处理
        if self.current_volume_index < 0:
            return

        # 计算源和目标索引
        from_index = start
        to_index = row
        if to_index > from_index:
            to_index -= 1

        # 如果源和目标相同，不需要处理
        if from_index == to_index:
            return

        # 移动大纲中的章节
        volumes = self.outline.get("volumes", [])
        volume = volumes[self.current_volume_index]
        chapters = volume.get("chapters", [])
        chapter = chapters.pop(from_index)
        chapters.insert(to_index, chapter)

        # 更新所有章节的序号
        self._update_chapter_numbers()

        # 更新当前选中的章节
        self.current_chapter_index = to_index

    def _update_chapter_numbers(self):
        """更新所有章节的序号"""
        if self.current_volume_index < 0:
            return

        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < len(volumes):
            volume = volumes[self.current_volume_index]
            chapters = volume.get("chapters", [])

            # 清空章节列表
            self.chapter_list.clear()

            # 更新每个章节的标题和序号
            for i, chapter in enumerate(chapters):
                # 提取原标题（去除序号部分）
                title = chapter.get("title", "")
                chapter_number = i + 1

                # 如果标题包含“第”和“章”，则提取内容部分
                if "第" in title and "章" in title:
                    # 尝试提取“章：”后面的内容
                    parts = title.split("章：", 1)
                    if len(parts) > 1:
                        title = parts[1]
                    else:
                        # 尝试提取“章 ”后面的内容
                        parts = title.split("章 ", 1)
                        if len(parts) > 1:
                            title = parts[1]
                        else:
                            # 如果上述方法都失败，则保留原标题
                            pass

                # 更新章节标题
                new_title = f"第{chapter_number}章：{title}"
                chapter["title"] = new_title

                # 更新章节列表
                item = QListWidgetItem(new_title)
                item.setData(Qt.ItemDataRole.UserRole, i)
                self.chapter_list.addItem(item)

            # 选中当前章节
            if self.current_chapter_index >= 0 and self.current_chapter_index < self.chapter_list.count():
                self.chapter_list.setCurrentRow(self.current_chapter_index)

    def _save_outline(self, show_message=True):
        """保存大纲

        Args:
            show_message: 是否显示消息对话框
        """
        if not self.outline:
            return

        # 保存当前编辑的卷和章节
        if self.current_volume_index >= 0:
            volumes = self.outline.get("volumes", [])
            if self.current_volume_index < len(volumes):
                volume = volumes[self.current_volume_index]
                volume["title"] = self.volume_title_edit.text()
                # 更新description字段作为卷简介
                volume["description"] = self.volume_intro_edit.toPlainText()

                if self.current_chapter_index >= 0:
                    chapters = volume.get("chapters", [])
                    if self.current_chapter_index < len(chapters):
                        chapter = chapters[self.current_chapter_index]
                        chapter["title"] = self.chapter_title_edit.text()
                        chapter["summary"] = self.chapter_summary_edit.toPlainText()

        # 保存大纲
        self.main_window.set_outline(self.outline)

        if show_message:
            QMessageBox.information(self, "保存成功", "大纲修改已保存")

    def _select_characters_for_summary(self):
        """为章节摘要选择出场角色"""
        if not self.outline or "characters" not in self.outline or not self.outline["characters"]:
            QMessageBox.warning(self, "提示", "当前小说没有角色数据，请先在人物编辑标签页添加角色。")
            return

        # 获取当前章节的已选角色（如果有）
        selected_characters = []
        if self.current_volume_index >= 0 and self.current_chapter_index >= 0:
            volumes = self.outline.get("volumes", [])
            if self.current_volume_index < len(volumes):
                volume = volumes[self.current_volume_index]
                chapters = volume.get("chapters", [])
                if self.current_chapter_index < len(chapters):
                    chapter = chapters[self.current_chapter_index]
                    selected_characters = chapter.get("characters", [])

        # 获取所有角色
        all_characters = self.outline["characters"]

        # 创建角色选择对话框
        from ui.character_selector_dialog import CharacterSelectorDialog
        dialog = CharacterSelectorDialog(self, all_characters, selected_characters)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 获取选中的角色
            selected_characters = dialog.get_selected_characters()

            # 保存选中的角色到当前章节
            if self.current_volume_index >= 0 and self.current_chapter_index >= 0:
                volumes = self.outline.get("volumes", [])
                if self.current_volume_index < len(volumes):
                    volume = volumes[self.current_volume_index]
                    chapters = volume.get("chapters", [])
                    if self.current_chapter_index < len(chapters):
                        chapter = chapters[self.current_chapter_index]
                        chapter["characters"] = selected_characters

                        # 自动保存
                        self._save_outline(show_message=False)
                        self.main_window.status_bar_manager.show_message(f"已为章节设置{len(selected_characters)}个出场角色")

    def _generate_with_ai(self, field_name, current_text, set_func):
        """使用AI生成内容"""
        # 获取总大纲信息
        outline_info = {}
        if self.outline:
            outline_info = {
                "title": self.outline.get("title", ""),
                "theme": self.outline.get("theme", ""),
                "synopsis": self.outline.get("synopsis", ""),
                "worldbuilding": self.outline.get("worldbuilding", "")
            }

        # 根据不同的字段添加额外的上下文信息
        context_info = {}

        # 如果是卷简介，添加卷标题信息
        if field_name == "卷简介" and self.current_volume_index >= 0:
            volumes = self.outline.get("volumes", [])
            if self.current_volume_index < len(volumes):
                volume = volumes[self.current_volume_index]
                context_info["volume_title"] = volume.get("title", "")

        # 如果是章节摘要，添加卷标题、卷简介、章节标题信息以及前10章和后3章的标题和摘要
        if field_name == "章节摘要" and self.current_volume_index >= 0 and self.current_chapter_index >= 0:
            volumes = self.outline.get("volumes", [])
            if self.current_volume_index < len(volumes):
                volume = volumes[self.current_volume_index]
                context_info["volume_title"] = volume.get("title", "")
                context_info["volume_description"] = volume.get("description", "")

                chapters = volume.get("chapters", [])
                if self.current_chapter_index < len(chapters):
                    chapter = chapters[self.current_chapter_index]
                    context_info["chapter_title"] = chapter.get("title", "")
                    context_info["chapter_number"] = self.current_chapter_index + 1

                    # 添加章节出场角色信息
                    chapter_characters = chapter.get("characters", [])
                    if chapter_characters:
                        context_info["chapter_characters"] = chapter_characters

                    # 添加前10章的标题和摘要
                    previous_chapters = []
                    start_idx = max(0, self.current_chapter_index - 10)
                    for i in range(start_idx, self.current_chapter_index):
                        if i < len(chapters):
                            prev_chapter = chapters[i]
                            previous_chapters.append({
                                "title": prev_chapter.get("title", ""),
                                "summary": prev_chapter.get("summary", "")
                            })
                    context_info["previous_chapters"] = previous_chapters

                    # 添加后3章的标题和摘要
                    next_chapters = []
                    end_idx = min(len(chapters), self.current_chapter_index + 4)
                    for i in range(self.current_chapter_index + 1, end_idx):
                        if i < len(chapters):
                            next_chapter = chapters[i]
                            next_chapters.append({
                                "title": next_chapter.get("title", ""),
                                "summary": next_chapter.get("summary", "")
                            })
                    context_info["next_chapters"] = next_chapters

        dialog = AIGenerateDialog(
            self,
            f"AI生成{field_name}",
            field_name,
            current_text,
            models=self._get_available_models(),
            default_model="GPT",
            outline_info=outline_info,
            context_info=context_info,
            prompt_manager=self.main_window.prompt_manager
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                set_func(result)
                # 在使用AI生成结果后自动保存
                self._save_outline()
                # 不显示保存成功对话框，只显示状态栏消息
                self.main_window.status_bar_manager.show_message("已使用AI生成结果并保存")

    def _get_available_models(self):
        """获取可用的模型列表"""
        # 只返回标准模型，不显示具体的自定义模型
        # 添加 SiliconFlow 到硬编码列表
        return ["GPT", "Claude", "Gemini", "自定义OpenAI", "ModelScope", "Ollama", "SiliconFlow"]

    def update_outline(self):
        """更新大纲（供外部调用）"""
        self._load_outline()
