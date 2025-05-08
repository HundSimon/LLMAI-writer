from google import genai
import asyncio
from .ai_model import AIModel # Changed import

class GeminiModel(AIModel):
    """Google Gemini模型实现"""

    def __init__(self, config=None, config_manager=None): # Added config parameter
        """
        初始化Gemini模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., api_key, model_name).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None
        
        # API Key
        if config and 'api_key' in config:
            self.api_key = config['api_key']
        elif config_manager:
            self.api_key = config_manager.get_api_key('gemini')
        else:
            self.api_key = None

        # Model Name
        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('gemini')
        else:
            self.model_name = None

        if not self.api_key:
            if config_manager and not (config and 'api_key' in config):
                self.api_key = config_manager.get_api_key('gemini')
            if not self.api_key:
                raise ValueError("Google API密钥未配置 (gemini_api_key)")

        if not self.model_name:
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name('gemini')
            if not self.model_name:
                default_model = "gemini-1.5-flash"
                if config_manager:
                    default_model = config_manager.get_config('GEMINI', 'default_model_name', fallback=default_model)
                self.model_name = default_model
        
        # Base URL for Gemini is not typically changed like OpenAI, but could be added if needed
        # self.base_url = (config and config.get('base_url')) or \
        #                (config_manager and config_manager.get_config('GEMINI', 'base_url', fallback=None))
        # If base_url is used, genai.configure might need client_options.

        # 配置代理 - This part is tricky as genai SDK might not use env vars directly
        # or might require specific http client configuration.
        # For library use, relying on system-wide proxy or user configuring their env is safer
        # than the library trying to manipulate os.environ directly during __init__.
        # If proxy settings are passed in `config` or `config_manager`, they should be
        # used to configure the `genai.GenerativeModel` if its API allows.
        # For now, removing direct os.environ manipulation from __init__.
        # The user of the library would be responsible for ensuring proxy is set up
        # if they provide proxy details through config_manager.
        # if self.proxy:
        #     import os
        #     proxy_url = self.proxy.get("https") # Assuming self.proxy is populated by super().__init__
        #     if proxy_url:
        #          # This is generally not recommended for libraries to set global env vars.
        #          # os.environ["HTTP_PROXY"] = proxy_url
        #          # os.environ["HTTPS_PROXY"] = proxy_url
        #          pass # Log a warning or note that proxy needs to be set externally for genai

        # 初始化Gemini API客户端
        # It's better to configure genai per instance if possible, or ensure api_key is set before model init.
        # genai.configure(api_key=self.api_key) # Global configuration, might affect other instances.
        # Consider if genai.GenerativeModel can take api_key directly or via client_options.
        # As of recent versions, genai.configure is the primary way.
        # This should be called once, or be idempotent.
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Gemini model '{self.model_name}': {e}")


    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块 (not used in this sync wrapper)

        Returns:
            生成的文本
        """

        # 在事件循环中运行同步API调用
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, # Uses the default ThreadPoolExecutor
            self.model.generate_content, # Method to call
            prompt # Arguments to the method
        )

        return response.text

    async def generate_stream(self, prompt, callback=None):
        """
        流式生成文本

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本流（异步生成器）
        """

        # 在事件循环中运行同步API调用 that returns an iterator
        loop = asyncio.get_event_loop()
        response_stream = await loop.run_in_executor(
            None,
            self.model.generate_content,
            prompt,
            {"stream": True} # Pass stream=True as part of generation_config or directly if API supports
        )
        # The above might need adjustment based on how google-generativeai handles stream=True
        # If generate_content itself returns an iterable when stream=True, this is fine.
        # Otherwise, a specific stream method might be needed.
        # Assuming `model.generate_content(prompt, stream=True)` is the correct way.

        # 处理流式响应
        for chunk in response_stream: # Iterate over the synchronous iterator
            chunk_text = ""
            if hasattr(chunk, 'text'):
                chunk_text = chunk.text
            # Gemini API might have a different structure for streaming chunks
            # This part needs to be aligned with the actual structure of `chunk` objects
            # from `generate_content(..., stream=True)`
            # For example, it might be chunk.parts[0].text

            if chunk_text:
                if callback:
                    # If callback is async, it needs to be awaited or scheduled
                    # For simplicity, assuming callback is a sync function here
                    callback(chunk_text)
                yield chunk_text
            await asyncio.sleep(0) # Yield control to the event loop


    # _process_stream might not be needed if the main generate_stream directly iterates
    # and yields. The original _process_stream was designed for a different stream object.
    # Keeping it for reference but it might be replaced by direct iteration in generate_stream.
    async def _process_stream(self, response_stream): # This might be redundant
        """
        处理Gemini流式响应 (Potentially redundant if generate_content(stream=True) is directly iterable)

        Args:
            response_stream: Gemini流式响应

        Yields:
            文本块
        """
        for chunk in response_stream:
            chunk_text = ""
            if hasattr(chunk, 'text'):
                chunk_text = chunk.text
            elif hasattr(chunk, 'parts') and chunk.parts: # Common structure for Gemini
                chunk_text = chunk.parts[0].text
            # Add more specific error handling or structure checking if needed

            if chunk_text:
                yield chunk_text

            await asyncio.sleep(0) # Give async event loop a chance to run other tasks