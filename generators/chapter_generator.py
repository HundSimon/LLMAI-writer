import json
from models.ai_model import AIModel # Changed import
from utils.prompt_manager import PromptManager # Added import
from utils.config_manager import ConfigManager # Added import

class ChapterGenerator:
    """小说章节生成器"""

    def __init__(self, ai_model: AIModel, prompt_manager: PromptManager, config_manager: ConfigManager): # Changed signature
        """
        初始化章节生成器

        Args:
            ai_model: AI模型实例
            prompt_manager: PromptManager实例
            config_manager: 配置管理器实例
        """
        self.ai_model = ai_model
        self.prompt_manager = prompt_manager # Added
        self.config_manager = config_manager # Added

    async def generate_chapter(self, novel_data: dict, volume_index: int, chapter_index: int, callback=None): # Changed 'outline' to 'novel_data' to match NovelGenerator
        """
        生成章节内容

        Args:
            outline: 小说大纲（JSON格式）
            volume_index: 卷索引
            chapter_index: 章节索引
            callback: 回调函数，用于接收流式生成的内容

        Returns:
            生成的章节内容
        """
        # prompt = self._create_chapter_prompt(novel_data, volume_index, chapter_index)
        # If using PromptManager:
        # This requires a more structured way to pass parameters to the prompt template.
        # For example, extract all necessary details from novel_data, volume_index, chapter_index
        # into a flat dictionary.
        
        prompt_construction_params = self._prepare_prompt_params(novel_data, volume_index, chapter_index)
        if isinstance(prompt_construction_params, str): # Error string from _prepare_prompt_params
            raise ValueError(prompt_construction_params)

        # Example using PromptManager, assuming a template named "ChapterGenerationTemplate"
        # prompt = self.prompt_manager.format_prompt("StandardChapterTemplate", **prompt_construction_params)
        # if not prompt:
        #     # Fallback to old method or raise error
        #     prompt = self._create_chapter_prompt_from_params(prompt_construction_params)
        #     if not prompt: # If _create_chapter_prompt_from_params also fails (e.g. due to missing keys)
        #         raise ValueError("Could not create chapter generation prompt.")
        
        # For now, let's assume _create_chapter_prompt is adapted or a new method is used
        prompt = self._create_chapter_prompt_from_params(prompt_construction_params)


        # The callback in generate_stream is for the UI/caller to get chunks.
        # The callback in the original ChapterGenerator was also for this.
        # The AIModel's generate_stream should yield chunks, and this method will yield them further.
        # The NovelGenerator's generate_chapter_stream will then consume this.
        
        # This method is for non-streaming, so it awaits the full response.
        # The streaming version will be generate_chapter_stream.
        
        # If the AI model's generate method itself supports a callback for intermediate chunks (unlikely for non-stream)
        # then it could be passed. But typically, for non-streaming, we await the full result.
        # The `callback` parameter here seems to be a leftover from a design where
        # even non-streaming might have had progress updates. For a library API,
        # non-streaming `generate_chapter` should just return the full string.
        # The `generate_chapter_stream` will handle streaming.
        # Removing callback from non-streaming version for clarity.
        
        # return await self.ai_model.generate(prompt)
        # The NovelGenerator expects this to be async.
        # If self.ai_model.generate is async, this is fine.
        
        # The original code had a callback for generate_stream, let's ensure generate() is just plain.
        # The `callback` parameter in the original `generate_chapter` was for streaming.
        # This method is now the non-streaming one.
        
        # If the original callback was for UI updates even for non-streaming (e.g. "Generating..."),
        # that's a UI concern, not for the library's core generation method.
        
        return await self.ai_model.generate(prompt)


    async def generate_chapter_stream(self, novel_data: dict, volume_index: int, chapter_index: int, callback=None):
        """
        流式生成章节内容. This is the new streaming method.
        Args:
            novel_data: 小说数据 (包含大纲等)
            volume_index: 卷索引
            chapter_index: 章节索引
            callback: (Optional) A callback function that will be called with each chunk of text.
                      This callback is for the caller of this library method.
        Yields:
            str: Chunks of the generated chapter content.
        """
        prompt_construction_params = self._prepare_prompt_params(novel_data, volume_index, chapter_index)
        if isinstance(prompt_construction_params, str): # Error string
            raise ValueError(prompt_construction_params)

        # prompt = self.prompt_manager.format_prompt("StandardChapterTemplate", **prompt_construction_params)
        # if not prompt:
        #     prompt = self._create_chapter_prompt_from_params(prompt_construction_params)
        #     if not prompt:
        #          raise ValueError("Could not create chapter generation prompt for streaming.")
        prompt = self._create_chapter_prompt_from_params(prompt_construction_params)

        # The AIModel's generate_stream is an async generator.
        # We iterate over it and yield its chunks.
        # The `callback` here is for the *user of this library method*, if they want immediate chunks
        # in addition to iterating the async generator.
        async for chunk in self.ai_model.generate_stream(prompt): # Pass model's own callback if it has one for internal use
            if callback:
                # If callback is async, it should be awaited or scheduled.
                # For simplicity, assume sync callback or handle appropriately.
                if asyncio.iscoroutinefunction(callback):
                    await callback(chunk)
                else:
                    callback(chunk)
            yield chunk

    def _prepare_prompt_params(self, novel_data, volume_index, chapter_index):
        """Helper to gather all necessary parameters for prompt creation."""
        params = {}
        params["title"] = novel_data.get("title", "未命名小说")
        params["theme"] = novel_data.get("theme", "")
        params["worldbuilding"] = novel_data.get("worldbuilding", "")
        
        characters = novel_data.get("characters", [])
        characters_info_str = ""
        for char in characters:
            characters_info_str += f"- {char.get('name', '')}: {char.get('identity', '')}, {char.get('personality', '')}, {char.get('background', '')}\n"
        params["characters_info"] = characters_info_str

        volumes = novel_data.get("volumes", [])
        if not isinstance(volumes, list) or volume_index >= len(volumes):
            return f"错误：卷索引 {volume_index} 超出范围或卷数据无效"
        
        current_volume = volumes[volume_index]
        if not isinstance(current_volume, dict):
            return f"错误：卷数据格式不正确 (索引 {volume_index})"

        params["volume_title"] = current_volume.get("title", f"第{volume_index+1}卷")
        params["volume_description"] = current_volume.get("description", "")

        chapters = current_volume.get("chapters", [])
        if not isinstance(chapters, list) or chapter_index >= len(chapters):
            return f"错误：章节索引 {chapter_index} 超出范围或章节数据无效"
        
        current_chapter = chapters[chapter_index]
        if not isinstance(current_chapter, dict):
             return f"错误：章节数据格式不正确 (卷 {volume_index}, 章 {chapter_index})"

        params["chapter_title"] = current_chapter.get("title", f"第{chapter_index+1}章")
        params["chapter_summary"] = current_chapter.get("summary", "")

        previous_chapter_summary = ""
        if chapter_index > 0:
            if chapter_index -1 < len(chapters): # Check bounds for previous chapter
                previous_chapter = chapters[chapter_index - 1]
                if isinstance(previous_chapter, dict):
                    previous_chapter_summary = previous_chapter.get("summary", "")
        params["previous_chapter_summary"] = previous_chapter_summary

        next_chapter_summary = ""
        if chapter_index < len(chapters) - 1:
            next_chapter = chapters[chapter_index + 1]
            if isinstance(next_chapter, dict):
                next_chapter_summary = next_chapter.get("summary", "")
        params["next_chapter_summary"] = next_chapter_summary
        
        return params

    def _create_chapter_prompt_from_params(self, params: dict):
        """Creates the chapter prompt string from a dictionary of parameters."""
        # This is the old _create_chapter_prompt, adapted to take a params dict.
        # This could be replaced by a template in prompt_templates.json and use self.prompt_manager
        title = params.get("title", "未命名小说")
        theme = params.get("theme", "")
        worldbuilding = params.get("worldbuilding", "")
        characters_info = params.get("characters_info", "")
        volume_title = params.get("volume_title", "")
        volume_description = params.get("volume_description", "")
        chapter_title = params.get("chapter_title", "")
        chapter_summary = params.get("chapter_summary", "")
        previous_chapter_summary = params.get("previous_chapter_summary", "")
        next_chapter_summary = params.get("next_chapter_summary", "")

        return f"""
        请为以下小说生成一个完整的章节内容：

        小说标题：{title}
        核心主题：{theme}
        世界观设定：{worldbuilding}

        主要人物：
        {characters_info}

        当前卷：{volume_title}
        卷简介：{volume_description}

        当前章节：{chapter_title}
        章节摘要：{chapter_summary}

        {"前一章节摘要：" + previous_chapter_summary if previous_chapter_summary else ""}
        {"后一章节摘要：" + next_chapter_summary if next_chapter_summary else ""}

        请根据以上信息，创作一个完整、连贯、生动的章节内容。内容应该：
        1. 符合章节摘要的描述
        2. 与前后章节保持连贯
        3. 展现人物性格和发展
        4. 符合小说的整体风格和主题
        5. 包含丰富的对话、描写和情节发展

        请直接返回章节内容，不要包含其他解释或说明。
        """

    # Original _create_chapter_prompt is kept for reference or if direct use is still needed,
    # but _create_chapter_prompt_from_params is preferred for use with _prepare_prompt_params.
    def _create_chapter_prompt(self, novel_data, volume_index, chapter_index):
        """创建章节生成的提示词"""
        # 获取小说基本信息
        title = outline.get("title", "未命名小说")
        theme = outline.get("theme", "")
        worldbuilding = outline.get("worldbuilding", "")

        # 获取主要人物信息
        characters = outline.get("characters", [])
        characters_info = ""
        for char in characters:
            characters_info += f"- {char.get('name', '')}: {char.get('identity', '')}, {char.get('personality', '')}, {char.get('background', '')}\n"

        # 获取当前卷的信息
        volumes = outline.get("volumes", [])
        if volume_index >= len(volumes):
            return f"错误：卷索引 {volume_index} 超出范围"

        current_volume = volumes[volume_index]
        volume_title = current_volume.get("title", f"第{volume_index+1}卷")
        volume_description = current_volume.get("description", "")

        # 获取当前章节的信息
        chapters = current_volume.get("chapters", [])
        if chapter_index >= len(chapters):
            return f"错误：章节索引 {chapter_index} 超出范围"

        current_chapter = chapters[chapter_index]
        chapter_title = current_chapter.get("title", f"第{chapter_index+1}章")
        chapter_summary = current_chapter.get("summary", "")

        # 获取前一章节的信息（如果有）
        previous_chapter_summary = ""
        if chapter_index > 0:
            previous_chapter = chapters[chapter_index - 1]
            previous_chapter_summary = previous_chapter.get("summary", "")

        # 获取后一章节的信息（如果有）
        next_chapter_summary = ""
        if chapter_index < len(chapters) - 1:
            next_chapter = chapters[chapter_index + 1]
            next_chapter_summary = next_chapter.get("summary", "")

        return f"""
        请为以下小说生成一个完整的章节内容：

        小说标题：{title}
        核心主题：{theme}
        世界观设定：{worldbuilding}

        主要人物：
        {characters_info}

        当前卷：{volume_title}
        卷简介：{volume_description}

        当前章节：{chapter_title}
        章节摘要：{chapter_summary}

        {"前一章节摘要：" + previous_chapter_summary if previous_chapter_summary else ""}
        {"后一章节摘要：" + next_chapter_summary if next_chapter_summary else ""}

        请根据以上信息，创作一个完整、连贯、生动的章节内容。内容应该：
        1. 符合章节摘要的描述
        2. 与前后章节保持连贯
        3. 展现人物性格和发展
        4. 符合小说的整体风格和主题
        5. 包含丰富的对话、描写和情节发展

        请直接返回章节内容，不要包含其他解释或说明。
        """