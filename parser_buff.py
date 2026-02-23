import asyncio
import aiohttp
import sqlite3
from datetime import datetime
import config

DB_NAME = "market_data.db"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://buff.163.com/',
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buff_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goods_id TEXT NOT NULL,
            item_name TEXT,
            price_cny REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(goods_id, name, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO buff_prices (goods_id, item_name, price_cny) VALUES (?, ?, ?)", (goods_id, name, price))
    conn.commit()
    conn.close()

async def fetch_buff(session, goods_id, semaphore):
    async with semaphore:
        url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={goods_id}&page_num=1"
        try:
            async with session.get(url, headers=HEADERS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['code'] == 'OK':
                        items = data['data']['items']
                        info = data['data']['goods_infos'][goods_id]
                        if items:
                            price = float(items[0]['price'])
                            name = info.get('name', 'Unknown')
                            return name, price
                else:
                    print(f"Warning! Status {resp.status} for ID {goods_id}")
        except Exception as e:
            print(f"Error: {e}")
        return None, None

async def worker():
    init_db()
    sem = asyncio.Semaphore(config.BUFF_CONCURRENT)

    async with aiohttp.ClientSession() as session:
        print("🚀 Buff Parser started...")
        while True:
            tasks = [fetch_buff(session, gid, sem) for gid in config.BUFF_GOODS_IDS]
            results = await asyncio.gather(*tasks)

            for gid, res in zip(config.BUFF_GOODS_IDS, results):
                name, price = res
                if price:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] BUFF: {name} - ¥{price}")
                    save_to_db(gid, name, price)

            print("Buff cycle done. Sleeping...")
            await asyncio.sleep(config.BUFF_DELAY * 10)

if __name__ == "__main__":
    asyncio.run(worker())
