import json
from models.ai_model import AIModel

class OutlineGenerator:
    """小说大纲生成器"""

    def __init__(self, ai_model: AIModel, config_manager):
        """
        初始化大纲生成器

        Args:
            ai_model: AI模型实例
            config_manager: 配置管理器实例
        """
        self.ai_model = ai_model
        self.config_manager = config_manager

    async def generate_outline(self, title, genre, theme, style, synopsis, volume_count, chapters_per_volume, words_per_chapter, new_character_count, selected_characters=None, start_volume=None, start_chapter=None, end_volume=None, end_chapter=None, existing_outline=None, callback=None):
        """
        生成小说大纲

        Args:
            title: 小说标题
            genre: 小说类型
            theme: 小说主题
            style: 小说风格
            synopsis: 小说简介
            volume_count: 卷数
            chapters_per_volume: 每卷章节数
            words_per_chapter: 每章字数
            new_character_count: 新生成角色数量
            selected_characters: 选择的已有角色列表
            start_volume: 起始卷号（从1开始）
            start_chapter: 起始章节号（从1开始）
            end_volume: 结束卷号（从1开始）
            end_chapter: 结束章节号（从1开始）
            existing_outline: 已有的大纲内容（用于指定范围生成）
            callback: 回调函数，用于接收流式生成的内容

        Returns:
            生成的大纲（JSON格式）
        """
        prompt = self._create_outline_prompt(title, genre, theme, style, synopsis, volume_count, chapters_per_volume, words_per_chapter, new_character_count, selected_characters, start_volume, start_chapter, end_volume, end_chapter, existing_outline)

        if callback:
            # 流式生成
            full_response = ""
            async for chunk in self.ai_model.generate_stream(prompt, callback):
                full_response += chunk
            generated_outline = self._parse_outline(full_response)
        else:
            # 非流式生成
            response = await self.ai_model.generate(prompt)
            generated_outline = self._parse_outline(response)

        # 如果有已有大纲且指定了生成范围，则合并大纲
        if existing_outline and start_volume and end_volume:
            return self._merge_outlines(existing_outline, generated_outline, start_volume, start_chapter, end_volume, end_chapter)
        else:
            return generated_outline

    async def optimize_outline(self, outline, callback=None):
        """
        优化小说大纲

        Args:
            outline: 初步大纲（JSON格式）
            callback: 回调函数，用于接收流式生成的内容

        Returns:
            优化后的大纲（JSON格式）
        """
        prompt = self._create_optimization_prompt(outline)

        if callback:
            # 流式生成
            full_response = ""
            async for chunk in self.ai_model.generate_stream(prompt, callback):
                full_response += chunk
            return self._parse_outline(full_response)
        else:
            # 非流式生成
            response = await self.ai_model.generate(prompt)
            return self._parse_outline(response)

    def _create_outline_prompt(self, title, genre, theme, style, synopsis, volume_count, chapters_per_volume, words_per_chapter, new_character_count, selected_characters=None, start_volume=None, start_chapter=None, end_volume=None, end_chapter=None, existing_outline=None):
        """创建大纲生成的提示词"""
        # 构建提示词基础部分
        if start_volume and end_volume:
            prompt = f"""
            请为我创建一部小说的指定范围的详细大纲，以JSON格式返回。小说信息如下：
            """
        else:
            prompt = f"""
            请为我创建一部小说的详细大纲，以JSON格式返回。小说信息如下：
            """

        # 根据用户输入添加相应信息
        if title:
            prompt += f"""
        小说标题：{title}"""

        if genre:
            prompt += f"""
        小说类型：{genre}"""

        if theme:
            prompt += f"""
        主题：{theme}"""

        if style:
            prompt += f"""
        风格：{style}"""

        if synopsis:
            prompt += f"""
        简介：{synopsis}"""

        # 添加结构信息
        prompt += f"""
        卷数：{volume_count} 卷
        每卷章节数：{chapters_per_volume} 章
        每章字数：{words_per_chapter} 字
        总字数：约 {volume_count * chapters_per_volume * words_per_chapter // 10000} 万字

        人物设置：
        新生成角色数量：{new_character_count} 个
        """

        # 添加选择的角色信息
        if selected_characters and len(selected_characters) > 0:
            prompt += f"""
        已选择的出场角色：
        """
            character_names = [char.get("name", "未命名角色") for char in selected_characters]
            prompt += ", ".join(character_names)
            prompt += "\n"

        # 特别提醒AI关于角色生成的说明
        prompt += f"""
        特别说明：
        1. 新生成角色数量 {new_character_count} 个仅指需要新创建的角色数量
        2. 请不要重复创建已有角色，已有角色会在"已选择的出场角色"中列出
        3. 在生成的JSON中，characters字段只包含新创建的角色，不要包含已有角色
        """

        # 如果指定了生成范围
        if start_volume and end_volume:
            prompt += f"""

        生成范围：从第{start_volume}卷{f'第{start_chapter}章' if start_chapter else '开始'} 到 第{end_volume}卷{f'第{end_chapter}章' if end_chapter else '结束'}
        """

            # 如果有已存在的大纲，添加到提示中
            if existing_outline:
                # 提取已有大纲的基本信息
                existing_title = existing_outline.get('title', '')
                existing_theme = existing_outline.get('theme', '')
                existing_synopsis = existing_outline.get('synopsis', '')
                existing_worldbuilding = existing_outline.get('worldbuilding', '')

                # 提取已有的角色信息
                existing_characters = existing_outline.get('characters', [])
                characters_info = ""
                for char in existing_characters:
                    characters_info += f"- {char.get('name', '')}: {char.get('identity', '')}, {char.get('personality', '')}, {char.get('background', '')}\\n"

                # 提取已有的卷和章节信息
                existing_volumes = existing_outline.get('volumes', [])
                volumes_info = ""
                for i, vol in enumerate(existing_volumes):
                    volumes_info += f"第{i+1}卷：{vol.get('title', '')}\\n"
                    volumes_info += f"简介：{vol.get('description', '')}\\n"
                    chapters = vol.get('chapters', [])
                    for j, chap in enumerate(chapters):
                        volumes_info += f"  第{j+1}章：{chap.get('title', '')}\\n"
                        volumes_info += f"  摘要：{chap.get('summary', '')}\\n"

                prompt += f"""

        已有的大纲信息：
        标题：{existing_title}
        核心主题：{existing_theme}
        故事梗概：{existing_synopsis}
        世界观设定：{existing_worldbuilding}

        已有的角色信息：
{characters_info}

        已有的卷和章节结构：
{volumes_info}

        注意：请只生成指定范围内的卷和章节，不要重复已有的内容。如果指定范围内的卷或章节已经存在，请替换它们。你只需要返回指定范围内的卷和章节，不需要返回其他卷和章节。
        """

        prompt += f"""

        请生成以下内容：
        1. 小说标题
        2. 核心主题
        3. 主要人物（包括姓名、身份、年龄、性别、性格特点、背景故事、外貌描述、能力特长和目标动机）
        4. 故事梗概
        5. 分卷结构（每卷包含标题、简介和具体章节）
        6. 世界观设定

        特别要求：
        1. 卷标题必须包含卷号，如"第二卷：卷标题"，卷号必须与实际卷号一致
        2. 章节标题必须包含章节号，如"第三章：章节标题"，章节号必须与实际章节号一致
        3. 只生成指定数量的新角色，不要重复已有角色
        4. 在characters字段中只包含新创建的角色，不要包含已有角色
        """

        if start_volume and end_volume:
            prompt += f"""
        3. 只生成指定范围内的卷和章节，但保持与已有大纲的一致性
        4. 不要重复已有的内容，只返回指定范围内的卷和章节
        5. 在JSON的volumes字段中，只包含指定范围内的卷，不要包含其他卷
        """

        prompt += f"""

        请确保大纲结构完整、逻辑合理，并以下面的JSON格式返回：

        ```json
        {{
            "title": "小说标题",
            "theme": "核心主题",
            "characters": [
                {{
                    "name": "角色名",
                    "identity": "身份",
                    "age": "年龄",
                    "gender": "性别",
                    "personality": "性格特点（详细描述）",
                    "background": "背景故事（详细描述）",
                    "appearance": "外貌描述（详细描述）",
                    "abilities": "能力特长（详细描述）",
                    "goals": "目标动机（详细描述）"
                }}
            ],
            "synopsis": "故事梗概",
            "volumes": [
                {{
                    "title": "第{start_volume}卷：卷标题",
                    "description": "卷简介",
                    "chapters": [
                        {{
                            "title": "第{start_chapter}章：章节标题",
                            "summary": "章节摘要"
                        }},
                        {{
                            "title": "第2章：章节标题",
                            "summary": "章节摘要"
                        }}
                    ]
                }},
                {{
                    "title": "第2卷：卷标题",
                    "description": "卷简介",
                    "chapters": [
                        {{
                            "title": "第1章：章节标题",
                            "summary": "章节摘要"
                        }}
                    ]
                }}
            ],
            "worldbuilding": "世界观设定"
        }}
        ```

        注意：如果指定了生成范围，请只在volumes字段中包含范围内的卷，不要包含其他卷。

        请只返回JSON格式的内容，不要包含其他解释或说明。
        """

        return prompt

    def _create_optimization_prompt(self, outline):
        """创建大纲优化的提示词"""
        outline_json = json.dumps(outline, ensure_ascii=False, indent=2)

        return f"""
        请优化以下小说大纲，使其更加完善：

        {outline_json}

        请进行以下优化：
        1. 完善角色背景和动机
        2. 增强情节的起伏和转折
        3. 丰富世界观设定的细节
        4. 确保各章节和卷之间的逻辑连贯

        请保持原有的JSON格式，只返回优化后的JSON内容，不要包含其他解释或说明。
        """

    def _merge_outlines(self, existing_outline, generated_outline, start_volume, start_chapter, end_volume, end_chapter):
        """合并已有大纲和新生成的大纲

        Args:
            existing_outline: 已有的大纲
            generated_outline: 新生成的大纲
            start_volume: 起始卷号（从1开始）
            start_chapter: 起始章节号（从1开始）
            end_volume: 结束卷号（从1开始）
            end_chapter: 结束章节号（从1开始）

        Returns:
            合并后的大纲
        """
        # 创建结果大纲，基于已有大纲
        result_outline = existing_outline.copy()

        # 如果新生成的大纲中有volumes字段
        if 'volumes' in generated_outline and generated_outline['volumes']:
            # 确保结果大纲中有volumes字段
            if 'volumes' not in result_outline:
                result_outline['volumes'] = []

            # 遍历新生成的卷
            for new_volume in generated_outline['volumes']:
                # 提取卷号（从标题中提取数字）
                volume_title = new_volume.get('title', '')
                volume_number = 0

                # 尝试从标题中提取卷号
                import re
                match = re.search(r'第(\d+)卷', volume_title)
                if match:
                    volume_number = int(match.group(1))

                # 如果卷号在指定范围内
                if start_volume <= volume_number <= end_volume:
                    # 检查结果大纲中是否已有该卷
                    existing_volume_index = None
                    for i, vol in enumerate(result_outline['volumes']):
                        vol_title = vol.get('title', '')
                        match = re.search(r'第(\d+)卷', vol_title)
                        if match and int(match.group(1)) == volume_number:
                            existing_volume_index = i
                            break

                    # 如果已有该卷，替换或合并章节
                    if existing_volume_index is not None:
                        # 保留卷标题和简介
                        result_outline['volumes'][existing_volume_index]['title'] = new_volume.get('title', result_outline['volumes'][existing_volume_index]['title'])
                        result_outline['volumes'][existing_volume_index]['description'] = new_volume.get('description', result_outline['volumes'][existing_volume_index]['description'])

                        # 确保章节列表存在
                        if 'chapters' not in result_outline['volumes'][existing_volume_index]:
                            result_outline['volumes'][existing_volume_index]['chapters'] = []

                        # 如果有新章节
                        if 'chapters' in new_volume and new_volume['chapters']:
                            # 遍历新章节
                            for new_chapter in new_volume['chapters']:
                                # 提取章节号
                                chapter_title = new_chapter.get('title', '')
                                chapter_number = 0

                                match = re.search(r'第(\d+)章', chapter_title)
                                if match:
                                    chapter_number = int(match.group(1))

                                # 判断章节是否在范围内
                                in_range = True
                                if volume_number == start_volume and start_chapter and chapter_number < start_chapter:
                                    in_range = False
                                if volume_number == end_volume and end_chapter and chapter_number > end_chapter:
                                    in_range = False

                                if in_range:
                                    # 检查是否已有该章节
                                    existing_chapter_index = None
                                    for j, chap in enumerate(result_outline['volumes'][existing_volume_index]['chapters']):
                                        chap_title = chap.get('title', '')
                                        match = re.search(r'第(\d+)章', chap_title)
                                        if match and int(match.group(1)) == chapter_number:
                                            existing_chapter_index = j
                                            break

                                    # 如果已有该章节，替换
                                    if existing_chapter_index is not None:
                                        result_outline['volumes'][existing_volume_index]['chapters'][existing_chapter_index] = new_chapter
                                    else:
                                        # 如果没有，添加到适当位置
                                        # 找到插入位置
                                        insert_index = 0
                                        for j, chap in enumerate(result_outline['volumes'][existing_volume_index]['chapters']):
                                            chap_title = chap.get('title', '')
                                            match = re.search(r'第(\d+)章', chap_title)
                                            if match and int(match.group(1)) < chapter_number:
                                                insert_index = j + 1

                                        # 插入新章节
                                        result_outline['volumes'][existing_volume_index]['chapters'].insert(insert_index, new_chapter)
                    else:
                        # 如果没有该卷，添加到适当位置
                        # 找到插入位置
                        insert_index = 0
                        for i, vol in enumerate(result_outline['volumes']):
                            vol_title = vol.get('title', '')
                            match = re.search(r'第(\d+)卷', vol_title)
                            if match and int(match.group(1)) < volume_number:
                                insert_index = i + 1

                        # 插入新卷
                        result_outline['volumes'].insert(insert_index, new_volume)

        # 更新其他字段（如果有新内容）
        if 'title' in generated_outline and generated_outline['title']:
            result_outline['title'] = generated_outline['title']
        if 'theme' in generated_outline and generated_outline['theme']:
            result_outline['theme'] = generated_outline['theme']
        if 'synopsis' in generated_outline and generated_outline['synopsis']:
            result_outline['synopsis'] = generated_outline['synopsis']
        if 'worldbuilding' in generated_outline and generated_outline['worldbuilding']:
            result_outline['worldbuilding'] = generated_outline['worldbuilding']
        if 'characters' in generated_outline and generated_outline['characters']:
            result_outline['characters'] = generated_outline['characters']

        # 最终排序卷和章节，确保顺序正确
        if 'volumes' in result_outline and result_outline['volumes']:
            # 对卷进行排序
            import re
            def get_volume_number(volume):
                title = volume.get('title', '')
                match = re.search(r'第(\d+)卷', title)
                if match:
                    return int(match.group(1))
                return 0

            result_outline['volumes'].sort(key=get_volume_number)

            # 对每个卷的章节进行排序
            for volume in result_outline['volumes']:
                if 'chapters' in volume and volume['chapters']:
                    def get_chapter_number(chapter):
                        title = chapter.get('title', '')
                        match = re.search(r'第(\d+)章', title)
                        if match:
                            return int(match.group(1))
                        return 0

                    volume['chapters'].sort(key=get_chapter_number)

        return result_outline

    def _parse_outline(self, response):
        """解析AI生成的大纲响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            try:
                json_start = response.find('```json')
                if json_start != -1:
                    json_start += 7  # 跳过```json
                else:
                    json_start = response.find('{')

                json_end = response.rfind('```')
                if json_end != -1 and json_end > json_start:
                    json_text = response[json_start:json_end].strip()
                else:
                    json_end = response.rfind('}')
                    json_text = response[json_start:json_end+1].strip()

                return json.loads(json_text)
            except (json.JSONDecodeError, ValueError):
                # 如果仍然失败，返回原始响应
                return {"error": "无法解析响应", "raw_response": response}
