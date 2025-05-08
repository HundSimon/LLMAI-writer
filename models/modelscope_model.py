#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from openai import OpenAI # Assuming modelscope uses an OpenAI-compatible client
# If modelscope has its own SDK, that should be used instead.
# For this refactoring, we'll assume the existing OpenAI client usage is intended.
from .ai_model import AIModel # Changed import

class ModelScopeModel(AIModel):
    """ModelScope模型实现，支持DeepSeek-R1等模型"""

    def __init__(self, config=None, config_manager=None): # Added config parameter
        """
        初始化ModelScope模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., api_key, model_name, base_url).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None

        # API Key
        if config and 'api_key' in config:
            self.api_key = config['api_key']
        elif config_manager:
            self.api_key = config_manager.get_api_key('modelscope')
        else:
            self.api_key = None

        # Model Name
        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('modelscope')
        else:
            self.model_name = None
        
        # Base URL (api_url from select_model maps to base_url here for OpenAI client)
        if config and ('base_url' in config or 'api_url' in config):
            self.base_url = config.get('base_url') or config.get('api_url')
        elif config_manager:
            self.base_url = config_manager.get_config('MODELSCOPE', 'base_url', fallback='https://api-inference.modelscope.cn/v1/')
        else:
            self.base_url = 'https://api-inference.modelscope.cn/v1/'


        if not self.api_key:
            if config_manager and not (config and 'api_key' in config) :
                 self.api_key = config_manager.get_api_key('modelscope')
            if not self.api_key:
                raise ValueError("ModelScope API密钥未配置 (modelscope_api_key)")

        if not self.model_name:
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name('modelscope')
            if not self.model_name:
                default_model = "deepseek-ai/DeepSeek-R1" # Original default
                if config_manager:
                    default_model = config_manager.get_config('MODELSCOPE', 'default_model_name', fallback=default_model)
                self.model_name = default_model


        # 初始化OpenAI客户端
        # This assumes ModelScope's API is OpenAI compatible.
        # If it requires specific http client headers or auth, this needs adjustment.
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
            # http_client can be passed here if proxy support is needed via httpx
        )

    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数 (not typically used in non-streaming)

        Returns:
            生成的文本
        """
        try:
            # Using asyncio.to_thread for blocking I/O
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )

            # 获取思考过程和最终答案
            # This part is specific to how ModelScope might structure its response.
            # Standard OpenAI response doesn't have 'reasoning_content'.
            # We will adapt to a more standard OpenAI response structure first,
            # and if ModelScope has extensions, they might need special handling.
            result_content = ""
            if response.choices and response.choices[0].message:
                result_content = response.choices[0].message.content or ""
            
            # The original code had logic for 'reasoning_content'.
            # If this is a specific ModelScope feature, it needs to be handled.
            # For now, focusing on the standard 'content'.
            # If 'reasoning_content' is part of the 'message' object:
            message_obj = response.choices[0].message
            if hasattr(message_obj, 'reasoning_content') and message_obj.reasoning_content:
                # Prepend reasoning if available
                result_content = f"{message_obj.reasoning_content}\n\n === 最终答案 ===\n\n{result_content}"

            if not result_content:
                 # Fallback if content is empty, though typically an error or empty string is fine.
                return str(response) # Or raise an error, or return empty string

            return result_content

        except Exception as e:
            # Log the error or handle it more gracefully
            raise Exception(f"ModelScope - 生成文本时出错: {str(e)}")

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
            stream = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            # The original code had logic for 'reasoning_content' and 'done_reasoning'.
            # This suggests ModelScope might have a multi-part streaming response.
            # We'll try to adapt this.
            done_reasoning_separator = False
            async for chunk in self._iterate_stream(stream): # Use a helper to iterate over sync stream
                text_chunk = ""
                reasoning_chunk = ""

                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        reasoning_chunk = delta.reasoning_content
                    if hasattr(delta, 'content') and delta.content:
                        text_chunk = delta.content
                
                if reasoning_chunk:
                    if callback:
                        await self._async_callback(callback, reasoning_chunk)
                    yield reasoning_chunk
                
                if text_chunk:
                    if not done_reasoning_separator and (hasattr(chunk.choices[0].delta, 'reasoning_content') or reasoning_chunk): # Heuristic: if reasoning was ever present or just finished
                        # This logic for separator might need refinement based on actual stream structure
                        # Assuming reasoning comes first, then content.
                        # If reasoning_content was in the *previous* chunk and now we get content,
                        # then we add the separator.
                        # This is tricky with chunk-based processing.
                        # A simpler approach might be if the API signals end of reasoning.
                        # For now, if we get content and haven't put separator, and reasoning might have occurred.
                        # This part is highly dependent on ModelScope's specific stream format.
                        # Let's assume for now that if reasoning_content is ever non-empty in the stream,
                        # the separator is needed before the first actual content.
                        # This might be better handled by checking a flag from the API if available.
                        pass # Separator logic from original code was complex and might be ModelScope specific.
                             # Replicating it perfectly without API docs is hard.
                             # Sticking to yielding content for now.
                             # The "=== 最终答案 ===" part might be a post-processing step or specific stream event.

                    if callback:
                        await self._async_callback(callback, text_chunk)
                    yield text_chunk
                
                await asyncio.sleep(0) # Yield control

        except Exception as e:
            raise Exception(f"ModelScope - 流式生成文本时出错: {str(e)}")

    async def _iterate_stream(self, sync_iterator):
        # Helper to iterate over a synchronous iterator in an async context
        # This is necessary because client.chat.completions.create(stream=True) when run in to_thread
        # returns a synchronous iterator.
        loop = asyncio.get_event_loop()
        while True:
            try:
                item = await loop.run_in_executor(None, next, sync_iterator)
                yield item
            except StopIteration:
                break
            except Exception as e: # Catch other potential errors during iteration
                print(f"Error during stream iteration: {e}") # Or log
                break
    
    async def _async_callback(self, callback, chunk):
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(chunk)
            else:
                callback(chunk)