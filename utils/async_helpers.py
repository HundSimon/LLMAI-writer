#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
纯异步辅助函数和类。
此文件用于存放不依赖任何特定UI框架（如PyQt6）的异步工具。
"""

import asyncio
from typing import List, Any, Coroutine, TypeVar

_T = TypeVar('_T')

async def run_concurrently(coroutines: List[Coroutine[Any, Any, _T]]) -> List[_T]:
    """
    并发运行多个协程并收集它们的结果。

    Args:
        coroutines: 要并发运行的协程列表。

    Returns:
        一个列表，包含每个协程的返回结果，顺序与输入列表一致。
    """
    results = await asyncio.gather(*coroutines)
    return results

# 可以在此添加更多纯异步辅助函数，例如：
# - 带超时的异步任务执行器
# - 异步信号量或锁的简单封装
# - 异步任务组管理