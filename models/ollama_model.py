#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ollama模型实现

提供与Ollama本地模型的交互功能
"""

import json
import aiohttp
from models.ai_model import AIModel


class OllamaModel(AIModel):
    """Ollama模型实现类"""

    def __init__(self, config_manager, model_config=None):
        """
        初始化Ollama模型

        Args:
            config_manager: 配置管理器实例
            model_config: 可选的模型配置，用于自定义模型
        """
        super().__init__(config_manager)

        # 如果提供了模型配置，使用它
        if model_config:
            self.model_name = model_config.get('model_name', 'llama3.2')
            self.api_url = model_config.get('api_url', 'http://localhost:11434/api/chat')
            self.name = model_config.get('name', 'Ollama')
        else:
            # 否则使用配置管理器中的设置
            self.model_name = config_manager.get_model_name('ollama')
            self.api_url = config_manager.get_config('OLLAMA', 'api_url', 'http://localhost:11434/api/chat')
            self.name = 'Ollama'

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
            ]
        }

        # 创建HTTP会话
        async with aiohttp.ClientSession() as session:
            # 发送请求
            async with session.post(self.api_url, json=data, proxy=self.proxy) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API错误: {response.status} - {error_text}")

                # 读取完整响应
                full_response = ""
                async for line in response.content:
                    if not line:
                        continue

                    try:
                        chunk = json.loads(line)
                        if chunk.get("done", False):
                            break

                        content = chunk.get("message", {}).get("content", "")
                        full_response += content

                        if callback:
                            callback(content)
                    except json.JSONDecodeError:
                        print(f"无法解析JSON: {line}")

                return full_response

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
            ]
        }

        # 创建HTTP会话
        async with aiohttp.ClientSession() as session:
            # 发送请求
            async with session.post(self.api_url, json=data, proxy=self.proxy) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API错误: {response.status} - {error_text}")

                # 读取流式响应
                full_response = ""
                async for line in response.content:
                    if not line:
                        continue

                    try:
                        chunk = json.loads(line)
                        if chunk.get("done", False):
                            break

                        content = chunk.get("message", {}).get("content", "")
                        full_response += content

                        if callback:
                            callback(content)

                        yield content
                    except json.JSONDecodeError:
                        print(f"无法解析JSON: {line}")

                # 异步生成器不能使用带返回值的return语句
                # 这里只是为了结束生成器