import asyncio
import aiohttp
import sqlite3
from datetime import datetime
import config

DB_NAME = "market_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS steam_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            price REAL,
            volume INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def fetch_price(session, item_name):
    url = f"https://steamcommunity.com/market/priceoverview/?currency=1&appid=730&market_hash_name={item_name}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    price_str = data.get('lowest_price', '0')
                    price = float(price_str.replace('$', '').replace(' USD', '').replace(',', ''))
                    volume = int(data.get('volume', '0').replace(',', ''))
                    return price, volume
            return None, None
    except Exception as e:
        print(f"Error fetching {item_name}: {e}")
        return None, None

def save_to_db(item_name, price, volume):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO steam_prices (item_name, price, volume) VALUES (?, ?, ?)", (item_name, price, volume))
    conn.commit()
    conn.close()

async def worker():
    init_db()
    async with aiohttp.ClientSession() as session:
        print("🚀 Steam Parser started...")
        while True:
            for item in config.STEAM_ITEMS:
                price, volume = await fetch_price(session, item)
                if price:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] STEAM: {item} - ${price}")
                    save_to_db(item, price, volume)
                await asyncio.sleep(config.STEAM_DELAY)
            print("Cycle done. Sleeping 60s...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(worker())
