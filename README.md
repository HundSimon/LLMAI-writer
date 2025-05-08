# AI 小说生成 Python 库

一个 Python 库，利用多种大语言模型（如 GPT、Claude、Gemini 等）的能力来辅助创作和生成小说内容，包括大纲和章节。LLMAI-writer 是一个功能强大的 AI 辅助小说创作工具，利用最先进的大型语言模型帮助作家构思、规划和创作小说。无论您是经验丰富的作家还是初学者，LLMAI-writer 都能帮助您更高效地完成创作过程。

## ✨ 主要特性

*   **多模型支持**：
    *   支持多种 AI 模型接口，包括 OpenAI 的 GPT 系列、Anthropic 的 Claude 系列、Google 的 Gemini 系列。
    *   支持开源模型，如 ModelScope、SiliconFlow 以及通过 Ollama 运行的本地模型。
    *   支持任何兼容 OpenAI API 规范的自定义模型服务。
    *   所有模型均支持流式输出，实时查看生成过程。
*   **全流程创作支持**：
    *   **小说大纲生成与优化**：根据您的创意、主题和风格，AI 自动生成完整的小说大纲，并可进行优化。
    *   总大纲编辑：编辑小说标题、核心主题、故事梗概和世界观设定。
    *   章节大纲编辑：管理卷和章节结构，编辑章节摘要。
    *   人物设计：创建和管理小说中的角色，包括背景、性格、外貌等详细信息。
*   **小说章节内容生成**：
    *   基于大纲和前后章节上下文，生成连贯的章节内容。
    *   支持一次性生成和流式生成两种模式。
*   **配置与定制**：
    *   通过配置文件 ([`config.ini`](config.ini:1)) 灵活管理模型参数和 API 密钥。
    *   可定制的提示词模板 ([`prompt_templates.json`](prompt_templates.json:1))，允许用户修改和扩展用于生成任务的提示。
*   **数据管理**：
    *   小说项目数据（大纲、章节、人物等）的加载与保存 (例如 `.ainovel` 文件)。

## 📋 系统要求

> **必读提示：** 本项目库建议使用 **Python 3.9 或更高版本**！Gemini 功能依赖的 `google-genai` 库仅支持 Python 3.9+。

*   **操作系统**：Windows 10/11、macOS 10.14+、Linux
*   **Python**：3.9 或更高版本
*   **网络连接**：用于访问 AI API 服务
*   **硬盘空间**：约 100MB（不包括生成的小说文件和本地模型）

## 🚀 安装

1.  克隆本仓库：
    ```bash
    git clone <仓库URL> # 请用户自行替换为实际URL
    cd <仓库目录名>   # 请用户自行替换为实际目录名
    ```
2.  (可选) 创建并激活虚拟环境：
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ 配置

### 1. 模型配置 (`config.ini`)

您需要创建一个 [`config.ini`](config.ini:1) 文件来配置 AI 模型和 API 密钥。这是库进行 API 调用的核心配置文件。建议从项目根目录下的 [`config.example.ini`](config.example.ini:1) 文件复制并重命名得到。

关键配置部分说明：

*   **`[General]` 部分**:
    *   `default_model_name`: (可选) 指定 `NovelGenerator` 初始化时自动加载的模型名称。例如，`default_model_name = GPT`。如果设置，`NovelGenerator` 会尝试使用此名称对应的模型配置节（如 `[GPT]`）中的信息来初始化模型。
    *   `prompts_path`: (可选) 指定 [`prompt_templates.json`](prompt_templates.json:1) 文件的路径。如果未提供，`NovelGenerator` 初始化时会默认尝试加载项目根目录下的 `prompt_templates.json`。

*   **各模型配置节** (例如 `[GPT]`, `[Claude]`, `[Gemini]`, `[Ollama_Llama3]`, `[MyCustomModel]` 等):
    *   节名称 (例如 `GPT`, `Claude`, `Ollama_Llama3`) 是您在调用 `generator.select_model(model_name="节名称")` 时使用的标识符。
    *   `api_key`: (对于需要认证的云服务模型是必需的) 对应模型的 API 密钥。
    *   `model_name`: (必需) 模型提供商指定的具体模型标识符 (例如 `gpt-3.5-turbo`, `claude-3-opus-20240229`, `llama3` 等)。
    *   `base_url` (或 `api_url`): (对于自定义 OpenAI 兼容模型、Ollama、SiliconFlow 等是必需的) 对应模型的 API 基础 URL。对于 OpenAI 兼容的 API，通常指向 `v1` 路径 (例如 `http://localhost:8000/v1`)。对于 Ollama，通常是 `http://localhost:11434` (库内部会自动处理 `/api/chat` 或 `/api/generate` 路径)。

