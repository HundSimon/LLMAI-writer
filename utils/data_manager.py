#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据管理模块

提供数据管理、懒加载和缓存功能，优化性能。
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable


class CacheItem:
    """缓存项"""
    
    def __init__(self, key: str, value: Any, expire_time: float = None):
        """
        初始化缓存项
        
        Args:
            key: 缓存键
            value: 缓存值
            expire_time: 过期时间戳，None表示永不过期
        """
        self.key = key
        self.value = value
        self.expire_time = expire_time
        self.created_at = time.time()
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """
        检查是否已过期
        
        Returns:
            是否已过期
        """
        if self.expire_time is None:
            return False
        return time.time() > self.expire_time
    
    def access(self):
        """访问缓存项，更新最后访问时间"""
        self.last_accessed = time.time()


class Cache:
    """缓存管理器"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            max_size: 最大缓存项数
            default_ttl: 默认生存时间（秒）
        """
        self.cache: Dict[str, CacheItem] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        
        # 检查是否过期
        if item.is_expired():
            del self.cache[key]
            return None
        
        # 更新访问时间
        item.access()
        
        return item.value
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """
        设置缓存项
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），None表示使用默认值
        """
        # 检查缓存大小
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict()
        
        # 计算过期时间
        expire_time = None
        if ttl is not None:
            expire_time = time.time() + ttl
        elif self.default_ttl is not None:
            expire_time = time.time() + self.default_ttl
        
        # 创建缓存项
        self.cache[key] = CacheItem(key, value, expire_time)
    
    def delete(self, key: str) -> bool:
        """
        删除缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def _evict(self) -> None:
        """驱逐策略：删除最久未访问的项"""
        if not self.cache:
            return
        
        # 找出最久未访问的项
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        del self.cache[oldest_key]


class NovelDataManager: # This class name might be too specific if it's just a generic data manager.
                        # For now, keeping as is per instructions.
                        # The API design refers to it as NovelDataManager.
    """小说数据管理器"""
    
    def __init__(self, cache_enabled: bool = True):
        """
        初始化小说数据管理器
        
        Args:
            cache_enabled: 是否启用缓存
        """
        self.novel_data = {
            "title": "", # Added from API design expectation
            "genre": "", # Added
            "theme": "", # Added
            "style": "", # Added
            "synopsis": "", # Added
            "volume_count": 0, # Added
            "chapters_per_volume": 0, # Added
            "words_per_chapter": 0, # Added
            "new_character_count": 0, # Added
            "selected_characters": [], # Added
            "characters": [], # Added from API design (for new characters)
            "worldbuilding": "", # Added
            "outline": None, # This might be redundant if all info is top-level
            "volumes": [], # Added from API design (structure for outline)
            "chapters": {}, # This might be for actual chapter content, distinct from outline structure
            "metadata": {},
            "relationships": {} 
        }
        self.cache_enabled = cache_enabled
        self.cache = Cache() if cache_enabled else None
        self.modified = False
        self.current_file = None # Stores the path of the currently loaded .ainovel file
    
    def set_outline(self, outline: Dict[str, Any]) -> None:
        """
        设置小说大纲 (and other top-level novel properties)
        
        Args:
            outline: 大纲数据, which should conform to the structure in self.novel_data
        """
        # Update all relevant fields from the provided outline dictionary
        for key in self.novel_data.keys():
            if key in outline:
                self.novel_data[key] = outline[key]
        
        # Ensure 'outline' key itself is also set if it's part of the input,
        # though it might be better to integrate its content into volumes/characters etc.
        if "outline" in outline: # If the input specifically has an 'outline' sub-dict
             self.novel_data["outline"] = outline["outline"]
        elif "volumes" in outline: # If volumes are provided, assume this is the main outline structure
            self.novel_data["outline"] = {"volumes": outline.get("volumes", []), 
                                          "characters": outline.get("characters", [])}


        self.mark_modified()

        if self.cache_enabled and self.cache:
            self.cache.delete("novel_data_full") # Cache the whole novel_data
    
    def get_outline(self) -> Optional[Dict[str, Any]]:
        """
        获取小说大纲 (the entire novel_data structure)
        
        Returns:
            The full novel data structure
        """
        if not self.cache_enabled or not self.cache:
            return self.novel_data.copy() # Return a copy
        
        cached_data = self.cache.get("novel_data_full")
        if cached_data is None and self.novel_data is not None: # novel_data should always exist
            cached_data = self.novel_data.copy()
            self.cache.set("novel_data_full", cached_data)
        
        return cached_data

    def set_chapter_content(self, volume_index: int, chapter_index: int, content: str) -> None:
        """
        设置独立存储的章节内容 (if not part of the main outline structure)
        
        Args:
            volume_index: 卷索引
            chapter_index: 章节索引
            content: 章节内容
        """
        key = f"content_{volume_index}_{chapter_index}"
        self.novel_data["chapters"][key] = content # Storing actual content separately
        self.mark_modified()

        if self.cache_enabled and self.cache:
            self.cache.delete(f"chapter_content_{key}")
    
    def get_chapter_content(self, volume_index: int, chapter_index: int) -> Optional[str]:
        """
        获取独立存储的章节内容
        """
        key = f"content_{volume_index}_{chapter_index}"
        
        if not self.cache_enabled or not self.cache:
            return self.novel_data["chapters"].get(key)
        
        cache_key = f"chapter_content_{key}"
        content = self.cache.get(cache_key)
        if content is None:
            content = self.novel_data["chapters"].get(key)
            if content is not None and self.cache: # Check self.cache again
                self.cache.set(cache_key, content)
        
        return content
    
    def set_metadata(self, key: str, value: Any) -> None:
        self.novel_data["metadata"][key] = value
        self.mark_modified()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.novel_data["metadata"].get(key, default)

    def set_relationships(self, relationships_data: Dict[Any, Any]) -> None:
        self.novel_data["relationships"] = relationships_data
        self.mark_modified()

    def get_relationships(self) -> Dict[Any, Any]:
        return self.novel_data.get("relationships", {}).copy()

    # Renaming to match API design: save_novel_data, load_novel_data
    def save_project(self, novel_data_to_save: Dict, filepath: str) -> bool: # Changed to save_project
        """
        保存小说数据到 .ainovel 文件 (or other specified format)
        
        Args:
            novel_data_to_save: The dictionary containing all novel data.
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # Ensure directory exists
            abs_filepath = os.path.abspath(filepath)
            os.makedirs(os.path.dirname(abs_filepath), exist_ok=True)
            
            with open(abs_filepath, "w", encoding="utf-8") as f:
                json.dump(novel_data_to_save, f, ensure_ascii=False, indent=2)
            
            # If this instance's data matches what was saved, reset modified flag
            if novel_data_to_save is self.novel_data: # Check if it's the instance's own data
                 self.modified = False
                 self.current_file = abs_filepath
            return True
        except Exception as e:
            print(f"保存文件 '{filepath}' 出错: {e}") # Log error
            return False
    
    def load_project(self, filepath: str) -> Optional[Dict]: # Changed to load_project
        """
        从文件加载小说数据
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载的小说数据字典，如果失败则返回 None
        """
        try:
            abs_filepath = os.path.abspath(filepath)
            with open(abs_filepath, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            if not isinstance(loaded_data, dict):
                print(f"文件 '{filepath}' 格式错误: 不是一个字典。")
                return None # Or raise error
            
            # Basic validation (can be more extensive)
            # if "outline" not in loaded_data and "volumes" not in loaded_data : # Check for core components
            #     print(f"文件 '{filepath}' 缺少必要的大纲或卷信息。")
            #     return None

            # Update internal state if this manager instance is loading into itself
            # For library use, this method might just return the data.
            # The API design implies it loads into the instance.
            
            # Ensure all expected top-level keys are present in self.novel_data,
            # filling with defaults from loaded_data or initial defaults.
            current_keys = set(self.novel_data.keys())
            for key in current_keys:
                if key in loaded_data:
                    self.novel_data[key] = loaded_data[key]
                # else: it keeps its default from __init__
            
            # Add any extra keys from loaded_data not in initial self.novel_data structure
            for key, value in loaded_data.items():
                if key not in self.novel_data:
                    self.novel_data[key] = value

            self.modified = False
            self.current_file = abs_filepath
            
            if self.cache_enabled and self.cache:
                self.cache.clear()
                self.cache.set("novel_data_full", self.novel_data.copy()) # Cache the newly loaded data
            
            return self.novel_data.copy() # Return a copy of the loaded data
        except FileNotFoundError:
            print(f"加载文件出错: 文件未找到 '{filepath}'")
            return None
        except json.JSONDecodeError:
            print(f"加载文件出错: JSON 解析错误 '{filepath}'")
            return None
        except Exception as e:
            print(f"加载文件时发生未知错误 '{filepath}': {e}")
            return None
    
    def is_modified(self) -> bool:
        return self.modified

    def mark_modified(self):
        self.modified = True

    def clear_data(self) -> None: # Renamed from clear to clear_data for clarity
        """清空当前加载的小说数据"""
        self.novel_data = { # Reset to initial structure
            "title": "", "genre": "", "theme": "", "style": "", "synopsis": "",
            "volume_count": 0, "chapters_per_volume": 0, "words_per_chapter": 0,
            "new_character_count": 0, "selected_characters": [], "characters": [],
            "worldbuilding": "", "outline": None, "volumes": [],
            "chapters": {}, "metadata": {}, "relationships": {}
        }
        self.modified = False
        self.current_file = None
        
        if self.cache_enabled and self.cache:
            self.cache.clear()
    
    # Utility methods like get_chapter_count, get_all_chapter_keys, etc.
    # need to be re-evaluated based on the new self.novel_data structure.
    # For example, chapter count might come from len(self.novel_data['volumes'][v_idx]['chapters']).

    def get_chapter_summary(self, volume_index: int, chapter_index: int) -> Optional[str]:
        """ Helper to get a chapter summary from the outline structure """
        try:
            return self.novel_data["volumes"][volume_index]["chapters"][chapter_index]["summary"]
        except (IndexError, KeyError, TypeError):
            return None

    def get_total_word_count_estimate(self) -> int:
        """ Estimates total word count based on outline structure """
        count = 0
        if "volumes" in self.novel_data:
            for vol in self.novel_data.get("volumes", []):
                for chap in vol.get("chapters", []):
                    # This is a placeholder; actual word count would be from chapter content
                    # For now, let's assume words_per_chapter is accurate if available
                    if self.novel_data.get("words_per_chapter", 0) > 0:
                        count += self.novel_data["words_per_chapter"]
                    else: # Fallback: count words in summary if no explicit count
                        summary = chap.get("summary", "")
                        count += len(summary.split()) # Rough estimate
        return count

    # get_chapter_size and get_total_size are also affected by structure change.
    # get_total_size might be more about the size of the JSON data itself.