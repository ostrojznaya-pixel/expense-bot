# Настройка Notion

## 1. Создать интеграцию

1. Перейди на https://www.notion.so/my-integrations
2. Нажми **+ New integration**
3. Дай название: `Expense Bot`
4. Скопируй **Internal Integration Secret** → это твой `NOTION_TOKEN`

---

## 2. Создать базу данных "Expenses"

Создай новую страницу в Notion → тип **Database → Full page**.
Назови её `Expenses`.

### Поля базы:

| Название поля | Тип        | Примечание                          |
|---------------|------------|-------------------------------------|
| `Title`       | Title      | (создан по умолчанию)               |
| `Amount`      | Number     | Формат: Number                      |
| `Category`    | Select     | Варианты ниже ↓                     |
| `Date`        | Date       |                                     |
| `Source`      | Select     | Варианты: `photo`, `text`           |
| `Raw Text`    | Text       |                                     |
| `Items`       | Text       |                                     |

### Варианты для Category:
- Продукты
- Курение
- Животные
- Одежда
- Посиделки
- Автомобиль
- Дом
- Другое

---

## 3. Создать базу данных "Shopping List"

Создай новую страницу → тип **Database → Full page**.
Назови её `Shopping List`.

### Поля базы:

| Название поля    | Тип      |
|------------------|----------|
| `Item`           | Title    |
| `Added At`       | Date     |
| `Status`         | Checkbox |
| `Source Message` | Text     |

---

## 4. Подключить интеграцию к базам

Для каждой базы данных:
1. Открой базу в Notion
2. Нажми `...` (три точки) в правом верхнем углу
3. → **Connections** → найди свою интеграцию `Expense Bot` → **Confirm**

---

## 5. Получить ID баз данных

Открой базу данных в браузере.
URL выглядит так:
```
https://www.notion.so/YOUR_WORKSPACE/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...
```

Скопируй 32-символьный ID (между последним `/` и `?`).

- ID базы Expenses → `NOTION_EXPENSES_DB_ID`
- ID базы Shopping List → `NOTION_SHOPPING_DB_ID`
