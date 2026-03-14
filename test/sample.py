import asyncio

class DatabaseConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

async def process_data(data: list[int]) -> int:
    processed = [await asyncio.to_thread(sum, [x]) for x in data]
    try:
        with DatabaseConnection() as db:
            db.save(sum(processed))
    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Cleanup complete")

asyncio.run(process_data([1, 2, 3]))