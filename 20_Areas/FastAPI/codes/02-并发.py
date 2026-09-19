import asyncio


async def task_a() -> None:
    print("A 开始")
    await asyncio.sleep(3)
    print("A 结束")
    return "a"


async def task_b() -> None:
    print("B 开始")
    await asyncio.sleep(2)
    print("B 结束")
    return "b"

# 1.asyncio.gather(task_a(), task_b()) 表示并发运行这些任务，并接收返回值
# await 等待它们全部完成
async def main() -> None:
    a,b = await asyncio.gather(
        task_a(),
        task_b(),
    )
    print(a,b)

# 2.否则顺序执行
async def main0() -> None:
    result_a = await task_a() 
    # main 暂停，等待 A ,A 已经创建，可以运行,但 B 未创建不能并发
    result_b = await task_b()

# 3. 或者用 tsk_a = asyncio.create_task(task_a()) 建立任务也可实现并发
# asyncio.create_task 只是把任务分配给 事件循环 并不启动任务
# result_a = await tsk_a() 时事件循环 才 获得控制权开始执行
async def main2()->None:
    tsk_a = asyncio.create_task(task_a())
    tsk_b = asyncio.create_task(task_b())

    result_a = await tsk_a()
    result_b = await tsk_b()
# ==假设 A 需要 等待 3 秒，B 需要 等待 1 秒  （并发等待，不是 CPU 并行计算）
# 0 秒：创建 A
# 0 秒：创建 B
# 0 秒：main 等待 A
# 0 秒：A 和 B 开始
# 1 秒：B 完成
# 3 秒：A 完成
# 3 秒：main 恢复，得到 result_a
# 3 秒：main 执行 await B
# 3 秒：B 已经完成，立即得到 result_b
# ==假设 A 需要 1 秒，B 需要 3 秒：
# 0 秒：A 和 B 开始
# 1 秒：A 完成，main 得到 result_a
# 1 秒：main 执行 await B
# 1～3 秒：main 再次暂停，继续等待 B
# 3 秒：B 完成，main 恢复


asyncio.run(main2())
