import asyncio
# 1.async def 表示这个函数可能包含需要等待的操作。
async def greet() -> str:
    await asyncio.sleep(2)
    return "你好"

result = greet() 
# 这里不会直接得到 "你好"，而会得到一个协程对象。
# greet()里的代码也不会运行
# 协程: 一项已经描述好，但还没有执行完成的异步任务。


# 2.await 用来等待一个协程完成，并取得它的返回值。
# 等待：执行到 await 时，假如 await 所等待的操作暂时不能完成，那么当前协程会暂停并让出执行权，
#      事件循环去运行其他可执行的协程；等等待的操作完成后，该协程变为“就绪”状态；等事件循环之后再次调度到它时再恢复当前协程。
# 暂时不能完成： 
# await 必须写在由 async def 定义的函数里面。
# 也不能写在最外层
async def main() -> None:
    message = await greet() # greet() 中有等待 ，控制权交给事件循环，但循环为空，greet()就绪后恢复
    await asyncio.sleep(2)
    print(message)

# 3.asyncio.run(main()) 写在最外层来启动异步程序。

asyncio.run(main()) # 创建并启动事件循环

# 只有一个任务，本质顺序执行