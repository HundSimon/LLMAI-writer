#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import json
import asyncio
from models.ai_model import AIModel

class SiliconFlowModel(AIModel):
    """SiliconFlow模型实现 (OpenAI兼容)"""

    def __init__(self, config_manager):
        """
        初始化SiliconFlow模型

        Args:
            config_manager: 配置管理器实例
        """
        super().__init__(config_manager)

        self.name = 'SiliconFlow'
        # 从配置中读取SiliconFlow特定的API密钥
        self.api_key = config_manager.get_api_key('siliconflow')
        # 从配置中读取SiliconFlow特定的模型名称
        self.model_name = config_manager.get_model_name('siliconflow')
        # 如果配置中没有找到模型名称，则使用默认值
        if not self.model_name:
            self.model_name = 'deepseek-ai/DeepSeek-R1'
        # 从配置中读取SiliconFlow特定的API URL，提供默认值
        self.api_url = config_manager.get_config('SILICONFLOW', 'api_url', 'https://api.siliconflow.cn/v1/chat/completions')

        if not self.api_key:
            raise ValueError(f"模型 '{self.name}' 的API密钥未配置 (请检查config.ini)")

        # model_name 现在有默认值，这个检查可以移除或保留以防万一
        # if not self.model_name:
        #     raise ValueError(f"模型 '{self.name}' 的模型名称未配置")

        if not self.api_url:
            # api_url 也有默认值，这个检查可以移除或保留
            # raise ValueError(f"模型 '{self.name}' 的API地址未配置")
            # 如果真的需要强制配置URL，可以保留此检查
            pass # 暂时允许使用默认URL

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
                        elif "text" in result["choices"][0]: # 兼容旧格式
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
                                    elif "text" in choice: # 兼容旧格式
                                        chunk = choice["text"]
                                    else:
                                        continue # 没有有效内容块

                                    if chunk: # 确保块不为空
                                        if callback:
                                            callback(chunk)
                                        yield chunk
                            except json.JSONDecodeError:
                                # 忽略无法解析的行
                                print(f"无法解析的行: {line}") # 调试信息
                                continue
        except Exception as e:
            raise Exception(f"流式生成文本时出错: {str(e)}")