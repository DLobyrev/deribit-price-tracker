"""
Клиент для получения index price с биржи Deribit.
Использует публичный API, не требует авторизации.
"""

import requests
import time
from typing import Optional, Dict

# Базовый URL Deribit API
DERIBIT_API_URL = "https://www.deribit.com/api/v2/public/get_index_price"


def get_index_price(ticker: str) -> Optional[Dict[str, any]]:
    """
    Получает текущую справочную цену (index price) для указанного тикера.

    Args:
        ticker (str): Название индекса, например 'btc_usd' или 'eth_usd'.

    Returns:
        dict или None: Словарь вида:
            {
                "ticker": "btc_usd",
                "price": 92741.52,
                "timestamp": 1737284567
            }
        или None, если запрос не удался.
    """
    try:
        # Делаем GET-запрос к Deribit
        response = requests.get(
            DERIBIT_API_URL,
            params={"index_name": ticker},
            timeout=10  # Защита от зависания
        )
        response.raise_for_status()  # Вызовет исключение при HTTP ошибке

        data = response.json()

        # Проверяем, есть ли ожидаемые данные
        if "result" not in data or "index_price" not in data["result"]:
            print(f"Неожиданный формат ответа для {ticker}: {data}")
            return None

        price = data["result"]["index_price"]

        # Время сохраняем как UNIX timestamp в секундах (локальное время)
        # Почему локальное? Потому что Deribit в этом эндпоинте не всегда отдаёт timestamp.
        # А нам нужно фиксировать момент сохранения данных.
        timestamp = int(time.time())

        return {
            "ticker": ticker,
            "price": price,
            "timestamp": timestamp
        }

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при запросе {ticker}: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при обработке {ticker}: {e}")
        return None


# === Для тестирования модуля отдельно ===
if __name__ == "__main__":
    # Пример использования
    for ticker in ["btc_usd", "eth_usd"]:
        result = get_index_price(ticker)
        if result:
            print(f"{ticker}: {result['price']} USD @ {result['timestamp']}")
        else:
            print(f"Не удалось получить {ticker}")