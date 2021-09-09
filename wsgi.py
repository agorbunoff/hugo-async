import asyncio

from app.main import hugo

if __name__ == "__main__":
    asyncio.run(hugo.serve())
