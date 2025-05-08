import asyncio
import os
from utils.config_manager import ConfigManager
from models.siliconflow_model import SiliconFlowModel

async def test_siliconflow():
    """测试 SiliconFlow 模型"""
    print("开始测试 SiliconFlow 模型...")

    # 确保 config.ini 文件存在
    if not os.path.exists("config.ini"):
        print("错误：找不到 config.ini 文件。请确保配置文件存在于脚本同级目录。")
        return

    try:
        # 加载配置
        print("加载配置 (config.ini)...")
        config_manager = ConfigManager()
        print("配置加载成功。")

        # 初始化模型
        print("初始化 SiliconFlowModel...")
        # 检查 API Key 是否配置
        api_key = config_manager.get_api_key('siliconflow')
        if not api_key:
            print("\n错误：在 config.ini 中未找到或未设置 'siliconflow_api_key'。")
            print("请在 [API_KEYS] 部分添加 'siliconflow_api_key = YOUR_KEY_HERE'")
            return

        model = SiliconFlowModel(config_manager)
        print(f"模型 '{model.name}' 初始化成功。")
        print(f"  - 使用模型: {model.model_name}")
        print(f"  - API 地址: {model.api_url}")
        # 不打印 API Key

        # 测试提示词
        test_prompt = "你好，请介绍一下你自己。"
        print(f"\n测试提示词: '{test_prompt}'")

        # 调用 generate 方法 (非流式)
        print("\n正在调用 generate 方法 (非流式)...")
        try:
            response = await model.generate(test_prompt)
            print("\n非流式响应成功:")
            print("-" * 20)
            print(response)
            print("-" * 20)
        except Exception as e:
            print(f"\n调用 generate 方法时出错: {e}")

        # 调用 generate_stream 方法 (流式)
        print("\n正在调用 generate_stream 方法 (流式)...")
        try:
            print("\n流式响应:")
            print("-" * 20)
            async for chunk in model.generate_stream(test_prompt):
                print(chunk, end='', flush=True)
            print("\n" + "-" * 20)
            print("流式响应结束。")
        except Exception as e:
            print(f"\n调用 generate_stream 方法时出错: {e}")

    except ValueError as ve:
        print(f"\n初始化或配置错误: {ve}")
    except Exception as e:
        print(f"\n发生未知错误: {e}")

if __name__ == "__main__":
    # 运行异步测试函数
    # 在Windows上，可能需要设置事件循环策略以避免某些asyncio错误
    if os.name == 'nt':
         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_siliconflow())