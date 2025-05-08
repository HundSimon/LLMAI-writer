#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import json
import asyncio
from .ai_model import AIModel # Changed import

class SiliconFlowModel(AIModel):
    """SiliconFlow模型实现 (OpenAI兼容)"""

    def __init__(self, config=None, config_manager=None): # Added config parameter
        """
        初始化SiliconFlow模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., api_key, model_name, base_url/api_url).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None

        self.name = (config and config.get('name')) or 'SiliconFlow'
        
        # API Key
        if config and 'api_key' in config:
            self.api_key = config['api_key']
        elif config_manager:
            self.api_key = config_manager.get_api_key('siliconflow')
        else:
            self.api_key = None

        # Model Name
        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('siliconflow')
        else:
            self.model_name = None
        
        # API URL (base_url from select_model maps to api_url here)
        if config and ('api_url' in config or 'base_url' in config) :
            self.api_url = config.get('api_url') or config.get('base_url')
        elif config_manager:
            self.api_url = config_manager.get_config('SILICONFLOW', 'api_url', fallback='https://api.siliconflow.cn/v1/chat/completions')
        else:
            self.api_url = 'https://api.siliconflow.cn/v1/chat/completions'


        if not self.api_key:
            if config_manager and not (config and 'api_key' in config):
                 self.api_key = config_manager.get_api_key('siliconflow')
            if not self.api_key:
                raise ValueError(f"模型 '{self.name}' 的API密钥未配置 (siliconflow_api_key)")

        if not self.model_name:
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name('siliconflow')
            if not self.model_name: # If still not found, use a hardcoded default or from config's default section
                default_model = 'deepseek-ai/DeepSeek-V2' # Original default
                if config_manager:
                    default_model = config_manager.get_config('SILICONFLOW', 'default_model_name', fallback=default_model)
                self.model_name = default_model
        
        if not self.api_url: # Should always have a fallback
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
        proxy_url = self.proxy.get("https") if self.proxy and isinstance(self.proxy, dict) else None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=120) # 增加超时时间
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"SiliconFlow API请求失败: {response.status}, {error_text}")

                    result = await response.json()

                    # 解析响应 (与标准OpenAI格式一致)
                    if result.get("choices") and result["choices"][0].get("message"):
                        return result["choices"][0]["message"].get("content", "")
                    
                    # Fallback for older or slightly different formats if necessary
                    elif result.get("choices") and result["choices"][0].get("text"):
                         return result["choices"][0]["text"]

                    # 如果无法解析，返回原始响应或错误
                    # Consider logging the result for debugging
                    raise Exception(f"SiliconFlow API响应格式不符合预期: {result}")
        except aiohttp.ClientError as e: # Catch specific aiohttp errors
            raise Exception(f"SiliconFlow - 网络或请求错误: {str(e)}")
        except Exception as e: # Catch other errors
            raise Exception(f"SiliconFlow - 生成文本时出错: {str(e)}")

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
        proxy_url = self.proxy.get("https") if self.proxy and isinstance(self.proxy, dict) else None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=300) # 增加流式超时
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"SiliconFlow API流式请求失败: {response.status}, {error_text}")

                    # 处理流式响应 (与标准OpenAI格式一致)
                    async for line_bytes in response.content:
                        line = line_bytes.decode('utf-8').strip()
                        if not line:
                            continue
                        
                        if line == "data: [DONE]":
                            break 
                        
                        if line.startswith("data: "):
                            json_str = line[len("data: "):]
                            try:
                                chunk_data = json.loads(json_str)
                                if chunk_data.get("choices") and \
                                   chunk_data["choices"][0].get("delta") and \
                                   "content" in chunk_data["choices"][0]["delta"]:
                                    
                                    content_piece = chunk_data["choices"][0]["delta"]["content"]
                                    if content_piece: # Ensure content is not empty
                                        if callback:
                                            await self._async_callback(callback, content_piece)
                                        yield content_piece
                                else:
                                    # Handle cases where delta or content might be missing, or other stream events
                                    # For example, finish_reason might be in a chunk.
                                    pass


                            except json.JSONDecodeError:
                                # Log or handle malformed JSON lines
                                print(f"SiliconFlow - 无法解析的流式JSON行: {json_str}") # Consider logging
                                continue
                        await asyncio.sleep(0) # Yield control

        except aiohttp.ClientError as e:
            raise Exception(f"SiliconFlow - 流式网络或请求错误: {str(e)}")
        except Exception as e:
            raise Exception(f"SiliconFlow - 流式生成文本时出错: {str(e)}")

    async def _async_callback(self, callback, chunk):
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(chunk)
            else:
                callback(chunk)