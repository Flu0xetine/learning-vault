import asyncio


async def call_model() -> str:
    await asyncio.sleep(5)
    return "模型回答"


async def show_progress() -> None:
    while True:
        print("仍在等待模型……")
        await asyncio.sleep(0.5)


async def main() -> None:
    progress_task = asyncio.create_task(show_progress())

    try:
        result = await asyncio.wait_for(
            call_model(),
            timeout=2,
        )
        print(result)
    except asyncio.TimeoutError:
        print("模型调用超时")
    finally:
        progress_task.cancel()


asyncio.run(main())