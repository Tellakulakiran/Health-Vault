import asyncio
import asyncpg

PROJECT_ID = "aqjcsrmkxjtihbryxeyk"
PASSWORD = "QvkThMtgQ9aWZNNk"

REGIONS = [
    "ap-south-1", "us-east-1", "us-west-1", "us-west-2",
    "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1",
    "ap-southeast-2", "sa-east-1", "ca-central-1", "eu-west-2", "eu-west-3", "ap-northeast-2"
]

async def check_region(region):
    url = f"postgresql://postgres.{PROJECT_ID}:{PASSWORD}@aws-0-{region}.pooler.supabase.com:6543/postgres"
    try:
        # 3 second timeout for each
        conn = await asyncpg.connect(url, timeout=3.0)
        await conn.close()
        print(f"✅ SUCCESS: {url}")
        return url
    except Exception as e:
        # Suppress errors for failures
        pass
    return None

async def main():
    print("Scanning Supabase regions for IPv4 Pooler...")
    tasks = [check_region(r) for r in REGIONS]
    results = await asyncio.gather(*tasks)
    
    found = [r for r in results if r]
    if found:
        print(f"\nFound Valid IPv4 Pooler URL: {found[0]}")
    else:
        print("\nCould not resolve a valid connection pooler URL.")

if __name__ == "__main__":
    asyncio.run(main())
