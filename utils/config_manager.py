import configparser
import os

class ConfigManager:
    """配置管理器，负责读取和管理配置"""

    def __init__(self, config_source=None):
        """
        初始化配置管理器。

        Args:
            config_source: 配置的来源。
                           可以是配置文件路径 (str)，或配置字典 (dict)。
                           如果为 None，则使用空的配置。
        """
        self.config = configparser.ConfigParser()
        self.config_path = None # Only set if loaded from a file path

        if isinstance(config_source, str):
            self.config_path = config_source
            if os.path.exists(self.config_path):
                self.config.read(self.config_path, encoding='utf-8')
            else:
                # Library should not create files, so if path not found, it's an empty config
                # Or raise an error: raise FileNotFoundError(f"Config file not found: {self.config_path}")
                # For now, treat as empty config.
                pass
        elif isinstance(config_source, dict):
            # If a dictionary is provided, load it into the config parser
            # configparser needs sections, so we assume the dict is structured appropriately
            # e.g., {'SECTION_NAME': {'key': 'value'}}
            self.config.read_dict(config_source)
        elif config_source is None:
            # Use an empty config, methods will return defaults or None
            pass
        else:
            raise TypeError("config_source must be a file path (str), a dictionary, or None.")

    # _create_default_config is removed as the library should not create default files.

    def get_proxy_settings(self):
        """获取代理设置"""
        if 'PROXY' not in self.config:
            return None

        proxy_config = self.config['PROXY']
        enabled = proxy_config.getboolean('enabled', fallback=True)

        if not enabled:
            return None

        host = proxy_config.get('host', fallback='127.0.0.1')
        port = proxy_config.getint('port', fallback=10808)

        return {
            'http': f'http://{host}:{port}',
            'https': f'http://{host}:{port}'
        }

    def get_api_key(self, model_type):
        """获取指定模型的API密钥"""
        if 'API_KEYS' not in self.config:
            return None

        key_name = f'{model_type}_api_key'
        return self.config['API_KEYS'].get(key_name, None)

    def get_model_name(self, model_type):
        """获取指定类型的模型名称"""
        if 'MODELS' not in self.config:
            return None

        model_name = f'{model_type}_model'
        return self.config['MODELS'].get(model_name, None)

    def get_config(self, section, key, fallback=None): # Changed default to fallback to match configparser
        """获取指定配置项"""
        # getboolean, getint, getfloat can be used for typed retrieval
        return self.config.get(section, key, fallback=fallback)

    def set_config(self, section, key, value):
        """设置指定配置项 (in-memory only for library use)"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

    # GUI-specific or file-writing methods like is_custom_openai_enabled,
    # add_custom_openai_model, update_custom_openai_model, delete_custom_openai_model,
    # and save_config are removed or will be significantly re-evaluated for a library context.
    # For now, removing those that directly write to files or imply GUI interaction.

    def is_custom_openai_enabled(self):
        """检查自定义OpenAI API是否启用"""
        # 始终启用自定义OpenAI API
        return True

    def is_modelscope_enabled(self):
        """检查ModelScope API是否启用"""
        # ModelScope API始终启用
        return True

    def is_ollama_enabled(self):
        """检查Ollama API是否启用"""
        # Ollama API始终启用
        return True

    def is_custom_openai_models_enabled(self):
        """检查多个自定义OpenAI模型是否启用

        注意：多个自定义OpenAI模型始终启用，不需要额外的启用设置
        """
        return True

    def get_custom_openai_models(self):
        """获取所有自定义OpenAI模型配置"""
        if 'CUSTOM_OPENAI_MODELS' not in self.config:
            return []

        import json
        try:
            models_json = self.config['CUSTOM_OPENAI_MODELS'].get('models', '[]')
            return json.loads(models_json)
        except json.JSONDecodeError:
            return []

    def add_custom_openai_model(self, model_config):
        """添加一个自定义OpenAI模型配置

        Args:
            model_config: 模型配置字典，包含 name, api_key, model_name, api_url 等字段

        Returns:
            成功返回 True，失败返回 False
        """
        if 'CUSTOM_OPENAI_MODELS' not in self.config:
            self.config['CUSTOM_OPENAI_MODELS'] = {}
            # 不需要enabled设置，始终启用
            self.config['CUSTOM_OPENAI_MODELS']['models'] = '[]'

        # 获取当前模型列表
        models = self.get_custom_openai_models()

        # 检查是否已存在同名模型
        for model in models:
            if model.get('name') == model_config.get('name'):
                return False

        # 添加新模型
        models.append(model_config)

        # 保存模型列表
        import json
        self.config['CUSTOM_OPENAI_MODELS']['models'] = json.dumps(models, ensure_ascii=False)
        self.config['CUSTOM_OPENAI_MODELS']['enabled'] = 'true'

        # This method might not be relevant for a library if it doesn't manage saving.
        # self.save_config() # Removed
        return True

    def update_custom_openai_model(self, model_name, model_config):
        """更新一个自定义OpenAI模型配置 (in-memory)"""
        if 'CUSTOM_OPENAI_MODELS' not in self.config:
            # Or self.config.add_section('CUSTOM_OPENAI_MODELS')
            # self.config.set('CUSTOM_OPENAI_MODELS', 'models', '[]')
            return False # Cannot update if section doesn't exist

        models = self.get_custom_openai_models()
        updated = False
        for i, model in enumerate(models):
            if model.get('name') == model_name:
                models[i] = model_config
                updated = True
                break
        
        if updated:
            import json
            self.set_config('CUSTOM_OPENAI_MODELS', 'models', json.dumps(models, ensure_ascii=False))
            # self.save_config() # Removed
            return True
        return False

    def delete_custom_openai_model(self, model_name):
        """删除一个自定义OpenAI模型配置 (in-memory)"""
        if 'CUSTOM_OPENAI_MODELS' not in self.config:
            return False

        models = self.get_custom_openai_models()
        original_len = len(models)
        models = [model for model in models if model.get('name') != model_name]

        if len(models) < original_len:
            import json
            self.set_config('CUSTOM_OPENAI_MODELS', 'models', json.dumps(models, ensure_ascii=False))
            # self.save_config() # Removed
            return True
        return False

    def get_custom_openai_model(self, model_name):
        """获取指定名称的自定义OpenAI模型配置

        Args:
            model_name: 模型名称

        Returns:
            模型配置字典，如果不存在返回 None
        """
        models = self.get_custom_openai_models()

        for model in models:
            if model.get('name') == model_name:
                return model

        return None

    # def save_config(self): # Removed, library should not write files unless explicitly told to.
    #     """保存配置到文件"""
    #     if self.config_path: # Only save if a path was originally provided
    #         with open(self.config_path, 'w', encoding='utf-8') as f:
    #             self.config.write(f)
    #     else:
    #         # Optionally raise an error or log that config cannot be saved without a path
    #         pass