**示例 [`config.ini`](config.ini:1) 结构：**
```ini
[General]
default_model_name = GPT
# prompts_path = custom/path/to/prompts.json ; 可选

[PROXY]
host = 127.0.0.1
port = 10808
enabled = false ; 根据您的网络环境设置是否启用代理

[GPT]
api_key = YOUR_OPENAI_API_KEY
model_name = gpt-3.5-turbo
# base_url = https://your-azure-openai.openai.azure.com/ ; 如果使用 Azure OpenAI 或类似服务

[Claude]
api_key = YOUR_ANTHROPIC_API_KEY
model_name = claude-3-opus-20240229

[Gemini]
api_key = YOUR_GOOGLE_AI_KEY
model_name = gemini-1.5-flash

[Ollama_Llama3] ; 自定义节名，用于 select_model("Ollama_Llama3")
# api_key = ; Ollama 通常不需要 API Key
model_name = llama3 ; 您在 Ollama 中拉取的模型名
base_url = http://localhost:11434 ; Ollama API 的基础 URL

[MyLocalLLM] ; 示例：一个自定义的 OpenAI 兼容模型
api_key = sk-xxxxxxxxxxxx ; 可能是任意字符串，取决于服务
model_name = deepseek-coder-7b ; 服务端实际加载的模型名
base_url = http://localhost:8000/v1 ; 服务的 OpenAI 兼容 API 端点 (不含 /chat/completions)

# config.example.ini 中还有更多模型的配置示例，如 ModelScope, SiliconFlow 等
```

### 2. 提示词模板 (`prompt_templates.json`)

项目根目录下的 [`prompt_templates.json`](prompt_templates.json:1) 文件用于存储各种生成任务（如生成大纲、生成章节）所使用的提示词模板。这是一个 JSON 文件，您可以根据自己的需求修改或添加新的模板。

`NovelGenerator` ([`novel_generator.py:15`](novel_generator.py:15)) 在初始化时会加载此文件。您也可以通过在 `NovelGenerator` ([`novel_generator.py:15`](novel_generator.py:15)) 的构造函数中传递 `prompts_path` 参数来指定自定义的模板文件路径。

## 📖 使用示例 (快速开始 - Python 库调用)

以下示例展示了如何使用 `NovelGenerator` ([`novel_generator.py:15`](novel_generator.py:15)) 库来生成小说大纲和章节。请确保您已正确配置 API 密钥。

```python
import asyncio
from novel_generator import NovelGenerator # 确保 __init__.py 正确导出了 NovelGenerator

async def run_novel_generation():
    # 初始化 NovelGenerator
    # 推荐方式: 从 config.ini 加载配置
    generator = NovelGenerator() 
    # 或者指定路径:
    # generator = NovelGenerator(config_source="custom_config.ini", prompts_path="custom_prompts.json")

    try:
        # 选择模型 (假设 'GPT' 在 config.ini 中已配置 API key)
        generator.select_model(model_name="GPT")
        print(f"使用模型: {generator.current_model.model_name if generator.current_model else 'N/A'}")
    except Exception as e:
        print(f"选择模型出错: {e}")
        return

    try:
        print("\n开始生成大纲...")
        outline_creation_params = {
            "title": "迷雾中的灯塔",
            "genre": "奇幻冒险",
            "theme": "勇气与自我发现",
            "style": "史诗感，第三人称",
            "synopsis": "一个年轻的灯塔守护者发现了一张古老的地图，指向一座只在传说中存在的岛屿。为了拯救他日渐衰败的村庄，他必须踏上未知的旅程，面对海洋的怒火与内心的恐惧。",
            "volume_count": 1,
            "chapters_per_volume": 2, # 示例改为2章，加快演示
            "words_per_chapter": 1000, # 示例改小字数
            "new_character_count": 1,
            "selected_characters": [{"name": "芬恩", "description": "年轻勇敢的灯塔守护者"}]
        }
        # 调用 generate_outline，传递 prompt_params
        novel_outline_data = await generator.generate_outline(prompt_params=outline_creation_params)
        print("大纲生成完毕。")
        print(f"标题: {novel_outline_data.get('title')}")
        # print(novel_outline_data) # 可以取消注释以查看完整大纲结构

        if novel_outline_data and novel_outline_data.get('volumes'):
            print("\n开始生成第一卷第一章...")
            # 假设 outline_data 结构与 generate_chapter 期望的一致
            first_chapter_content = await generator.generate_chapter(
                outline_data=novel_outline_data,
                volume_index=0, # 第一卷
                chapter_index=0  # 第一章
            )
            print("第一章内容 (部分预览):")
            print(first_chapter_content[:300] + "...")
        else:
            print("未能从大纲中获取到卷信息，无法生成章节。")

    except Exception as e:
        print(f"生成内容时出错: {e}")

if __name__ == "__main__":
    asyncio.run(run_novel_generation())
```

