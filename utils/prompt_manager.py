#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提示词管理模块

提供提示词模板管理和历史记录功能。
"""

import os
import json
import time
from typing import List, Dict, Any, Optional


class PromptTemplate:
    """提示词模板类"""
    
    def __init__(self, name: str, content: str, category: str = "general", 
                 description: str = "", created_at: float = None):
        """
        初始化提示词模板
        
        Args:
            name: 模板名称
            content: 模板内容
            category: 模板分类
            description: 模板描述
            created_at: 创建时间戳
        """
        self.name = name
        self.content = content
        self.category = category
        self.description = description
        self.created_at = created_at or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典表示
        """
        return {
            "name": self.name,
            "content": self.content,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """
        从字典创建模板
        
        Args:
            data: 字典数据
            
        Returns:
            PromptTemplate实例
        """
        return cls(
            name=data.get("name", ""),
            content=data.get("content", ""),
            category=data.get("category", "general"),
            description=data.get("description", ""),
            created_at=data.get("created_at", time.time())
        )


class PromptHistory: # This class might be out of scope for the library if it's for UI/app history
    """提示词历史记录类"""
    
    def __init__(self, prompt: str, model: str, result: str = "", 
                 timestamp: float = None, metadata: Dict[str, Any] = None):
        """
        初始化提示词历史记录
        
        Args:
            prompt: 提示词内容
            model: 使用的模型
            result: 生成结果
            timestamp: 时间戳
            metadata: 元数据
        """
        self.prompt = prompt
        self.model = model
        self.result = result
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典表示
        """
        return {
            "prompt": self.prompt,
            "model": self.model,
            "result": self.result,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptHistory':
        """
        从字典创建历史记录
        
        Args:
            data: 字典数据
            
        Returns:
            PromptHistory实例
        """
        return cls(
            prompt=data.get("prompt", ""),
            model=data.get("model", ""),
            result=data.get("result", ""),
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {})
        )


class PromptManager:
    """提示词管理器类"""
    
    def __init__(self, prompts_path: str = "prompt_templates.json"): # Modified constructor
        """
        初始化提示词管理器
        
        Args:
            prompts_path: 提示词模板文件路径 (e.g., prompt_templates.json)
        """
        self.templates_file = prompts_path # Use the provided path
        # History file management is likely out of scope for the library's core PromptManager
        # self.history_file = history_file 
        self.templates: Dict[str, PromptTemplate] = {}
        # self.history: List[PromptHistory] = [] # History management removed for library
        # self.max_history = 100  # Max history items also removed

        self._load_templates()
        
        # Library should not create default templates in a file.
        # It can have hardcoded defaults or expect user to provide them.
        # For now, removing automatic creation of default templates.
        # If no templates are loaded from file, it will be empty.
        # if not self.templates:
        #     self._create_default_templates() # This wrote to file, not suitable for library
    
    def _load_templates(self):
        """加载模板"""
        if self.templates_file and os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list): # Expecting a list of template dicts
                        for template_data in data:
                            if isinstance(template_data, dict):
                                template = PromptTemplate.from_dict(template_data)
                                self.templates[template.name] = template
                            else:
                                print(f"Skipping invalid template data (not a dict): {template_data}")
                    elif isinstance(data, dict): # Support for old format (dict of dicts) or single template
                         for name, template_data in data.items():
                            if isinstance(template_data, dict):
                                # Ensure name from dict key is used if not in template_data
                                if "name" not in template_data:
                                    template_data["name"] = name
                                template = PromptTemplate.from_dict(template_data)
                                self.templates[template.name] = template
                            else:
                                print(f"Skipping invalid template data for key '{name}': {template_data}")
                    else:
                        print(f"模板文件 '{self.templates_file}' 格式无法识别。应为JSON列表或字典。")

            except (json.JSONDecodeError, IOError) as e:
                print(f"加载模板文件 '{self.templates_file}' 出错: {e}")
        # else:
            # print(f"模板文件 '{self.templates_file}' 未找到。") # Optional: log this

    # _load_history, _save_history, add_history, get_history, clear_history removed.
    # These are application-level concerns, not core library prompt management.

    def _save_templates(self):
        """保存模板 (Primarily for application use, library might not save by default)"""
        # This method should ideally not be called by the library itself unless explicitly instructed.
        # For now, keeping it but noting it's more for an app using this manager.
        if not self.templates_file:
            print("无法保存模板：未指定模板文件路径。")
            return

        try:
            # Ensure directory exists if templates_file path includes directories
            dir_name = os.path.dirname(self.templates_file)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)

            with open(self.templates_file, "w", encoding="utf-8") as f:
                data = [template.to_dict() for template in self.templates.values()]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存模板文件 '{self.templates_file}' 出错: {e}")
    
    # _create_default_templates removed as library should not write files by default.
    # Default templates could be provided as a class method returning a list of PromptTemplate objects
    # or loaded from a resource within the package if needed.

    def add_template(self, name: str, content: str, category: str = "general", 
                    description: str = "", save_after_add: bool = False) -> bool: # Added save_after_add
        """
        添加模板 (in-memory)
        
        Args:
            name: 模板名称
            content: 模板内容
            category: 模板分类
            description: 模板描述
            save_after_add: 是否在添加后立即保存到文件 (for app use)
            
        Returns:
            是否添加成功
        """
        if name in self.templates:
            print(f"添加模板失败：名称 '{name}' 已存在。")
            return False
        
        template = PromptTemplate(name, content, category, description)
        self.templates[name] = template
        if save_after_add: # Conditional save
            self._save_templates()
        return True
    
    def update_template(self, name: str, content: Optional[str] = None, 
                       category: Optional[str] = None, 
                       description: Optional[str] = None,
                       save_after_update: bool = False) -> bool: # Added save_after_update
        """
        更新模板 (in-memory)
        """
        if name not in self.templates:
            print(f"更新模板失败：名称 '{name}' 未找到。")
            return False
        
        template = self.templates[name]
        updated = False
        if content is not None:
            template.content = content
            updated = True
        if category is not None:
            template.category = category
            updated = True
        if description is not None:
            template.description = description
            updated = True
        
        if updated and save_after_update: # Conditional save
            self._save_templates()
        return updated
    
    def delete_template(self, name: str, save_after_delete: bool = False) -> bool: # Added save_after_delete
        """
        删除模板 (in-memory)
        """
        if name not in self.templates:
            print(f"删除模板失败：名称 '{name}' 未找到。")
            return False
        
        del self.templates[name]
        if save_after_delete: # Conditional save
            self._save_templates()
        return True
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        return self.templates.get(name)
    
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        return [t for t in self.templates.values() if t.category == category]
    
    def get_all_templates(self) -> List[PromptTemplate]:
        return list(self.templates.values())
    
    # get_prompt_suggestions removed as it depends on history, which is removed.
    # This kind of feature could be a separate utility or part of an application layer.

    def format_prompt(self, template_name: str, **kwargs) -> Optional[str]:
        """
        使用给定参数格式化指定名称的提示词模板。

        Args:
            template_name: 要格式化的模板名称。
            **kwargs: 用于格式化模板的键值对参数。

        Returns:
            格式化后的提示词字符串，如果模板不存在则返回None。
        """
        template = self.get_template(template_name)
        if not template:
            return None
        
        try:
            return template.content.format(**kwargs)
        except KeyError as e:
            print(f"格式化模板 '{template_name}' 出错：缺少参数 {e}")
            return template.content # Return unformatted content on error
        except Exception as e:
            print(f"格式化模板 '{template_name}' 时发生未知错误: {e}")
            return template.content # Return unformatted content on error

# Example of how default templates could be provided by the library if needed:
# class DefaultTemplates:
#     @staticmethod
#     def get_standard_outline_template() -> PromptTemplate:
#         return PromptTemplate(
#             name="Standard Outline Template",
#             content="Create a detailed novel outline...\n{specifications}",
#             category="outline",
#             description="Standard template for generating novel outlines."
#         )

#     @staticmethod
#     def get_standard_chapter_template() -> PromptTemplate:
#         return PromptTemplate(
#             name="Standard Chapter Template",
#             content="Based on the following, write a chapter...\nTitle: {title}\nSummary: {summary}\n{context}",
#             category="chapter",
#             description="Standard template for generating novel chapters."
#         )
#
# To use:
# pm = PromptManager(prompts_path=None) # Initialize without a file
# pm.add_template(DefaultTemplates.get_standard_outline_template())
# pm.add_template(DefaultTemplates.get_standard_chapter_template())
# formatted_prompt = pm.format_prompt("Standard Chapter Template", title="My Chapter", summary="It's about...", context="Previous events...")