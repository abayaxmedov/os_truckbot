# 🚚 TruckBot — Telegram Mini App маркетплейс запчастей для грузовиков

Telegram **Mini App** (маркетплейс) + **Telegram Bot** (уведомления) для продажи запчастей для
грузовых автомобилей (MAN, Volvo, DAF, Scania, Mercedes-Benz, Renault Trucks, Iveco).

Реализовано по ТЗ (Приложение №1 к Договору № 2208) — см. [`docs/TZ.md`](docs/TZ.md).

---

## Возможности (по ТЗ)

| ТЗ | Реализация |
|----|------------|
| §1 Платформа | Telegram Mini App (React) + Telegram Bot (aiogram) для уведомлений |
| §2 Каталог | 7 марок, 18 категорий (ru/uz), админ управляет категориями |
| §3 Поиск | по артикулу, OEM-номеру, бренду, названию, марке/модели/двигателю + аналоги |
| §4 Карточка товара | фото, артикул, OEM, бренд, совместимость, цена, наличие, гарантия, продавец, рейтинг + «В корзину / Купить / Задать вопрос» |
| §5–6 Корзина, оформление | корзина, доставка, контактные данные |
| §7 Оплата | Click / Payme / Uzum — **архитектура-заглушки** (готовы к подключению) |
| §8 Кабинет покупателя | заказы, история, избранное, личные данные |
| §9–10 Кабинет продавца | товары CRUD, фото, остатки, **массовая загрузка Excel/CSV**, заказы, статусы, статистика |
| §11 Админ-панель | продавцы, модерация товаров, категории, комиссия, статистика, баннеры |
| §12 Комиссия | 5/7/10/15%+ глобально, по продавцу или категории |
| §13 Рейтинг продавцов | 1–5★, кол-во заказов/отзывов, % выполненных |
| §14 Уведомления | покупателю / продавцу / администратору через бота |
| §15 Аналоги | поиск по OEM-номеру, расширяемая база кросс-ссылок |
| §16 B2B | архитектурные точки расширения (см. ниже) |

---

## Архитектура

```
Telegram ──▶ Mini App (React/Vite)  ──HTTP──▶  FastAPI  ──▶  PostgreSQL
                                                  │
Telegram Bot (aiogram, в том же процессе) ◀───────┘  (уведомления)
```