## 📚 API 参考 (简要)

以下是 `NovelGenerator` ([`novel_generator.py:15`](novel_generator.py:15)) 类的主要公共 API：

*   **`NovelGenerator(config_source: Union[str, Dict, None] = None, prompts_path: Optional[str] = None)`**
    *   初始化小说生成器。
    *   `config_source`: 配置文件的路径 (str)，或配置字典 (Dict)，或 `None` (默认加载 `config.ini`)。
    *   `prompts_path`: 提示词模板文件的路径 (str)，或 `None` (默认加载 `prompt_templates.json`，或从配置中读取 `General.prompts_path`)。

*   **`select_model(model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs)`**
    *   选择并配置一个 AI 模型。
    *   `model_name`: 对应 [`config.ini`](config.ini:1) 中模型节的名称 (例如 "GPT", "Claude", "Ollama_Llama3")。
    *   `api_key`, `base_url`: 可选，用于覆盖或提供 [`config.ini`](config.ini:1) 中未指定的参数。
    *   `**kwargs`: 其他特定于模型的参数。

*   **`async generate_outline(prompt_params: Dict) -> Dict`**
    *   生成小说大纲。
    *   `prompt_params`: 一个包含生成大纲所需参数的字典，例如：
        *   `title` (str): 小说标题。
        *   `genre` (str): 小说类型。
        *   `theme` (str): 小说主题。
        *   `style` (str): 写作风格。
        *   `synopsis` (str): 故事梗概。
        *   `volume_count` (int): 卷数。
        *   `chapters_per_volume` (int): 每卷章节数。
        *   `words_per_chapter` (int): 每章字数。
        *   `new_character_count` (int): 新角色数量。
        *   `selected_characters` (Optional[List[Dict]]): 已选角色列表，每个角色是一个包含 `name` 和 `description` 的字典。
        *   (其他可选参数如 `start_volume`, `start_chapter`, `end_volume`, `end_chapter`, `existing_outline_data` 等，具体请参考 [`novel_generator.py:54`](novel_generator.py:54) 中的 `generate_outline` ([`novel_generator.py:54`](novel_generator.py:54)) 方法定义)
    *   返回一个包含大纲数据的字典。

*   **`async optimize_outline(outline_data: Dict) -> Dict`**
    *   优化现有的小说大纲。
    *   `outline_data`: 要优化的大纲数据。
    *   返回优化后的大纲数据字典。

*   **`async generate_chapter(outline_data: Dict, volume_index: int, chapter_index: int) -> str`**
    *   生成指定卷和章节的内容。
    *   `outline_data`: 完整的小说数据（通常是包含大纲的字典）。
    *   `volume_index`: 卷的索引 (0-based)。
    *   `chapter_index`: 章的索引 (0-based)。
    *   返回生成的章节内容字符串。

*   **`async generate_chapter_stream(outline_data: Dict, volume_index: int, chapter_index: int) -> AsyncIterator[str]`**
    *   流式生成指定卷和章节的内容。
    *   参数同 `generate_chapter` ([`novel_generator.py:100`](novel_generator.py:100))。
    *   返回一个异步迭代器，逐块产生章节内容字符串。

*   **`load_novel_data(filepath: str) -> Optional[Dict]`**
    *   从文件加载小说数据。
    *   `filepath`: 小说数据文件的路径。
    *   返回加载的小说数据字典，如果加载失败则为 `None`。

*   **`save_novel_data(novel_data: Dict, filepath: str) -> bool`**
    *   将小说数据保存到文件。
    *   `novel_data`: 要保存的小说数据。
    *   `filepath`: 保存文件的路径。
    *   返回 `True` 如果保存成功，否则 `False`。

## 🤝 贡献

欢迎各种形式的贡献！如果您有任何建议、错误修复或功能请求，请随时提出 Issue 或 Pull Request。

## 📄 许可证

原项目使用 MIT 许可证。

本项目使用 GNU GPL v3 协议开源
