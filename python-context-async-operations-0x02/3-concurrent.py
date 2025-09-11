import asyncio
import aiosqlite

async def async_fetch_users(db_name):
    async with aiosqlite.connect(db_name) as db:
        cursor = await db.execute('SELECT * FROM users')
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def async_fetch_older_users(db_name):
    async with aiosqlite.connect(db_name) as db:
        cursor = await db.execute('SELECT * FROM users WHERE age > ?', (40,))
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def fetch_concurrently():
    db_name = 'users.db'
    users, older_users = await asyncio.gather(
        async_fetch_users(db_name),
        async_fetch_older_users(db_name)
    )
    print("All users:")
    for user in users:
        print(user)
    print("\nUsers older than 40:")
    for user in older_users:
        print(user)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())