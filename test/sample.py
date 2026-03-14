import asyncio

class DatabaseConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

async def process_data(data: list[int]) -> int:
    processed = [await x for x in data if isinstance(x, asyncio.Future)]
    try:
        with DatabaseConnection() as db:
            db.save(sum(processed))
    except Exception as e:
        print(f"Error: {e}")

async def get_data():
    return [asyncio.create_task(asyncio.sleep(1)), asyncio.create_task(asyncio.sleep(2)), asyncio.create_task(asyncio.sleep(3))]

async def main():
    data = await get_data()
    await process_data(data)

asyncio.run(main())