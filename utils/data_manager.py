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


class NovelDataManager:
    """小说数据管理器"""
    
    def __init__(self, cache_enabled: bool = True):
        """
        初始化小说数据管理器
        
        Args:
            cache_enabled: 是否启用缓存
        """
        self.novel_data = {
            "outline": None,
            "chapters": {},
            "metadata": {},
            "relationships": {} # ✨ 人物关系就放这儿！
        }
        self.cache_enabled = cache_enabled
        self.cache = Cache() if cache_enabled else None
        self.modified = False
        self.current_file = None
    
    def set_outline(self, outline: Dict[str, Any]) -> None:
        """
        设置小说大纲
        
        Args:
            outline: 大纲数据
        """
        self.novel_data["outline"] = outline
        self.mark_modified() # 使用新方法

        # 清除相关缓存
        if self.cache_enabled:
            self.cache.delete("outline")
    
    def get_outline(self) -> Optional[Dict[str, Any]]:
        """
        获取小说大纲
        
        Returns:
            大纲数据
        """
        if not self.cache_enabled:
            return self.novel_data["outline"]
        
        # 尝试从缓存获取
        outline = self.cache.get("outline")
        if outline is None and self.novel_data["outline"] is not None:
            outline = self.novel_data["outline"]
            self.cache.set("outline", outline)
        
        return outline
    
    def set_chapter(self, volume_index: int, chapter_index: int, content: str) -> None:
        """
        设置章节内容
        
        Args:
            volume_index: 卷索引
            chapter_index: 章节索引
            content: 章节内容
        """
        key = f"{volume_index}_{chapter_index}"
        self.novel_data["chapters"][key] = content
        self.mark_modified() # 使用新方法

        # 清除相关缓存
        if self.cache_enabled:
            self.cache.delete(f"chapter_{key}")
    
    def get_chapter(self, volume_index: int, chapter_index: int) -> Optional[str]:
        """
        获取章节内容
        
        Args:
            volume_index: 卷索引
            chapter_index: 章节索引
            
        Returns:
            章节内容
        """
        key = f"{volume_index}_{chapter_index}"
        
        if not self.cache_enabled:
            return self.novel_data["chapters"].get(key)
        
        # 尝试从缓存获取
        cache_key = f"chapter_{key}"
        content = self.cache.get(cache_key)
        if content is None:
            content = self.novel_data["chapters"].get(key)
            if content is not None:
                self.cache.set(cache_key, content)
        
        return content
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        设置元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        self.novel_data["metadata"][key] = value
        self.mark_modified() # 使用新方法
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        获取元数据
        
        Args:
            key: 元数据键
            default: 默认值
            
        Returns:
            元数据值
        """
        return self.novel_data["metadata"].get(key, default)

    def set_relationships(self, relationships_data: Dict[Any, Any]) -> None: # 改为 Any, Any 兼容可能的键转换
        """
        设置人物关系数据

        Args:
            relationships_data: 人物关系字典
        """
        self.novel_data["relationships"] = relationships_data
        self.mark_modified() # 标记已修改

    def get_relationships(self) -> Dict[Any, Any]:
        """
        获取人物关系数据

        Returns:
            人物关系字典 (返回副本)
        """
        # 返回一个副本，防止外部直接修改内部数据
        return self.novel_data.get("relationships", {}).copy()

    def save_to_file(self, filepath: str) -> bool:
        """
        保存到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            # 保存数据
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.novel_data, f, ensure_ascii=False, indent=2)
            
            self.modified = False
            self.current_file = filepath
            return True
        except Exception as e:
            print(f"保存文件出错: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        从文件加载
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 验证数据结构
            if not isinstance(data, dict):
                return False
            
            if "outline" not in data:
                return False
            
            # 更新数据，确保所有预期的键都存在
            self.novel_data = {
                "outline": data.get("outline"),
                "chapters": data.get("chapters", {}),
                "metadata": data.get("metadata", {}),
                "relationships": data.get("relationships", {}) # 加载人物关系，兼容旧文件
            }
            self.modified = False
            self.current_file = filepath
            
            # 清除缓存
            if self.cache_enabled:
                self.cache.clear()
            
            return True
        except Exception as e:
            print(f"加载文件出错: {e}")
            return False
    
    def is_modified(self) -> bool:
        """
        检查是否已修改
        
        Returns:
            是否已修改
        """
        return self.modified

    def mark_modified(self):
        """标记数据已被修改"""
        self.modified = True

    def clear(self) -> None:
        """清空数据"""
        self.novel_data = {
            "outline": None,
            "chapters": {},
            "metadata": {},
            "relationships": {} # 清空人物关系
        }
        self.modified = False
        self.current_file = None
        
        # 清除缓存
        if self.cache_enabled:
            self.cache.clear()
    
    def get_chapter_count(self) -> int:
        """
        获取章节总数
        
        Returns:
            章节总数
        """
        return len(self.novel_data["chapters"])
    
    def get_all_chapter_keys(self) -> List[str]:
        """
        获取所有章节键
        
        Returns:
            章节键列表
        """
        return list(self.novel_data["chapters"].keys())
    
    def get_chapter_size(self, volume_index: int, chapter_index: int) -> int:
        """
        获取章节大小（字符数）
        
        Args:
            volume_index: 卷索引
            chapter_index: 章节索引
            
        Returns:
            章节大小
        """
        key = f"{volume_index}_{chapter_index}"
        content = self.novel_data["chapters"].get(key)
        return len(content) if content else 0
    
    def get_total_size(self) -> int:
        """
        获取总大小（字符数）
        
        Returns:
            总大小
        """
        total = 0
        
        # 计算大纲大小
        if self.novel_data["outline"]:
            total += len(json.dumps(self.novel_data["outline"], ensure_ascii=False))
        
        # 计算章节大小
        for content in self.novel_data["chapters"].values():
            total += len(content)
        
        return total
