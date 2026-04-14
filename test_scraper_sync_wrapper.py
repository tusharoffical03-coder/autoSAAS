import asyncio
from maps_scraper import run_maps_scraper

def test_sync():
    print("Starting sync wrapper test...")
    # This is what I added to main.py
    count = asyncio.run(run_maps_scraper(niche="Gym", city="Dubai", max_results=1))
    print(f"Test complete. Saved: {count}")

if __name__ == "__main__":
    test_sync()
