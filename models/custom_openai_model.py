#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import json
import asyncio
from .ai_model import AIModel # Changed import

class CustomOpenAIModel(AIModel):
    """自定义OpenAI兼容API模型实现"""

    def __init__(self, config=None, config_manager=None): # Renamed model_config to config for consistency
        """
        初始化自定义OpenAI兼容模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., name, api_key, model_name, base_url/api_url).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None

        # Determine configuration source priority: instance config > config_manager > defaults
        
        # Name
        if config and 'name' in config:
            self.name = config['name']
        elif config_manager:
            # Custom OpenAI models might not have a single 'name' in config_manager,
            # as it could manage multiple. For a generic one, we might use a default.
            self.name = config_manager.get_config('CUSTOM_OPENAI', 'default_name', fallback='自定义OpenAI模型')
        else:
            self.name = '自定义OpenAI模型'

        # API Key
        if config and 'api_key' in config:
            self.api_key = config['api_key']
        elif config_manager:
            # For a generic custom_openai, it might fetch a default key.
            # If this class is used for *specific* named custom models from config, logic would differ.
            self.api_key = config_manager.get_api_key('custom_openai') # Assumes a generic key in config
        else:
            self.api_key = None

        # Model Name
        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('custom_openai') # Assumes a generic model name
        else:
            self.model_name = None

        # API URL (base_url from select_model maps to api_url here)
        if config and ('api_url' in config or 'base_url' in config) :
            self.api_url = config.get('api_url') or config.get('base_url')
        elif config_manager:
            self.api_url = config_manager.get_config('CUSTOM_OPENAI', 'api_url', fallback=None)
        else:
            self.api_url = None
            
        # Validation after attempting to load from all sources
        if not self.api_key:
            # Try one last time from config_manager if not in instance config
            if config_manager and not (config and 'api_key' in config):
                self.api_key = config_manager.get_api_key(self.name) # Try with specific name if available
                if not self.api_key: # Try generic if specific name fails
                    self.api_key = config_manager.get_api_key('custom_openai')
            if not self.api_key:
                raise ValueError(f"模型 '{self.name}' 的API密钥未配置")

        if not self.model_name:
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name(self.name) # Try with specific name
                if not self.model_name:
                     self.model_name = config_manager.get_model_name('custom_openai')
            if not self.model_name: # If still not found, it's an issue
                # It could have a hardcoded default, but for "custom" it should be specified.
                raise ValueError(f"模型 '{self.name}' 的模型名称未配置")


        if not self.api_url:
            if config_manager and not (config and ('api_url' in config or 'base_url' in config)):
                 self.api_url = config_manager.get_config(self.name, 'api_url', fallback=None) # Try with specific name
                 if not self.api_url:
                      self.api_url = config_manager.get_config('CUSTOM_OPENAI', 'api_url', fallback=None)
            if not self.api_url:
                raise ValueError(f"模型 '{self.name}' 的API地址未配置")

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
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 设置代理
        proxy = None
        if self.proxy:
            proxy = self.proxy.get("https")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API请求失败: {response.status}, {error_text}")

                    result = await response.json()

                    # 解析响应
                    if "choices" in result and len(result["choices"]) > 0:
                        if "message" in result["choices"][0]:
                            return result["choices"][0]["message"]["content"]
                        elif "text" in result["choices"][0]:
                            return result["choices"][0]["text"]

                    # 如果无法解析，返回原始响应
                    return str(result)
        except Exception as e:
            raise Exception(f"生成文本时出错: {str(e)}")

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
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 设置代理
        proxy = None
        if self.proxy:
            proxy = self.proxy.get("https")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API请求失败: {response.status}, {error_text}")

                    # 处理流式响应
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line:
                            # 跳过空行和"data: [DONE]"
                            if line == "data: [DONE]":
                                continue

                            # 处理"data: "前缀
                            if line.startswith("data: "):
                                line = line[6:]

                            try:
                                data = json.loads(line)
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"]:
                                        chunk = choice["delta"]["content"]
                                    elif "text" in choice:
                                        chunk = choice["text"]
                                    else:
                                        continue

                                    if callback:
                                        callback(chunk)
                                    yield chunk
                            except json.JSONDecodeError:
                                # 忽略无法解析的行
                                continue
        except Exception as e:
            raise Exception(f"流式生成文本时出错: {str(e)}")