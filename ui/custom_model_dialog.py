#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QFormLayout, QMessageBox,
    QGroupBox, QCheckBox, QListWidgetItem
)
from PyQt6.QtCore import Qt

class CustomModelDialog(QDialog):
    """自定义模型管理对话框"""

    def __init__(self, parent=None, config_manager=None):
        """
        初始化自定义模型管理对话框
        
        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
        """
        super().__init__(parent)
        self.setWindowTitle("自定义OpenAI兼容模型管理")
        self.resize(800, 500)
        
        self.config_manager = config_manager
        self.current_model = None
        
        # 初始化UI
        self._init_ui()
        
        # 加载模型列表
        self._load_models()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QHBoxLayout(self)
        
        # 创建左侧模型列表
        left_panel = QGroupBox("模型列表")
        left_layout = QVBoxLayout(left_panel)
        
        self.model_list = QListWidget()
        self.model_list.currentItemChanged.connect(self._on_model_selected)
        left_layout.addWidget(self.model_list)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("添加模型")
        self.add_button.clicked.connect(self._add_model)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("删除模型")
        self.delete_button.clicked.connect(self._delete_model)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        left_layout.addLayout(button_layout)
        
        # 创建右侧模型编辑面板
        right_panel = QGroupBox("模型配置")
        right_layout = QFormLayout(right_panel)
        
        self.name_edit = QLineEdit()
        right_layout.addRow("模型名称:", self.name_edit)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        right_layout.addRow("API密钥:", self.api_key_edit)
        
        self.model_name_edit = QLineEdit()
        right_layout.addRow("模型标识:", self.model_name_edit)
        
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("https://your-custom-api-endpoint.com/v1/chat/completions")
        right_layout.addRow("API地址:", self.api_url_edit)
        
        # 添加保存按钮
        save_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存更改")
        self.save_button.clicked.connect(self._save_model)
        self.save_button.setEnabled(False)
        save_layout.addWidget(self.save_button)
        
        right_layout.addRow("", save_layout)
        
        # 添加全局启用复选框
        self.enable_checkbox = QCheckBox("启用自定义OpenAI兼容模型")
        self.enable_checkbox.setChecked(self.config_manager.is_custom_openai_models_enabled())
        self.enable_checkbox.stateChanged.connect(self._on_enable_changed)
        right_layout.addRow("", self.enable_checkbox)
        
        # 添加到主布局
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        # 添加底部按钮
        bottom_layout = QHBoxLayout()
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_button)
        
        main_layout.addLayout(bottom_layout)
    
    def _load_models(self):
        """加载模型列表"""
        self.model_list.clear()
        
        models = self.config_manager.get_custom_openai_models()
        
        for model in models:
            item = QListWidgetItem(model.get('name', '未命名模型'))
            item.setData(Qt.ItemDataRole.UserRole, model)
            self.model_list.addItem(item)
    
    def _on_model_selected(self, current, previous):
        """处理模型选择事件"""
        if not current:
            self.current_model = None
            self.delete_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self._clear_form()
            return
        
        # 获取选中的模型
        self.current_model = current.data(Qt.ItemDataRole.UserRole)
        
        # 更新表单
        self.name_edit.setText(self.current_model.get('name', ''))
        self.api_key_edit.setText(self.current_model.get('api_key', ''))
        self.model_name_edit.setText(self.current_model.get('model_name', ''))
        self.api_url_edit.setText(self.current_model.get('api_url', ''))
        
        # 启用按钮
        self.delete_button.setEnabled(True)
        self.save_button.setEnabled(True)
    
    def _clear_form(self):
        """清空表单"""
        self.name_edit.clear()
        self.api_key_edit.clear()
        self.model_name_edit.clear()
        self.api_url_edit.clear()
    
    def _add_model(self):
        """添加新模型"""
        # 清空表单
        self._clear_form()
        
        # 设置默认值
        self.name_edit.setText(f"自定义模型{self.model_list.count() + 1}")
        self.api_url_edit.setText("https://api.openai.com/v1/chat/completions")
        
        # 创建新模型配置
        new_model = {
            'name': self.name_edit.text(),
            'api_key': '',
            'model_name': '',
            'api_url': self.api_url_edit.text()
        }
        
        # 添加到列表
        item = QListWidgetItem(new_model['name'])
        item.setData(Qt.ItemDataRole.UserRole, new_model)
        self.model_list.addItem(item)
        
        # 选中新添加的项
        self.model_list.setCurrentItem(item)
        
        # 启用保存按钮
        self.save_button.setEnabled(True)
        
        # 聚焦到API密钥输入框
        self.api_key_edit.setFocus()
    
    def _delete_model(self):
        """删除当前选中的模型"""
        if not self.current_model:
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除模型 '{self.current_model.get('name')}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 从配置中删除
        success = self.config_manager.delete_custom_openai_model(self.current_model.get('name'))
        
        if success:
            # 从列表中删除
            self.model_list.takeItem(self.model_list.currentRow())
            
            # 清空表单
            self._clear_form()
            
            # 禁用按钮
            self.delete_button.setEnabled(False)
            self.save_button.setEnabled(False)
            
            # 更新当前模型
            self.current_model = None
            
            QMessageBox.information(self, "删除成功", "模型已删除")
        else:
            QMessageBox.warning(self, "删除失败", "无法删除模型")
    
    def _save_model(self):
        """保存当前模型配置"""
        # 验证表单
        name = self.name_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        model_name = self.model_name_edit.text().strip()
        api_url = self.api_url_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "验证失败", "模型名称不能为空")
            self.name_edit.setFocus()
            return
        
        if not api_key:
            QMessageBox.warning(self, "验证失败", "API密钥不能为空")
            self.api_key_edit.setFocus()
            return
        
        if not model_name:
            QMessageBox.warning(self, "验证失败", "模型标识不能为空")
            self.model_name_edit.setFocus()
            return
        
        if not api_url:
            QMessageBox.warning(self, "验证失败", "API地址不能为空")
            self.api_url_edit.setFocus()
            return
        
        # 创建模型配置
        model_config = {
            'name': name,
            'api_key': api_key,
            'model_name': model_name,
            'api_url': api_url
        }
        
        # 检查是否是更新现有模型
        if self.current_model and self.current_model.get('name') == name:
            # 更新现有模型
            success = self.config_manager.update_custom_openai_model(name, model_config)
        else:
            # 添加新模型
            success = self.config_manager.add_custom_openai_model(model_config)
        
        if success:
            # 更新列表
            self._load_models()
            
            # 选中保存的模型
            for i in range(self.model_list.count()):
                item = self.model_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole).get('name') == name:
                    self.model_list.setCurrentItem(item)
                    break
            
            QMessageBox.information(self, "保存成功", "模型配置已保存")
        else:
            QMessageBox.warning(self, "保存失败", "无法保存模型配置，可能存在同名模型")
    
    def _on_enable_changed(self, state):
        """处理启用状态变更"""
        enabled = state == Qt.CheckState.Checked.value
        
        # 更新配置
        if 'CUSTOM_OPENAI_MODELS' not in self.config_manager.config:
            self.config_manager.config['CUSTOM_OPENAI_MODELS'] = {}
        
        self.config_manager.config['CUSTOM_OPENAI_MODELS']['enabled'] = str(enabled).lower()
        self.config_manager.save_config()