- **backend/** — FastAPI (REST API) + aiogram (бот) в одном процессе, SQLAlchemy 2 (async), Alembic.
- **miniapp/** — React + Vite + TypeScript, i18next (ru/uz), zustand. Тема берётся из Telegram.
- Авторизация — валидация Telegram `initData` (HMAC) → JWT.

Полное дерево каталогов описано в плане и в `backend/app` / `miniapp/src`.

---

## Требования

- Docker (для PostgreSQL) **или** локальный PostgreSQL 15+
- Python 3.11+
- Node.js 20+
- Токен бота от [@BotFather](https://t.me/BotFather)

> На этой машине порты `5432` и `8000` заняты другими проектами, поэтому по умолчанию
> используются **PostgreSQL → 5433** и **backend → 8010**. Меняются в `.env` и `docker-compose.yml`.

---

## Быстрый старт

**Одной командой** (PostgreSQL + backend + Mini App):

```bash
./scripts/dev.sh              # запускает всё; ./scripts/stop.sh — остановить
```

> Docker в этом проекте — через **colima**. Если он остановлен: `colima start` (данные БД в томе сохраняются).

Открыть: `http://localhost:5173/?dev_tg=100000004` (покупатель) · `…=100000002` (продавец) · `…=100000001` (админ).

---

### Или вручную (по шагам)

```bash
cp .env.example .env          # заполните BOT_TOKEN и TELEGRAM_ADMIN_IDS
make db-up                    # поднять PostgreSQL в Docker
make backend-install          # venv + зависимости backend
make migrate                  # применить миграции
make seed                     # марки, 18 категорий, демо-данные
make dev                      # backend на http://localhost:8010  (Swagger: /docs)
```

В отдельном терминале — Mini App:

```bash
make miniapp-install
make miniapp-dev              # http://localhost:5173  (проксирует /api и /media на backend)
```

Либо всё в Docker: `make up` (поднимает PostgreSQL + backend, применяет миграции и сид автоматически).

---

## Подключение к Telegram

1. Создайте бота у [@BotFather](https://t.me/BotFather) → получите `BOT_TOKEN` → впишите в `.env`.
2. Узнайте свой числовой Telegram ID (например, у [@userinfobot](https://t.me/userinfobot)) →
   впишите в `TELEGRAM_ADMIN_IDS` (несколько — через запятую) → это даёт права администратора.
3. Mini App требует **HTTPS**. Для локальной разработки поднимите туннель:
   ```bash
   cloudflared tunnel --url http://localhost:5173     # или ngrok http 5173
   ```
   Полученный `https://…`-адрес укажите:
   - в `.env` → `MINIAPP_URL=https://…`
   - в BotFather → *Bot Settings → Menu Button / Web App URL*.
4. Перезапустите backend — бот стартует в режиме polling (`BOT_MODE=polling`).
   Для продакшена — `BOT_MODE=webhook` + публичный `PUBLIC_BASE_URL`.

### Вариант с ngrok (стабильный URL)

```bash
brew install ngrok
ngrok config add-authtoken <ВАШ_ТОКЕН>          # dashboard.ngrok.com
# (рекомендуется) создайте бесплатный статичный домен в дашборде → Domains
ngrok http 5173 --url=<ваш-домен>.ngrok-free.dev \
  --traffic-policy-file ngrok.policy.yml         # без --url — эфемерный адрес
```
Затем пропишите этот `https://…`-адрес в `.env` (`MINIAPP_URL`, `PUBLIC_BASE_URL`),
перезапустите backend и обновите кнопку меню бота (`setChatMenuButton`).

> ⚠️ На **бесплатном** тарифе ngrok при первом открытии показывает страницу-предупреждение
> («Visit Site» — один раз на сессию браузера). API/XHR обходят её заголовком
> `ngrok-skip-browser-warning` (уже добавлен во фронтенд), но верхнеуровневую навигацию из
> Telegram обойти нельзя. Полностью без предупреждения — платный ngrok, **cloudflared**
> (`cloudflared tunnel --url http://localhost:5173`, без интерстишела) или деплой на свой домен.

---

## Разработка без Telegram (dev-режим)

Пока `DEV_AUTH_BYPASS=true`, приложение можно открыть в обычном браузере, а роль выбрать через
параметр URL (демо-пользователи создаются сидом):

| URL | Роль |
|-----|------|
| `http://localhost:5173/?dev_tg=100000004` | Покупатель |
| `http://localhost:5173/?dev_tg=100000002` | Продавец |
| `http://localhost:5173/?dev_tg=100000001` | Администратор |

> ⚠️ В продакшене обязательно `DEV_AUTH_BYPASS=false`.

---

## Тесты

```bash
make test        # pytest: комиссия, разбиение заказа по продавцам, поиск аналогов, initData
```

---

## Оплата (Click / Payme / Uzum)

Реализован интерфейс `PaymentProviderBase` (`create_payment` / `handle_callback`) со
**заглушками**: заказ проходит весь цикл, оплата помечается `pending`, доступна демо-страница
`/api/v1/payments/{provider}/mock`. Для реальной интеграции нужно заполнить тела провайдеров
(`backend/app/services/payments/`) и добавить merchant-ключи в `.env`.

## B2B (§16) — точки расширения

Заложены без переработки ядра: роль/тип клиента на пользователе, снапшоты цен и комиссии в заказе,
конфигурируемая комиссия по продавцу/категории. Кабинет B2B добавляется как отдельный набор
эндпоинтов и экранов поверх существующих моделей.

---

## Переменные окружения

Все переменные описаны в [`.env.example`](.env.example). Ключевые: `BOT_TOKEN`,
`TELEGRAM_ADMIN_IDS`, `MINIAPP_URL`, `DATABASE_URL`, `JWT_SECRET`, `DEV_AUTH_BYPASS`,
`DEFAULT_COMMISSION_PERCENT`.

## Чек-лист передачи проекта

- [ ] Исходный код (этот репозиторий)
- [ ] `BOT_TOKEN` и доступы к боту
- [ ] Доступ к серверу и БД (дамп/строка подключения)
- [ ] Merchant-ключи Click/Payme/Uzum (для боевой оплаты)
- [ ] Домен + HTTPS-сертификат для Mini App
