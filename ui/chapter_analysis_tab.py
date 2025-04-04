#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
章节分析标签页

提供章节分析功能，包括核心剧情分析、故事梗概提取、优缺点分析、
角色和物品标注等功能。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QComboBox, QGroupBox, QFormLayout, QTabWidget,
    QMessageBox, QSplitter, QListWidget, QListWidgetItem, QCheckBox,
    QProgressBar, QDialog, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from ui.components import AIGenerateDialog


class ChapterAnalysisTab(QWidget):
    """章节分析标签页"""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.outline = None
        self.current_volume_index = -1
        self.selected_chapters = []
        self.analysis_result = {}

        # 初始化UI
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 创建左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 创建模型选择组
        model_group = QGroupBox("模型选择")
        model_layout = QFormLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT", "Claude", "Gemini", "自定义OpenAI", "ModelScope"])
        model_layout.addRow("AI模型:", self.model_combo)

        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)

        # 创建卷选择组
        volume_group = QGroupBox("卷选择")
        volume_layout = QVBoxLayout()

        self.volume_list = QListWidget()
        self.volume_list.currentRowChanged.connect(self.on_volume_selected)
        volume_layout.addWidget(self.volume_list)

        volume_group.setLayout(volume_layout)
        left_layout.addWidget(volume_group)

        # 创建章节选择组
        chapter_group = QGroupBox("章节选择")
        chapter_layout = QVBoxLayout()

        self.chapter_list = QListWidget()
        self.chapter_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.chapter_list.itemSelectionChanged.connect(self.on_chapter_selection_changed)
        chapter_layout.addWidget(self.chapter_list)

        # 添加分析范围选择
        range_layout = QHBoxLayout()
        self.range_label = QLabel("分析章节数:")
        self.range_spinner = QSpinBox()
        self.range_spinner.setMinimum(1)
        self.range_spinner.setMaximum(10)
        self.range_spinner.setValue(1)
        range_layout.addWidget(self.range_label)
        range_layout.addWidget(self.range_spinner)
        range_layout.addStretch()
        chapter_layout.addLayout(range_layout)

        # 添加分析按钮
        button_layout = QHBoxLayout()
        self.analyze_button = QPushButton("分析章节")
        self.analyze_button.clicked.connect(self.analyze_chapters)
        self.analyze_button.setEnabled(False)
        button_layout.addWidget(self.analyze_button)
        button_layout.addStretch()
        chapter_layout.addLayout(button_layout)

        chapter_group.setLayout(chapter_layout)
        left_layout.addWidget(chapter_group)

        # 添加分析选项组
        options_group = QGroupBox("分析选项")
        options_layout = QVBoxLayout()

        self.plot_checkbox = QCheckBox("核心剧情分析")
        self.plot_checkbox.setChecked(True)
        options_layout.addWidget(self.plot_checkbox)

        self.summary_checkbox = QCheckBox("故事梗概提取")
        self.summary_checkbox.setChecked(True)
        options_layout.addWidget(self.summary_checkbox)

        self.pros_cons_checkbox = QCheckBox("优缺点分析")
        self.pros_cons_checkbox.setChecked(True)
        options_layout.addWidget(self.pros_cons_checkbox)

        self.character_checkbox = QCheckBox("角色标注")
        self.character_checkbox.setChecked(True)
        options_layout.addWidget(self.character_checkbox)

        self.item_checkbox = QCheckBox("物品标注")
        self.item_checkbox.setChecked(True)
        options_layout.addWidget(self.item_checkbox)

        self.improvement_checkbox = QCheckBox("改进建议")
        self.improvement_checkbox.setChecked(True)
        options_layout.addWidget(self.improvement_checkbox)

        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)

        # 设置左侧面板
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)
        splitter.addWidget(left_panel)

        # 创建右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 创建分析结果标签页
        self.result_tabs = QTabWidget()
        
        # 创建各个分析结果标签页
        self.plot_tab = QWidget()
        plot_layout = QVBoxLayout(self.plot_tab)
        self.plot_edit = QTextEdit()
        self.plot_edit.setReadOnly(True)
        plot_layout.addWidget(self.plot_edit)
        self.result_tabs.addTab(self.plot_tab, "核心剧情")

        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_edit = QTextEdit()
        self.summary_edit.setReadOnly(True)
        summary_layout.addWidget(self.summary_edit)
        self.result_tabs.addTab(self.summary_tab, "故事梗概")

        self.pros_cons_tab = QWidget()
        pros_cons_layout = QVBoxLayout(self.pros_cons_tab)
        self.pros_cons_edit = QTextEdit()
        self.pros_cons_edit.setReadOnly(True)
        pros_cons_layout.addWidget(self.pros_cons_edit)
        self.result_tabs.addTab(self.pros_cons_tab, "优缺点")

        self.character_tab = QWidget()
        character_layout = QVBoxLayout(self.character_tab)
        self.character_edit = QTextEdit()
        self.character_edit.setReadOnly(True)
        character_layout.addWidget(self.character_edit)
        self.result_tabs.addTab(self.character_tab, "角色标注")

        self.item_tab = QWidget()
        item_layout = QVBoxLayout(self.item_tab)
        self.item_edit = QTextEdit()
        self.item_edit.setReadOnly(True)
        item_layout.addWidget(self.item_edit)
        self.result_tabs.addTab(self.item_tab, "物品标注")

        self.improvement_tab = QWidget()
        improvement_layout = QVBoxLayout(self.improvement_tab)
        self.improvement_edit = QTextEdit()
        self.improvement_edit.setReadOnly(True)
        improvement_layout.addWidget(self.improvement_edit)
        self.result_tabs.addTab(self.improvement_tab, "改进建议")

        right_layout.addWidget(self.result_tabs)

        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        # 设置右侧面板
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)

        # 设置分割器比例
        splitter.setSizes([300, 700])

    def set_outline(self, outline):
        """设置大纲数据"""
        self.outline = outline
        self._update_volume_list()

    def _update_volume_list(self):
        """更新卷列表"""
        self.volume_list.clear()
        self.chapter_list.clear()
        self.current_volume_index = -1
        self.selected_chapters = []
        self.analyze_button.setEnabled(False)

        if not self.outline:
            return

        volumes = self.outline.get("volumes", [])
        for i, volume in enumerate(volumes):
            title = volume.get("title", f"第{i+1}卷")
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.volume_list.addItem(item)

    def on_volume_selected(self, index):
        """卷选择事件处理"""
        self.current_volume_index = index
        self.chapter_list.clear()
        self.selected_chapters = []
        self.analyze_button.setEnabled(False)

        if index < 0:
            return

        volumes = self.outline.get("volumes", [])
        if index >= len(volumes):
            return

        volume = volumes[index]
        chapters = volume.get("chapters", [])

        for i, chapter in enumerate(chapters):
            title = chapter.get("title", f"第{i+1}章")
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.chapter_list.addItem(item)

    def on_chapter_selection_changed(self):
        """章节选择变更事件处理"""
        self.selected_chapters = []
        for item in self.chapter_list.selectedItems():
            chapter_index = item.data(Qt.ItemDataRole.UserRole)
            self.selected_chapters.append(chapter_index)

        # 启用或禁用分析按钮
        self.analyze_button.setEnabled(len(self.selected_chapters) > 0)

    def analyze_chapters(self):
        """分析章节"""
        if not self.selected_chapters:
            QMessageBox.warning(self, "分析失败", "请先选择要分析的章节")
            return

        # 获取选中的章节内容
        chapter_contents = []
        chapter_titles = []
        volumes = self.outline.get("volumes", [])
        if self.current_volume_index < 0 or self.current_volume_index >= len(volumes):
            QMessageBox.warning(self, "分析失败", "请先选择一个卷")
            return

        volume = volumes[self.current_volume_index]
        chapters = volume.get("chapters", [])

        # 获取分析范围
        analysis_range = self.range_spinner.value()
        if analysis_range > len(self.selected_chapters):
            analysis_range = len(self.selected_chapters)

        # 只分析选中的前N个章节
        for i in range(analysis_range):
            if i >= len(self.selected_chapters):
                break
                
            chapter_index = self.selected_chapters[i]
            if chapter_index < 0 or chapter_index >= len(chapters):
                continue

            chapter = chapters[chapter_index]
            chapter_title = chapter.get("title", f"第{chapter_index+1}章")
            chapter_titles.append(chapter_title)

            # 获取章节内容
            content = self.main_window.get_chapter(self.current_volume_index, chapter_index)
            if content:
                chapter_contents.append(f"【{chapter_title}】\n{content}")

        if not chapter_contents:
            QMessageBox.warning(self, "分析失败", "选中的章节没有内容")
            return

        # 获取模型类型
        model_type = self.model_combo.currentText()
        try:
            model = self.main_window.get_model(model_type)
        except ValueError as e:
            QMessageBox.warning(self, "模型错误", str(e))
            return

        # 获取总大纲信息
        outline_info = {}
        if self.outline:
            outline_info = {
                "title": self.outline.get("title", ""),
                "theme": self.outline.get("theme", ""),
                "synopsis": self.outline.get("synopsis", ""),
                "worldbuilding": self.outline.get("worldbuilding", "")
            }

        # 获取分析选项
        analysis_options = {
            "plot": self.plot_checkbox.isChecked(),
            "summary": self.summary_checkbox.isChecked(),
            "pros_cons": self.pros_cons_checkbox.isChecked(),
            "character": self.character_checkbox.isChecked(),
            "item": self.item_checkbox.isChecked(),
            "improvement": self.improvement_checkbox.isChecked()
        }

        # 构建提示词
        prompt = self._build_analysis_prompt(chapter_contents, chapter_titles, outline_info, analysis_options)

        # 创建分析对话框
        dialog = AIGenerateDialog(
            self,
            "章节分析",
            "分析结果",
            prompt,
            models=[model_type],
            default_model=model_type,
            outline_info=outline_info
        )

        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                self._process_analysis_result(result, analysis_options)

    def _build_analysis_prompt(self, chapter_contents, chapter_titles, outline_info, analysis_options):
        """构建分析提示词"""
        prompt = "请对以下章节内容进行详细分析：\n\n"

        # 添加小说信息
        if outline_info.get("title"):
            prompt += f"小说标题：{outline_info.get('title')}\n"
        if outline_info.get("theme"):
            prompt += f"中心思想：{outline_info.get('theme')}\n"
        if outline_info.get("synopsis"):
            prompt += f"故事梗概：{outline_info.get('synopsis')}\n"
        if outline_info.get("worldbuilding"):
            prompt += f"世界观设定：{outline_info.get('worldbuilding')}\n"

        prompt += "\n要分析的章节：" + "、".join(chapter_titles) + "\n\n"

        # 添加章节内容
        prompt += "章节内容：\n\n"
        prompt += "\n\n---\n\n".join(chapter_contents)
        prompt += "\n\n"

        # 添加分析要求
        prompt += "请进行以下分析：\n\n"

        if analysis_options.get("plot"):
            prompt += "1. 核心剧情分析：提取章节中的核心剧情线索，分析情节发展和转折点。\n\n"

        if analysis_options.get("summary"):
            prompt += "2. 故事梗概提取：简明扼要地总结章节内容，突出关键事件。\n\n"

        if analysis_options.get("pros_cons"):
            prompt += "3. 优缺点分析：分析章节写作的优点和不足之处。\n\n"

        if analysis_options.get("character"):
            prompt += "4. 角色标注：标注章节中出现的主要角色，分析其性格特点和行为动机。\n\n"

        if analysis_options.get("item"):
            prompt += "5. 物品标注：标注章节中出现的重要物品，分析其原本含义和在文本中的象征意义。\n\n"

        if analysis_options.get("improvement"):
            prompt += "6. 改进建议：提供具体的改进建议，包括情节、人物、对话、描写等方面。\n\n"

        prompt += "请以Markdown格式输出分析结果，使用标题、列表等格式元素使结果清晰易读。每个分析部分请使用二级标题（##）标明。"

        return prompt

    def _process_analysis_result(self, result, analysis_options):
        """处理分析结果"""
        # 清空之前的结果
        self.plot_edit.clear()
        self.summary_edit.clear()
        self.pros_cons_edit.clear()
        self.character_edit.clear()
        self.item_edit.clear()
        self.improvement_edit.clear()

        # 保存结果
        self.analysis_result = {}

        # 尝试解析结果中的各个部分
        if analysis_options.get("plot"):
            plot_section = self._extract_section(result, "核心剧情分析", "故事梗概提取", "优缺点分析", "角色标注", "物品标注", "改进建议")
            if plot_section:
                self.plot_edit.setMarkdown(plot_section)
                self.analysis_result["plot"] = plot_section

        if analysis_options.get("summary"):
            summary_section = self._extract_section(result, "故事梗概提取", "核心剧情分析", "优缺点分析", "角色标注", "物品标注", "改进建议")
            if summary_section:
                self.summary_edit.setMarkdown(summary_section)
                self.analysis_result["summary"] = summary_section

        if analysis_options.get("pros_cons"):
            pros_cons_section = self._extract_section(result, "优缺点分析", "核心剧情分析", "故事梗概提取", "角色标注", "物品标注", "改进建议")
            if pros_cons_section:
                self.pros_cons_edit.setMarkdown(pros_cons_section)
                self.analysis_result["pros_cons"] = pros_cons_section

        if analysis_options.get("character"):
            character_section = self._extract_section(result, "角色标注", "核心剧情分析", "故事梗概提取", "优缺点分析", "物品标注", "改进建议")
            if character_section:
                self.character_edit.setMarkdown(character_section)
                self.analysis_result["character"] = character_section

        if analysis_options.get("item"):
            item_section = self._extract_section(result, "物品标注", "核心剧情分析", "故事梗概提取", "优缺点分析", "角色标注", "改进建议")
            if item_section:
                self.item_edit.setMarkdown(item_section)
                self.analysis_result["item"] = item_section

        if analysis_options.get("improvement"):
            improvement_section = self._extract_section(result, "改进建议", "核心剧情分析", "故事梗概提取", "优缺点分析", "角色标注", "物品标注")
            if improvement_section:
                self.improvement_edit.setMarkdown(improvement_section)
                self.analysis_result["improvement"] = improvement_section

        # 如果没有找到特定部分，则显示完整结果
        if not any(self.analysis_result.values()):
            self.plot_edit.setMarkdown(result)
            self.analysis_result["full"] = result

        # 切换到第一个有内容的标签页
        for i, key in enumerate(["plot", "summary", "pros_cons", "character", "item", "improvement", "full"]):
            if key in self.analysis_result and self.analysis_result[key]:
                self.result_tabs.setCurrentIndex(min(i, self.result_tabs.count() - 1))
                break

    def _extract_section(self, text, section_title, *other_titles):
        """从文本中提取特定部分"""
        # 尝试查找二级标题
        section_pattern = f"## {section_title}"
        section_start = text.find(section_pattern)
        
        # 如果没找到，尝试查找一级标题
        if section_start == -1:
            section_pattern = f"# {section_title}"
            section_start = text.find(section_pattern)
        
        # 如果没找到，尝试查找无标记的标题
        if section_start == -1:
            section_pattern = f"{section_title}"
            section_start = text.find(section_pattern)
        
        # 如果仍然没找到，返回空字符串
        if section_start == -1:
            return ""
        
        # 找到了部分的开始，现在查找结束位置
        section_end = len(text)
        
        # 查找下一个部分的开始位置
        for title in other_titles:
            # 尝试查找二级标题
            next_section = text.find(f"## {title}", section_start + 1)
            if next_section != -1 and next_section < section_end:
                section_end = next_section
                continue
                
            # 尝试查找一级标题
            next_section = text.find(f"# {title}", section_start + 1)
            if next_section != -1 and next_section < section_end:
                section_end = next_section
                continue
                
            # 尝试查找无标记的标题
            next_section = text.find(f"{title}", section_start + 1)
            if next_section != -1 and next_section < section_end:
                section_end = next_section
        
        # 提取部分内容
        section_content = text[section_start:section_end].strip()
        
        return section_content
