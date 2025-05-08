import aiohttp
import json
import asyncio
from .ai_model import AIModel

class ClaudeModel(AIModel):
    """Anthropic Claude模型实现"""

    def __init__(self, config=None, config_manager=None): # Added config parameter
        """
        初始化Claude模型

        Args:
            config (dict, optional): 特定于此模型实例的配置 (e.g., api_key, model_name).
            config_manager (ConfigManager, optional): 全局配置管理器.
        """
        super().__init__(config_manager) # config_manager can be None if all config is in `config`
        
        # Prioritize instance-specific config, then config_manager, then defaults
        if config and 'api_key' in config:
            self.api_key = config['api_key']
        elif config_manager:
            self.api_key = config_manager.get_api_key('claude')
        else:
            self.api_key = None

        if config and 'model_name' in config:
            self.model_name = config['model_name']
        elif config_manager:
            self.model_name = config_manager.get_model_name('claude')
        else:
            self.model_name = None # Will be set to default if still None

        # API URL can also be configurable
        self.api_url = (config and config.get('base_url')) or \
                       (config_manager and config_manager.get_config('CLAUDE', 'api_url', fallback=None)) or \
                       "https://api.anthropic.com/v1/messages"

        if not self.api_key:
            # Try to get from config_manager again if not in instance_config
            if config_manager and not (config and 'api_key' in config) : # if not provided by instance config
                 self.api_key = config_manager.get_api_key('claude')

            if not self.api_key: # if still not found
                 raise ValueError("Anthropic API密钥未配置 (claude_api_key)")


        if not self.model_name:
            # Try to get from config_manager again
            if config_manager and not (config and 'model_name' in config):
                self.model_name = config_manager.get_model_name('claude')
            
            if not self.model_name: # if still not found, use default
                default_model = "claude-3-opus-20240229"
                if config_manager:
                    default_model = config_manager.get_config('CLAUDE', 'default_model_name', fallback=default_model)
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
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
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
                    raise Exception(f"Anthropic API错误: {response.status} - {error_text}")

                result = await response.json()
                return result["content"][0]["text"]

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
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
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
                    raise Exception(f"Anthropic API错误: {response.status} - {error_text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        json_str = line[6:]
                        try:
                            data = json.loads(json_str)
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield delta.get("text", "")
                        except json.JSONDecodeError:
                            continue