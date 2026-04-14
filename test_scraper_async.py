import asyncio
from maps_scraper import run_maps_scraper

async def test():
    print("Starting async test...")
    # Just scrape 1 result to be fast
    count = await run_maps_scraper(niche="Gym", city="Dubai", max_results=1)
    print(f"Test complete. Saved: {count}")

if __name__ == "__main__":
    asyncio.run(test())
