# Local Bot API Server

Краткое руководство по использованию **локального Bot API сервера** Telegram в проекте.

## Зачем это нужно

Официальный `api.telegram.org` ограничивает:
- **загрузку файлов ботом** — до **20 МБ**;
- загрузку (upload) — до 50 МБ и т.д.

Локальный Bot API сервер (режим `--local`) даёт:
- **загрузку файлов без лимита по размеру**;
- загрузку (upload) до **2000 МБ**;
- использование локальных путей к файлам после `getFile` (без повторной загрузки);
- webhook на HTTP, любой порт, любой IP;
- до 100 000 соединений для webhook.

Подробнее: [Using a Local Bot API Server](https://core.telegram.org/bots/api#using-a-local-bot-api-server).

---

## 1. Получить API ID и API Hash

1. Зайти на https://my.telegram.org
2. Войти по номеру телефона.
3. Перейти в **API development tools**.
4. Создать приложение (если ещё нет) и скопировать **api_id** и **api_hash**.

Инструкция: https://core.telegram.org/api/obtaining_api_id

---

## 2. Запуск Local Bot API Server

### Вариант A: Docker (проще всего)

Используется неофициальный образ [aiogram/telegram-bot-api](https://github.com/aiogram/telegram-bot-api).

```bash
docker run -d \
  -p 8081:8081 \
  --name telegram-bot-api \
  --restart always \
  -v telegram-bot-api-data:/var/lib/telegram-bot-api \
  -e TELEGRAM_API_ID=ВАШ_API_ID \
  -e TELEGRAM_API_HASH=ВАШ_API_HASH \
  -e TELEGRAM_LOCAL=1 \
  aiogram/telegram-bot-api:latest
```

**Важно:** `TELEGRAM_LOCAL=1` включает локальный режим (снятие лимита на размер файлов и остальные фичи).

Проверка: `curl http://localhost:8081` — должен ответить сервер.

### Вариант B: Сборка из исходников

Репозиторий: https://github.com/tdlib/telegram-bot-api

Генератор инструкций по сборке под ОС: https://tdlib.github.io/telegram-bot-api/build.html

Кратко (Linux/macOS):

```bash
git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --target install
```

Запуск с локальным режимом:

```bash
telegram-bot-api --api-id=API_ID --api-hash=API_HASH --http-port=8081 --local
```

---

## 3. Подключение бота (aiogram) к локальному серверу

Бот должен слать запросы на свой сервер вместо `https://api.telegram.org`.

### Настройка в проекте

В `setting.py` добавьте (или раскомментируйте):

```python
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

# Локальный Bot API (опционально)
USE_LOCAL_BOT_API = os.getenv("USE_LOCAL_BOT_API", "false").lower() == "true"
LOCAL_BOT_API_BASE = os.getenv("LOCAL_BOT_API_BASE", "http://localhost:8081")
```

В `.env`:

```env
USE_LOCAL_BOT_API=true
LOCAL_BOT_API_BASE=http://localhost:8081
```

В `bot.py` создавайте Bot с сессией, указывающей на локальный сервер:

```python
from setting import TOKEN, USE_LOCAL_BOT_API, LOCAL_BOT_API_BASE

from aiogram import Bot
from aiogram.client.session import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

if USE_LOCAL_BOT_API:
    session = AiohttpSession(
        api=TelegramAPIServer.from_base(LOCAL_BOT_API_BASE)
    )
    bot = Bot(token=TOKEN, session=session)
else:
    bot = Bot(token=TOKEN)
```

После этого все вызовы Bot API (в том числе загрузка файлов в `file_service`) пойдут на ваш сервер, и лимит 20 МБ при загрузке файлов действовать не будет.

---

## 4. Переход с облачного API на локальный

Чтобы бот не терял обновления при переключении:

1. На старом (облачном) боте вызвать [logOut](https://core.telegram.org/bots/api#logout) (или удалить webhook через `deleteWebhook`, затем остановить бота).
2. Запустить локальный Bot API сервер.
3. Запустить бота с настройками выше (USE_LOCAL_BOT_API=true).

Рекомендуется сначала протестировать с polling на своей машине, затем уже настраивать webhook на прод.

---

## 5. Docker Compose (пример)

Рядом с проектом можно использовать:

```yaml
# docker-compose.bot-api.yml (опционально)
version: "3.8"

services:
  telegram-bot-api:
    image: aiogram/telegram-bot-api:latest
    environment:
      TELEGRAM_API_ID: ${TELEGRAM_API_ID}
      TELEGRAM_API_HASH: ${TELEGRAM_API_HASH}
      TELEGRAM_LOCAL: 1
    volumes:
      - telegram-bot-api-data:/var/lib/telegram-bot-api
    ports:
      - "8081:8081"
    restart: unless-stopped

volumes:
  telegram-bot-api-data:
```

Запуск: `TELEGRAM_API_ID=... TELEGRAM_API_HASH=... docker-compose -f docker-compose.bot-api.yml up -d`

---

## Итог

| Шаг | Действие |
|-----|----------|
| 1 | Получить api_id и api_hash на my.telegram.org |
| 2 | Запустить Local Bot API (Docker с `TELEGRAM_LOCAL=1` или бинарник с `--local`) |
| 3 | В проекте: USE_LOCAL_BOT_API=true, создать Bot с `AiohttpSession(api=TelegramAPIServer.from_base(...))` |
| 4 | При необходимости вызвать logOut на старом API и перезапустить бота |

После этого загрузка файлов в боте (в т.ч. в `download_file_BytesIo`) будет идти через локальный сервер без лимита в 20 МБ.
