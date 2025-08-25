# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/21
import platform

system = platform.system().lower()
if system == 'windows':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())