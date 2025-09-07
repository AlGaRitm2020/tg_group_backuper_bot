import random

import aiohttp

API_URL = "http://shortiki.com/export/api.php"


async def get_random_top_shortik() -> str:
    params = {"format": "json", "type": "top", "amount": 100}
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=params, timeout=5) as resp:
            data = await resp.json()
            if isinstance(data, list) and data:
                joke = random.choice(data).get("content", "😔 Шутка не найдена")
                return joke
            return "😔 Не удалось получить шутку"
