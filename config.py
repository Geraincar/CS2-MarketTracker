# === НАСТРОЙКИ ПАРСЕРА STEAM ===
STEAM_ITEMS = [
    "AK-47 | Redline (Field-Tested)",
    "AWP | Dragon Lore (Factory New)",
    "M4A4 | Howl (Minimal Wear)",
    # Добавьте свои предметы для Steam
]

STEAM_DELAY = 5  # Задержка между запросами в секундах (Не меньше 3-4)

# === НАСТРОЙКИ ПАРСЕРА BUFF163 ===
# ID можно найти в URL товара: buff.163.com/goods/34207.html -> ID: 34207
BUFF_GOODS_IDS = [
    "34207",  # AK-47 | Redline (FT)
    "128832", # AWP | Dragon Lore (FN)
    "35006",  # M4A4 | Howl (MW)
    # Добавьте ID товаров
]

BUFF_DELAY = 1.0          # Задержка между "пачками" запросов
BUFF_CONCURRENT = 5       # Количество одновременных запросов (не ставьте много!)
CURRENCY_RATE = 7.3       # Курс CNY к USD для примерного расчета в дашборде
