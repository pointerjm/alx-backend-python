import asyncio
import aiosqlite

# Fetch all users asynchronously
async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

# Fetch users older than 40 asynchronously
async def async_fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()

# Run both queries concurrently
async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print("All users:")
    for user in all_users:
        print(user)
    print("\nUsers older than 40:")
    for user in older_users:
        print(user)

# Execute the concurrent fetch
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
