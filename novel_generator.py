# llmai_lib/novel_generator.py
import asyncio 
from typing import AsyncIterator, Dict, List, Optional, Union

from utils.config_manager import ConfigManager
from utils.prompt_manager import PromptManager
from utils.data_manager import NovelDataManager
from models.ai_model import AIModel
# Import specific model classes. These will be used in select_model.
# It's good practice to have an __init__.py in llmai_lib/models/ that could expose these,
# or a factory function. For now, direct imports as shown in the plan.
from models import gpt_model, claude_model, gemini_model, custom_openai_model, modelscope_model, ollama_model, siliconflow_model

from generators.outline_generator import OutlineGenerator
from generators.chapter_generator import ChapterGenerator


class NovelGenerator:
    def __init__(self, config_source: Union[str, Dict, None] = None, prompts_path: Optional[str] = None): # prompts_path can be None
        self.config_manager = ConfigManager(config_source=config_source)
        
        # If prompts_path is None, PromptManager might load from a default or be empty.
        # The plan specified "prompts_path: str = "prompt_templates.json""
        # If None is passed, PromptManager will try to load "prompt_templates.json" if it exists,
        # otherwise it will have no templates unless defaults are hardcoded (which we removed).
        # For a library, it's better if the user explicitly provides the path or None for no file.
        effective_prompts_path = prompts_path
        if prompts_path is None and self.config_manager:
            # Optionally, try to get a default prompts_path from config
            effective_prompts_path = self.config_manager.get_config('General', 'prompts_path', fallback="prompt_templates.json")

        self.prompt_manager = PromptManager(prompts_path=effective_prompts_path)
        self.data_manager = NovelDataManager() 
        self.current_model: Optional[AIModel] = None
        self._initialize_default_model()

    def _initialize_default_model(self):
        default_model_name = self.config_manager.get_config('General', 'default_model_name', fallback=None)
        if default_model_name:
            # This is a placeholder, you'll need a robust way to get model params
            # For a library, API keys and base_urls for default models should ideally be
            # configured by the user when they instantiate NovelGenerator or via config_source.
            # Relying on config_manager to have these for a "default_model_name" might be fragile
            # if config_source wasn't comprehensive.
            
            # We will attempt to select the model. If critical params like API key are missing,
            # select_model will raise an error, or the model's __init__ will.
            try:
                # For default model, we don't pass api_key/base_url here,
                # relying on the model's __init__ to fetch from ConfigManager
                # using its own section or the generic one.
                self.select_model(model_name=default_model_name)
            except Exception as e:
                print(f"Warning: Failed to initialize default model '{default_model_name}': {e}")
                # Continue without a default model if initialization fails. User must call select_model.


    def select_model(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        # model_config will be passed to the model's constructor.
        model_instance_config = {}
        if api_key:
            model_instance_config['api_key'] = api_key
        if base_url:
            # Models might expect 'api_url' or 'base_url'. We pass 'base_url' for consistency from this API.
            # The model's __init__ should handle mapping this if it internally uses 'api_url'.
            model_instance_config['base_url'] = base_url 
        
        # Pass any other kwargs to the model's config
        model_instance_config.update(kwargs)
        
        # Pass the global config_manager to the model too.
        # The model's __init__ will prioritize model_instance_config then config_manager.

        model_name_lower = model_name.lower()
        selected_model_instance: Optional[AIModel] = None

        if model_name_lower == "gpt":
            selected_model_instance = gpt_model.GPTModel(config=model_instance_config, config_manager=self.config_manager)
        elif model_name_lower == "claude":
            selected_model_instance = claude_model.ClaudeModel(config=model_instance_config, config_manager=self.config_manager)
        elif model_name_lower == "gemini":
            selected_model_instance = gemini_model.GeminiModel(config=model_instance_config, config_manager=self.config_manager)
        elif model_name_lower == "custom_openai": # Generic custom
            selected_model_instance = custom_openai_model.CustomOpenAIModel(config=model_instance_config, config_manager=self.config_manager)
        elif model_name_lower == "modelscope":
            selected_model_instance = modelscope_model.ModelScopeModel(config=model_instance_config, config_manager=self.config_manager)
        elif model_name_lower == "ollama":
            selected_model_instance = ollama_model.OllamaModel(config=model_instance_config, config_manager=self.config_manager)
        elif model_name_lower == "siliconflow":
            selected_model_instance = siliconflow_model.SiliconFlowModel(config=model_instance_config, config_manager=self.config_manager)
        else:
            # Attempt to load as a custom OpenAI model if name matches one in config
            if self.config_manager:
                custom_model_conf = self.config_manager.get_custom_openai_model(model_name)
                if custom_model_conf:
                    # Merge provided api_key/base_url with stored custom_model_conf
                    # Provided args (api_key, base_url) take precedence
                    merged_conf = {**custom_model_conf, **model_instance_config}
                    selected_model_instance = custom_openai_model.CustomOpenAIModel(config=merged_conf, config_manager=self.config_manager)
            
            if not selected_model_instance:
                raise ValueError(f"Unsupported or unknown model: {model_name}")
        
        self.current_model = selected_model_instance
        if not self.current_model: # Should be caught by ValueError above, but as a safeguard.
            raise ConnectionError(f"Failed to initialize model: {model_name}")


    async def generate_outline(self, title: str, genre: str, theme: str, style: str,
                               synopsis: str, volume_count: int, chapters_per_volume: int,
                               words_per_chapter: int, new_character_count: int,
                               selected_characters: Optional[List[Dict]] = None,
                               start_volume: Optional[int] = None, start_chapter: Optional[int] = None,
                               end_volume: Optional[int] = None, end_chapter: Optional[int] = None,
                               existing_outline_data: Optional[Dict] = None) -> Dict:
        if not self.current_model:
            raise RuntimeError("AI model not selected. Call select_model() first.")
        
        outline_generator = OutlineGenerator(self.current_model, self.prompt_manager, self.config_manager)
        
        prompt_params = {
            "title": title, "genre": genre, "theme": theme, "style": style,
            "synopsis": synopsis, "volume_count": volume_count, 
            "chapters_per_volume": chapters_per_volume, "words_per_chapter": words_per_chapter,
            "new_character_count": new_character_count, 
            "selected_characters": selected_characters or [],
            "start_volume": start_volume, "start_chapter": start_chapter,
            "end_volume": end_volume, "end_chapter": end_chapter,
            "existing_outline": existing_outline_data 
        }
        
        # OutlineGenerator.generate_outline now expects prompt_params and existing_outline_data
        # The existing_outline_data is for merging logic, prompt_params['existing_outline'] for prompt.
        generated_outline = await outline_generator.generate_outline(prompt_params, existing_outline_data)
        return generated_outline


    async def optimize_outline(self, outline_data: Dict) -> Dict:
        if not self.current_model:
            raise RuntimeError("AI model not selected. Call select_model() first.")
        outline_generator = OutlineGenerator(self.current_model, self.prompt_manager, self.config_manager)
        optimized_outline = await outline_generator.optimize_outline(outline_data)
        return optimized_outline

    async def generate_chapter(self, novel_data: Dict, volume_index: int, chapter_index: int) -> str:
        if not self.current_model:
            raise RuntimeError("AI model not selected. Call select_model() first.")
        chapter_generator = ChapterGenerator(self.current_model, self.prompt_manager, self.config_manager)
        
        # ChapterGenerator.generate_chapter expects novel_data (which is the full outline_data)
        chapter_content = await chapter_generator.generate_chapter(
            novel_data=novel_data, 
            volume_index=volume_index, 
            chapter_index=chapter_index
        )
        return chapter_content


    async def generate_chapter_stream(self, novel_data: Dict, volume_index: int, chapter_index: int) -> AsyncIterator[str]:
        if not self.current_model:
            raise RuntimeError("AI model not selected. Call select_model() first.")
        chapter_generator = ChapterGenerator(self.current_model, self.prompt_manager, self.config_manager)
        
        async for chunk in chapter_generator.generate_chapter_stream(
            novel_data=novel_data,
            volume_index=volume_index,
            chapter_index=chapter_index
        ):
            yield chunk


    def load_novel_data(self, filepath: str) -> Optional[Dict]: # Return Optional[Dict] as load_project can return None
        loaded_data = self.data_manager.load_project(filepath)
        # If load_project successfully loads data into self.data_manager.novel_data,
        # and also returns it, we can use the returned value.
        # The current NovelDataManager.load_project updates its internal state and returns a copy.
        return loaded_data

    def save_novel_data(self, novel_data: Dict, filepath: str) -> bool: # Return bool for success/failure
        return self.data_manager.save_project(novel_data, filepath)