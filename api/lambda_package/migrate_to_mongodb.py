import asyncio
from mongodb_service import connect_to_mongodb, migrate_from_json_to_mongodb

async def main():
    print("Connecting to MongoDB...")
    await connect_to_mongodb()
    print("Migrating data from JSON to MongoDB...")
    await migrate_from_json_to_mongodb()
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(main()) 