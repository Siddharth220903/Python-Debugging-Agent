import asyncio

class DatabaseConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def process_data(self, data: list[int]) -> None:
        processed = [await asyncio.to_thread(sum, [x]) for x in data]
        try:
            with DatabaseConnection() as db:
                db.save(processed)
        except Exception as e:
            print(f"Error: {e}")

        finally:
            print("Cleanup complete")

    # Removed duplicate method
