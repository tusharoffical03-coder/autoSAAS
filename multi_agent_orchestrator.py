# ================================================================
#   MULTI_AGENT_ORCHESTRATOR.PY - Concurrent Swarm Engine
#   Launches Maps, Twitter, and Reddit agents simultaneously
# ================================================================

import asyncio
import time
import datetime
from database import SessionLocal, Lead, init_db
from maps_scraper import run_maps_scraper
from reddit_agent import run_reddit_agent
from twitter_agent import run_twitter_agent
from config import CYCLE_DELAY

async def run_swarm_cycle(niche, city):
    """
    Launch all specialized agents concurrently using asyncio.gather.
    Gathering data from Maps, Twitter, and Reddit at the exact same time.
    """
    print(f"\n[SWARM] Launching concurrent agents for: {niche} in {city}...")

    # Run all agents in parallel
    results = await asyncio.gather(
        run_maps_scraper(niche, city, max_results=10),
        run_reddit_agent(),
        run_twitter_agent(),
        return_exceptions=True
    )

    # Process results
    maps_saved = results[0] if isinstance(results[0], int) else 0
    reddit_saved = results[1] if isinstance(results[1], int) else 0
    twitter_saved = results[2] if isinstance(results[2], int) else 0

    total_saved = maps_saved + reddit_saved + twitter_saved

    print(f"\n[SWARM] Cycle Complete!")
    print(f"   [AGENT-MAPS]    : {maps_saved} leads")
    print(f"   [AGENT-REDDIT]  : {reddit_saved} leads")
    print(f"   [AGENT-TWITTER] : {twitter_saved} leads")
    print(f"   [TOTAL NEW]     : {total_saved} leads saved to DB")

    return total_saved

async def main():
    init_db()
    print("\n[INIT] Swarm Orchestrator Ready!")

    # Demo targets
    targets = [
        {"niche": "law firm", "city": "Miami"},
        {"niche": "gym", "city": "Los Angeles"},
        {"niche": "salon", "city": "Dallas"}
    ]

    cycle = 1
    while True:
        target = targets[(cycle - 1) % len(targets)]
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"\n{'='*60}")
        print(f"  🐝 SWARM CYCLE #{cycle} | ⏰ {ts} | Target: {target['niche']}")
        print(f"{'='*60}")

        await run_swarm_cycle(target['niche'], target['city'])

        print(f"\n[WAIT] Next swarm cycle in {CYCLE_DELAY}s...")
        await asyncio.sleep(CYCLE_DELAY)
        cycle += 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOPPED] Swarm shut down.")
