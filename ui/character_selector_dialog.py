from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

class CharacterSelectorDialog(QDialog):
    """角色选择对话框，用于选择章节中出场的角色"""

    def __init__(self, parent, characters, selected_characters=None):
        """
        初始化角色选择对话框
        
        Args:
            parent: 父窗口
            characters: 所有角色列表
            selected_characters: 已选择的角色列表
        """
        super().__init__(parent)
        self.setWindowTitle("选择出场角色")
        self.resize(400, 500)
        self.characters = characters
        self.selected_characters = selected_characters or []
        self.selected_indices = []
        
        # 初始化UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        layout.addWidget(QLabel("请选择在本章节中出场的角色："))
        
        # 创建角色列表
        self.character_list = QListWidget()
        self._populate_character_list()
        layout.addWidget(self.character_list)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _populate_character_list(self):
        """填充角色列表"""
        self.character_list.clear()
        self.checkboxes = []
        
        for i, character in enumerate(self.characters):
            name = character.get("name", "未命名角色")
            identity = character.get("identity", "")
            display_text = f"{name} - {identity}" if identity else name
            
            # 创建列表项
            item = QListWidgetItem()
            self.character_list.addItem(item)
            
            # 创建复选框
            checkbox = QCheckBox(display_text)
            
            # 如果角色已被选中，设置复选框为选中状态
            if name in self.selected_characters:
                checkbox.setChecked(True)
                self.selected_indices.append(i)
            
            self.character_list.setItemWidget(item, checkbox)
            self.checkboxes.append(checkbox)
    
    def get_selected_characters(self):
        """获取选中的角色"""
        selected_characters = []
        selected_indices = []
        
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected_characters.append(self.characters[i])
                selected_indices.append(i)
        
        self.selected_indices = selected_indices
        return selected_characters
