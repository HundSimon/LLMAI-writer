#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ollama模型实现

提供与Ollama本地模型的交互功能
"""

import json
import aiohttp
from .ai_model import AIModel # Changed import


class OllamaModel(AIModel):
    """Ollama模型实现类"""

    def __init__(self, config=None, config_manager=None): # Renamed model_config to config
        """
        初始化Ollama模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., model_name, api_url/base_url, name).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None

        # Name
        if config and 'name' in config:
            self.name = config['name']
        elif config_manager:
            self.name = config_manager.get_config('OLLAMA', 'default_name', fallback='Ollama')
        else:
            self.name = 'Ollama'
            
        # Model Name
        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('ollama') # Generic 'ollama' model name
        else:
            self.model_name = None

        # API URL (base_url from select_model maps to api_url here)
        if config and ('api_url' in config or 'base_url' in config) :
            self.api_url = config.get('api_url') or config.get('base_url')
        elif config_manager:
            self.api_url = config_manager.get_config('OLLAMA', 'api_url', fallback='http://localhost:11434/api/chat')
        else:
            self.api_url = 'http://localhost:11434/api/chat'


        if not self.model_name:
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name('ollama') # Try generic again
            if not self.model_name: # If still not found, use a hardcoded default or from config's default section
                default_model = 'llama3'
                if config_manager:
                    default_model = config_manager.get_config('OLLAMA', 'default_model_name', fallback=default_model)
                self.model_name = default_model
        
        if not self.api_url: # Should always have a fallback
             raise ValueError(f"Ollama模型 '{self.name}' 的API URL未配置")
        
        # API Key is not typically used for local Ollama, but if a specific Ollama instance requires it:
        # if config and 'api_key' in config:
        #     self.api_key = config['api_key']
        # elif config_manager:
        #     self.api_key = config_manager.get_api_key('ollama') # Or self.name if specific
        # else:
        #     self.api_key = None
        # And then use it in headers if self.api_key is present.


    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本
        """
        # 构建请求数据
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False # Explicitly set stream to False for non-streaming
        }

        # 创建HTTP会话
        async with aiohttp.ClientSession() as session:
            # 发送请求
            # The original code used self.proxy directly. aiohttp expects proxy URL string.
            proxy_url = self.proxy.get("https") if self.proxy and isinstance(self.proxy, dict) else None
            async with session.post(self.api_url, json=data, proxy=proxy_url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API错误: {response.status} - {error_text}")

                # 读取完整响应 (Ollama non-streaming returns a single JSON object)
                response_data = await response.json()
                full_response_content = response_data.get("message", {}).get("content", "")

                if callback: # Callback might not be typical for non-streaming full response
                    await self._async_callback(callback, full_response_content)
                
                return full_response_content


    async def generate_stream(self, prompt, callback=None):
        """
        流式生成文本

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本流（异步生成器）
        """
        # 构建请求数据
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": True # Explicitly set stream to True
        }

        # 创建HTTP会话
        async with aiohttp.ClientSession() as session:
            proxy_url = self.proxy.get("https") if self.proxy and isinstance(self.proxy, dict) else None
            async with session.post(self.api_url, json=data, proxy=proxy_url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API错误: {response.status} - {error_text}")

                # 读取流式响应
                # Ollama stream sends multiple JSON objects, one per line
                async for line_bytes in response.content:
                    if not line_bytes:
                        continue
                    
                    line_str = line_bytes.decode('utf-8').strip()
                    if not line_str:
                        continue

                    try:
                        chunk_data = json.loads(line_str)
                        # Check if the stream is done (Ollama specific field)
                        if chunk_data.get("done", False) and not chunk_data.get("message", {}).get("content"):
                            # If 'done' is true and there's no more content in this chunk, it's the end.
                            # Some Ollama versions might send a final chunk with "done": true and summary stats.
                            break 

                        content_piece = chunk_data.get("message", {}).get("content", "")
                        if content_piece: # Only yield if there's actual content
                            if callback:
                                await self._async_callback(callback, content_piece)
                            yield content_piece
                        
                        if chunk_data.get("done", False): # If done is true, even with content, stop after yielding.
                            break

                    except json.JSONDecodeError:
                        # Log or handle malformed JSON lines if necessary
                        print(f"Ollama - 无法解析JSON: {line_str}") # Consider logging instead of printing
                        continue
                    await asyncio.sleep(0) # Yield control to event loop

    async def _async_callback(self, callback, chunk):
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(chunk)
            else:
                callback(chunk)