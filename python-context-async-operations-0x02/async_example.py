import asyncio
import aiosqlite

async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def main():
    users = await async_fetch_users()
    print(users)

if __name__ == "__main__":
    asyncio.run(main())
