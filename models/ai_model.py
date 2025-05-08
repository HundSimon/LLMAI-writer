from abc import ABC, abstractmethod

class AIModel(ABC):
    """AI模型的抽象基类，定义了所有AI模型需要实现的接口"""

    def __init__(self, config_manager):
        """
        初始化AI模型

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.proxy = config_manager.get_proxy_settings()

    @abstractmethod
    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本
        """
        pass

    @abstractmethod
    async def generate_stream(self, prompt, callback=None):
        """
        流式生成文本

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本流（异步生成器）
        """
        pass