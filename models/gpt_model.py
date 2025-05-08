import aiohttp
import json
import asyncio
from .ai_model import AIModel # Changed import

class GPTModel(AIModel):
    """OpenAI GPT模型实现"""

    def __init__(self, config=None, config_manager=None): # Added config parameter
        """
        初始化GPT模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., api_key, model_name, base_url).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None

        # API Key
        if config and 'api_key' in config:
            self.api_key = config['api_key']
        elif config_manager:
            self.api_key = config_manager.get_api_key('gpt')
        else:
            self.api_key = None

        # Model Name
        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('gpt')
        else:
            self.model_name = None
        
        # API URL (base_url from select_model maps to api_url here)
        if config and ('api_url' in config or 'base_url' in config) :
            self.api_url = config.get('api_url') or config.get('base_url')
        elif config_manager:
            # OpenAI base URL is standard but can be overridden (e.g. for Azure OpenAI)
            self.api_url = config_manager.get_config('GPT', 'api_url', fallback='https://api.openai.com/v1/chat/completions')
        else:
            self.api_url = 'https://api.openai.com/v1/chat/completions'


        if not self.api_key:
            if config_manager and not (config and 'api_key' in config):
                self.api_key = config_manager.get_api_key('gpt')
            if not self.api_key:
                raise ValueError("OpenAI API密钥未配置 (gpt_api_key)")

        if not self.model_name:
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name('gpt')
            if not self.model_name:
                default_model = "gpt-4-turbo"
                if config_manager:
                    default_model = config_manager.get_config('GPT', 'default_model_name', fallback=default_model)
                self.model_name = default_model

    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=data,
                proxy=self.proxy["https"] if self.proxy else None
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误: {response.status} - {error_text}")

                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt, callback=None):
        """
        流式生成文本

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本流（异步生成器）
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=data,
                proxy=self.proxy["https"] if self.proxy else None
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误: {response.status} - {error_text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: "):
                        json_str = line[6:]
                        try:
                            data = json.loads(json_str)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue