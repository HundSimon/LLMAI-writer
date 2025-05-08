#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from openai import OpenAI
from models.ai_model import AIModel

class ModelScopeModel(AIModel):
    """ModelScope模型实现，支持DeepSeek-R1等模型"""

    def __init__(self, config_manager):
        """
        初始化ModelScope模型

        Args:
            config_manager: 配置管理器实例
        """
        super().__init__(config_manager)
        self.api_key = config_manager.get_api_key('modelscope')
        self.model_name = config_manager.get_model_name('modelscope')
        # 使用默认的ModelScope API地址
        self.base_url = 'https://api-inference.modelscope.cn/v1/'

        if not self.api_key:
            raise ValueError("ModelScope API密钥未配置")

        if not self.model_name:
            self.model_name = "deepseek-ai/DeepSeek-R1"  # 默认使用DeepSeek-R1模型

        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )

            # 获取思考过程和最终答案
            result = ""

            # 先检查是否有思考过程
            if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content
                if reasoning:
                    result += reasoning
                    result += "\n\n === 最终答案 ===\n\n"

            # 再获取最终答案
            if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                content = response.choices[0].message.content
                if content:
                    result += content

            # 如果没有内容，返回原始响应
            if not result:
                return str(response)

            return result

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
        try:
            # 使用to_thread将同步API调用转换为异步
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            # 处理流式响应
            done_reasoning = False
            for chunk in response:
                # 获取思考过程和最终答案
                reasoning_content = ""
                content = ""

                if hasattr(chunk.choices[0].delta, 'reasoning_content'):
                    reasoning_content = chunk.choices[0].delta.reasoning_content or ""

                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content or ""

                # 先输出思考过程
                if reasoning_content:
                    if callback:
                        callback(reasoning_content)
                    yield reasoning_content

                # 再输出最终答案
                elif content:
                    # 如果是第一次输出最终答案，添加分隔符
                    if not done_reasoning:
                        separator = "\n\n === 最终答案 ===\n\n"
                        if callback:
                            callback(separator)
                        yield separator
                        done_reasoning = True

                    if callback:
                        callback(content)
                    yield content

        except Exception as e:
            raise Exception(f"流式生成文本时出错: {str(e)}")
