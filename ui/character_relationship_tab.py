from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QSpacerItem, QSizePolicy, QMessageBox
from PyQt6.QtCore import Qt
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('QtAgg') # 确保使用 Qt 后端

class CharacterRelationshipTab(QWidget):
    """人物关系图标签页"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self._init_ui()
        self.relationships = {} # 用于存储关系数据 {("角色A", "角色B"): "关系描述"}

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)

        # --- 控件区 ---
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)

        # 角色选择1
        controls_layout.addWidget(QLabel("角色1:"))
        self.char1_combo = QComboBox()
        self.char1_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.char1_combo)

        # 角色选择2
        controls_layout.addWidget(QLabel("角色2:"))
        self.char2_combo = QComboBox()
        self.char2_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.char2_combo)

        # 关系描述
        controls_layout.addWidget(QLabel("关系:"))
        self.relation_edit = QLineEdit()
        self.relation_edit.setPlaceholderText("例如：朋友、敌人、父子...")
        controls_layout.addWidget(self.relation_edit)

        # 添加/更新关系按钮
        self.add_relation_button = QPushButton("添加/更新关系")
        self.add_relation_button.clicked.connect(self.add_or_update_relationship)
        controls_layout.addWidget(self.add_relation_button)

        # 删除关系按钮
        self.delete_relation_button = QPushButton("删除关系")
        self.delete_relation_button.clicked.connect(self.delete_relationship)
        controls_layout.addWidget(self.delete_relation_button)

        # 添加手动保存按钮
        self.save_relationships_button = QPushButton("保存关系(暂存)")
        self.save_relationships_button.setToolTip("将当前关系数据暂存到内存，最终需点击主工具栏保存按钮写入文件")
        self.save_relationships_button.clicked.connect(self.save_relationships_and_notify) # 连接新的带通知的方法
        controls_layout.addWidget(self.save_relationships_button)


        controls_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        main_layout.addWidget(controls_widget)

        # --- 图形显示区 ---
        # 创建 matplotlib 图形和画布
        self.figure = Figure(figsize=(5, 4), dpi=100) # 创建 Figure
        self.canvas = FigureCanvas(self.figure) # 创建画布并关联 Figure
        self.ax = self.figure.add_subplot(111) # 添加绘图区域
        self.ax.set_xticks([]) # 隐藏 x 轴刻度
        self.ax.set_yticks([]) # 隐藏 y 轴刻度
        self.ax.spines['top'].set_visible(False) # 隐藏上边框
        self.ax.spines['right'].set_visible(False) # 隐藏右边框
        self.ax.spines['bottom'].set_visible(False) # 隐藏下边框
        self.ax.spines['left'].set_visible(False) # 隐藏左边框

        main_layout.addWidget(self.canvas, 1) # 将画布添加到布局，并让它占据更多空间

        self.setLayout(main_layout)

        # 连接信号 (需要在 data_manager 中实现这些信号)
        # self.data_manager.characters_updated.connect(self.update_character_list) # 假设这个信号存在
        # self.data_manager.relationships_loaded.connect(self.load_relationships_from_data) # 假设这个信号存在

        # 连接下拉框变化，尝试加载现有关系
        self.char1_combo.currentIndexChanged.connect(self._update_relation_edit)
        self.char2_combo.currentIndexChanged.connect(self._update_relation_edit)


    def update_character_list(self):
        """更新角色下拉列表"""
        print("人物关系图：尝试更新角色列表...") # Debug
        current_char1 = self.char1_combo.currentText()
        current_char2 = self.char2_combo.currentText()

        self.char1_combo.clear()
        self.char2_combo.clear()

        # 尝试从 data_manager 获取角色列表
        characters = []
        if hasattr(self.data_manager, 'get_characters'): # 检查方法是否存在
             characters = self.data_manager.get_characters() or [] # 获取角色，确保是列表
        elif hasattr(self.data_manager, 'novel_data') and 'outline' in self.data_manager.novel_data and self.data_manager.novel_data['outline'] and 'characters' in self.data_manager.novel_data['outline']:
             # 如果没有 get_characters 方法，尝试从 outline 中获取
             characters = self.data_manager.novel_data['outline'].get('characters', []) or [] # 兼容旧格式或无角色情况
        else:
            print("人物关系图：无法找到角色数据源。") # Debug


        if characters and isinstance(characters, list):
            char_names = sorted([char.get('name', f'未命名_{i}') for i, char in enumerate(characters) if isinstance(char, dict)]) # 确保 char 是字典
            self.char1_combo.addItems([""] + char_names) # 添加一个空选项
            self.char2_combo.addItems([""] + char_names) # 添加一个空选项
            print(f"人物关系图：已添加 {len(char_names)} 个角色到下拉列表。") # Debug

            # 尝试恢复之前的选择
            if current_char1 in char_names:
                self.char1_combo.setCurrentText(current_char1)
            if current_char2 in char_names:
                self.char2_combo.setCurrentText(current_char2)
        else:
            print(f"人物关系图：未找到有效的角色列表数据。找到的数据类型: {type(characters)}") # Debug

        # 更新一下图形，因为角色列表变了可能需要重绘画布（比如添加了孤立节点）
        self.update_graph_display()


    def _get_relationship_key(self, char1, char2):
        """获取标准化的关系键 (确保顺序不影响)"""
        if not char1 or not char2 or char1 == char2:
            return None
        # 返回元组，因为 networkx 可以接受元组作为边的端点
        return tuple(sorted((char1, char2)))

    def _update_relation_edit(self):
        """当选择的角色变化时，更新关系输入框"""
        char1 = self.char1_combo.currentText()
        char2 = self.char2_combo.currentText()
        key = self._get_relationship_key(char1, char2)

        if key and key in self.relationships:
            self.relation_edit.setText(self.relationships[key])
            print(f"人物关系图：找到现有关系 {key}: {self.relationships[key]}") # Debug
        else:
            self.relation_edit.clear()
            # print(f"人物关系图：未找到关系 {key}") # Debug

    def load_relationships_from_data(self, relationships_data):
        """从 data_manager 加载关系数据"""
        print(f"人物关系图：正在从数据管理器加载关系: {relationships_data}") # Debug
        # JSON 不支持元组键，加载进来可能是字符串 "('角色A', '角色B')" 或列表 ["角色A", "角色B"]
        # 需要转换回元组键
        loaded_relationships = {}
        if isinstance(relationships_data, dict):
            for k, v in relationships_data.items():
                # 尝试多种可能的键格式转换
                try:
                    if isinstance(k, str) and k.startswith("(") and k.endswith(")"):
                         # 尝试解析 "('角色A', '角色B')" 格式
                         parsed_key = eval(k)
                         if isinstance(parsed_key, tuple) and len(parsed_key) == 2:
                             loaded_relationships[tuple(sorted(parsed_key))] = v
                         else:
                              print(f"人物关系图：无法解析的字符串键格式: {k}") # Debug
                    elif isinstance(k, list) and len(k) == 2:
                         # 尝试解析 ["角色A", "角色B"] 格式
                         loaded_relationships[tuple(sorted(k))] = v
                    elif isinstance(k, str) and '|' in k:
                         # 尝试解析 "角色A|角色B" 格式 (由 save_relationships_to_data 保存的格式)
                         parts = k.split('|', 1) # 只分割一次
                         if len(parts) == 2:
                             char1, char2 = parts
                             # 确保名字不为空
                             if char1 and char2:
                                 loaded_relationships[tuple(sorted((char1, char2)))] = v
                                 # print(f"人物关系图：成功解析竖线分隔键: {k}") # Debug (可选)
                             else:
                                 print(f"人物关系图：竖线分隔键包含空角色名: {k}") # Debug
                         else:
                             print(f"人物关系图：无法正确分割竖线分隔的字符串键: {k}") # Debug
                    elif isinstance(k, tuple) and len(k) == 2:
                         # 如果已经是元组了 (不太可能从JSON直接得到，除非手动处理过)
                         loaded_relationships[tuple(sorted(k))] = v
                    else:
                        # 只有在以上所有格式都不匹配时才忽略
                        print(f"人物关系图：忽略无法识别的关系键: {k} (类型: {type(k)})") # Debug
                except Exception as e:
                    print(f"人物关系图：解析关系键 '{k}' 时出错: {e}") # Debug

        self.relationships = loaded_relationships
        self.update_graph_display() # 更新图形显示
        self._update_relation_edit() # 更新一下输入框
        print(f"人物关系图：关系加载完成，转换后: {self.relationships}") # Debug

    def save_relationships_to_data(self):
        """将当前关系保存到 data_manager"""
        print("人物关系图：正在准备保存关系到数据管理器...") # Debug
        # JSON 不支持元组键，需要转换为字符串或列表
        # 为了简单起见，我们转换为字符串 "角色A|角色B"
        savable_relationships = {}
        for (char1, char2), desc in self.relationships.items():
            # 使用排序后的元组作为键，确保一致性
            key_str = f"{char1}|{char2}" # 使用分隔符，避免eval的安全风险
            savable_relationships[key_str] = desc

        # 假设 data_manager 有 set_relationships 方法
        self.data_manager.set_relationships(savable_relationships)
        print(f"人物关系图：关系已转换为可保存格式并传递给数据管理器: {savable_relationships}") # Debug


    def save_relationships_and_notify(self):
        """调用保存关系到数据管理器，并显示状态栏消息"""
        self.save_relationships_to_data()
        # 尝试访问主窗口的状态栏管理器来显示消息
        if hasattr(self.main_window, 'status_bar_manager'):
            self.main_window.status_bar_manager.show_message("人物关系已暂存", 3000) # 显示3秒

    def add_or_update_relationship(self):
        """添加或更新选定角色之间的关系"""
        char1 = self.char1_combo.currentText()
        char2 = self.char2_combo.currentText()
        relation_desc = self.relation_edit.text().strip()
        key = self._get_relationship_key(char1, char2) # key 是元组

        if not key:
            QMessageBox.warning(self, "操作无效", "请选择两个不同的角色。")
            return

        if not relation_desc:
            # 如果描述为空，视为删除关系
            self.delete_relationship() # 调用删除方法会更新图形
            return

        print(f"人物关系图：添加/更新关系 {key} -> '{relation_desc}'") # Debug
        self.relationships[key] = relation_desc # 使用元组键在内存中操作
        self.data_manager.mark_modified() # 标记数据已修改
        self.update_graph_display() # 更新图形显示
        # 注意：保存时 save_relationships_to_data 会被调用（如果应用逻辑正确的话，比如在关闭或切换标签页时）
        # 或者我们需要在每次修改后显式调用转换和保存？暂时不，依赖外部调用 save
        print(f"人物关系图：当前内存中关系: {self.relationships}") # Debug

    def delete_relationship(self):
        """删除选定角色之间的关系"""
        char1 = self.char1_combo.currentText()
        char2 = self.char2_combo.currentText()
        key = self._get_relationship_key(char1, char2) # key 是元组

        if not key:
            QMessageBox.warning(self, "操作无效", "请选择两个不同的角色以删除关系。")
            return

        if key in self.relationships:
            print(f"人物关系图：删除关系 {key}") # Debug
            del self.relationships[key] # 从内存中删除
            self.relation_edit.clear() # 清空输入框
            self.data_manager.mark_modified() # 标记数据已修改
            self.update_graph_display() # 更新图形显示
            print(f"人物关系图：当前内存中关系: {self.relationships}") # Debug
        else:
            print(f"人物关系图：关系 {key} 不存在，无需删除。") # Debug
            # QMessageBox.information(self, "提示", "这两个角色之间没有已定义的关系。")

    def update_graph_display(self):
        """根据 self.relationships 更新图形区域的显示"""
        print("人物关系图：更新图形显示...") # Debug
        self.ax.clear() # 清除旧图形
        self.ax.set_xticks([]) # 再次隐藏刻度
        self.ax.set_yticks([]) # 再次隐藏刻度
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)


        if not self.relationships:
            self.ax.text(0.5, 0.5, '还没有人物关系呢，快去添加吧！😜',
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=12, color='gray')
            self.canvas.draw() # 刷新画布显示提示文本
            print("人物关系图：没有关系数据，显示提示信息。") # Debug
            return

        G = nx.Graph()
        edge_labels = {}

        # 添加节点和边 (使用内存中的元组键)
        nodes = set()
        for (char1, char2), desc in self.relationships.items():
            nodes.add(char1)
            nodes.add(char2)
            G.add_edge(char1, char2)
            edge_labels[(char1, char2)] = desc

        # 添加所有在下拉列表中的角色作为节点，即使他们没有关系
        all_chars = [self.char1_combo.itemText(i) for i in range(self.char1_combo.count()) if self.char1_combo.itemText(i)]
        for char in all_chars:
            if char not in nodes:
                G.add_node(char) # 添加孤立节点
                nodes.add(char)


        if not G.nodes():
             self.ax.text(0.5, 0.5, '没有角色信息或关系数据。',
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=12, color='gray')
             self.canvas.draw()
             print("人物关系图：图中没有节点。") # Debug
             return

        try:
            # 选择一个布局算法，spring_layout 通常效果不错
            # k 控制节点间距离，iterations 控制迭代次数
            pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42) # 使用种子保证布局相对稳定

            # 解决中文显示问题 - 获取字体文件的正确路径
            import os
            font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SourceHanSansCN-Normal.otf")
            font_prop = None
            font_name = None
            if os.path.exists(font_path):
                 print(f"人物关系图：找到字体文件: {font_path}") # Debug
                 try:
                     # 创建字体属性对象
                     font_prop = matplotlib.font_manager.FontProperties(fname=font_path)
                     font_name = font_prop.get_name() # 获取字体名称供 networkx 使用
                     plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
                     print(f"人物关系图：使用字体: {font_name}") # Debug
                 except Exception as font_e:
                     print(f"人物关系图：加载字体文件 {font_path} 时出错: {font_e}") # Debug
                     font_prop = None
                     font_name = None
            else:
                 print(f"人物关系图：警告：未找到字体文件 {font_path}，标签可能使用默认字体。") # Debug
                 font_prop = None # 使用默认字体
                 font_name = None
                 plt.rcParams['axes.unicode_minus'] = False # 仍然设置这个

            # 绘制图形
            nx.draw_networkx_nodes(G, pos, ax=self.ax, node_size=2000, node_color='skyblue', alpha=0.9)
            nx.draw_networkx_edges(G, pos, ax=self.ax, width=1.0, alpha=0.5, edge_color='gray')
            # 使用 font_family 参数指定字体名称
            nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=10, font_family=font_name)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax, font_size=8, font_color='red', font_family=font_name)

            self.figure.tight_layout() # 调整布局防止标签重叠
            self.canvas.draw() # 刷新画布
            print(f"人物关系图：图形绘制完成，包含 {len(G.nodes())} 个节点和 {len(G.edges())} 条边。") # Debug
        except Exception as e:
            print(f"绘制关系图时出错: {e}") # Debug
            self.ax.text(0.5, 0.5, f'绘制图形出错:\n{e}',
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=10, color='red')
            self.canvas.draw()


    def set_outline(self, outline):
        """当加载新小说或大纲更新时调用"""
        print("人物关系图：接收到大纲/小说加载信号。") # Debug
        # 1. 更新角色列表
        self.update_character_list() # 这个方法内部会打印角色信息并调用 update_graph_display
        # 2. 加载关系数据 (需要确保在 update_character_list 之后执行，因为它依赖角色列表)
        relationships_data = self.data_manager.get_relationships()
        # 注意：load_relationships_from_data 内部也会调用 update_graph_display
        # update_character_list 内部也调用了 update_graph_display
        # 为了避免重复绘制，我们在 load_relationships_from_data 中绘制最终结果
        self.load_relationships_from_data(relationships_data)


# 需要在 data_manager.py 中添加:
# 1. get_characters() 方法 (如果还没有) -> 已在 update_character_list 中添加兼容逻辑
# 2. set_relationships(savable_data) 方法 -> 已修改为接收字典
# 3. get_relationships() 方法 -> 已存在
# 4. 在 load_from_file 中加载 relationships -> 已修改
# 5. 在 save_to_file 中保存 relationships -> 已修改为保存整个 novel_data
# 6. mark_modified() 方法 -> 已添加

# 需要在 main_window.py 的 _on_tab_changed 中，当 current_tab 是 character_relationship_tab 时，
# 调用 self.character_relationship_tab.save_relationships_to_data() 来触发保存。
# 或者在 save_novel 方法中统一处理所有数据的保存准备。

# 需要安装 networkx 和 matplotlib: pip install networkx matplotlib
# 需要系统中安装中文字体，或者提供字体文件。