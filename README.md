# 💰 Expense Bot — Telegram-ассистент для учёта расходов

Персональный бот для учёта расходов и списка покупок.  
Распознаёт фото чеков через GPT-4o Vision, понимает текстовые сообщения и сохраняет всё в Notion.

---

## ⚡ Быстрый старт

### 1. Клонируй проект и создай окружение

```bash
git clone <repo>
cd expense-bot

python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Создай .env файл

```bash
cp .env.example .env
```

Открой `.env` и заполни токены (см. шаги ниже).

---

## 🔑 Получение токенов

### Telegram Bot Token
1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`
3. Придумай имя и username боту
4. Скопируй токен → `TELEGRAM_BOT_TOKEN`

### Свой Telegram User ID
1. Напиши [@userinfobot](https://t.me/userinfobot)
2. Скопируй свой `id` → `TELEGRAM_ALLOWED_USER_ID`

> Это защита — бот будет отвечать только тебе.

### OpenAI API Key
1. Зайди на [platform.openai.com](https://platform.openai.com)
2. API Keys → Create new secret key
3. Скопируй → `OPENAI_API_KEY`

> Используется модель `gpt-4o`. Убедись, что на аккаунте есть баланс.

### Notion Token
1. Перейди на [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Нажми **+ New integration**
3. Название: `Expense Bot`, тип: Internal
4. Скопируй **Internal Integration Secret** → `NOTION_TOKEN`

### Notion Parent Page ID
1. Открой Notion в браузере
2. Создай новую страницу (например, "Expense Bot")
3. Скопируй ID из URL:
   ```
   https://notion.so/ИмяРабочего/Expense-Bot-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
   ID — это последние 32 символа до `?v=`
4. Вставь → `NOTION_PARENT_PAGE_ID`

---

## 🗄️ Настройка Notion (автоматически)

После заполнения `.env` запусти скрипт — он сам создаст обе базы данных:

```bash
python setup_notion.py
```

Вывод будет примерно такой:
```
🔌 Проверяю подключение к Notion...
✅ Подключение успешно!

📊 Создаю базу данных Expenses...
✅ Expenses создана! ID: abc123...

🛍 Создаю базу данных Shopping List...
✅ Shopping List создана! ID: def456...

============================================================
✅ Базы данных успешно созданы!
============================================================

Добавь эти строки в свой .env файл:

NOTION_EXPENSES_DB_ID=abc123...
NOTION_SHOPPING_DB_ID=def456...
```

Скопируй ID в `.env`.

> ⚠️ Не забудь открыть созданные базы в Notion и подключить интеграцию:
> Открой базу → `...` (три точки) → **Connections** → найди `Expense Bot` → **Confirm**

---

## 🚀 Запуск бота

```bash
python -m bot.main
```

Бот запущен, если видишь:
```
🤖 Bot started. Polling...
```

---

## 🐳 Запуск через Docker

```bash
# Скопируй .env и заполни
cp .env.example .env

# Запусти
docker-compose up -d

# Логи
docker-compose logs -f
```

---

## 💬 Как пользоваться ботом

### Записать расход текстом
```
Купила продукты на 450 грн
Заплатила за бензин 800 грн
Потратила 120 грн на кофе с подругой
Купила корм Томе за 350 грн
```

### Записать расход фото
Просто отправь фото чека — бот сам распознает сумму, товары и категорию.

### Добавить в список покупок
```
Закончилась туалетная бумага
Нужно купить яйца
Купить шампунь
Закончился корм для кошки
```

### Команды
| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и справка |
| `/shopping` | Показать список покупок |
| `/clear_shopping` | Очистить список покупок |
| `/month` | Расходы за текущий месяц |
| `/week` | Расходы за последние 7 дней |

---

## 📁 Структура проекта

```
expense-bot/
├── bot/
│   ├── handlers/
│   │   ├── commands.py      # /start, /shopping, /month, /week
│   │   ├── photo.py         # Обработка фото чеков
│   │   └── text.py          # Обработка текстовых сообщений
│   ├── middlewares/
│   │   └── auth.py          # Защита — только авторизованный пользователь
│   └── main.py              # Точка входа
├── services/
│   ├── ai.py                # OpenAI GPT-4o — анализ текста и чеков
│   ├── notion.py            # Все операции с Notion API
│   └── formatter.py         # Форматирование ответов бота
├── config/
│   └── settings.py          # Переменные окружения
├── setup_notion.py          # Авто-создание баз в Notion
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🏷️ Категории расходов

| Категория | Эмодзи | Примеры |
|-----------|--------|---------|
| Продукты | 🛒 | супермаркет, рынок |
| Курение | 🚬 | сигареты, вейп |
| Животные | 🐾 | корм, ветеринар |
| Одежда | 👗 | магазины одежды |
| Посиделки | ☕ | кафе, рестораны, кофе |
| Автомобиль | 🚗 | бензин, мойка, ремонт |
| Дом | 🏠 | хозтовары, ремонт |
| Другое | 📦 | всё остальное |

---

## ❓ Частые вопросы

**Бот не отвечает на сообщения**  
Проверь `TELEGRAM_ALLOWED_USER_ID` — должен совпадать с твоим реальным user_id.

**Ошибка при сохранении в Notion**  
Убедись, что интеграция подключена к обеим базам данных (шаг Connections).

**Бот не распознаёт сумму на чеке**  
Убедись, что фото чёткое и освещение хорошее. Можно написать сумму вручную.
