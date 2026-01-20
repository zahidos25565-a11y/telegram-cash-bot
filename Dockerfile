# 1. Базовый образ с Python 3.12
FROM python:3.12-slim

# 2. Рабочая папка внутри контейнера
WORKDIR /app

# 3. Копируем все файлы проекта в контейнер
COPY . .

# 4. Обновляем pip и устанавливаем зависимости
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. Команда запуска бота
CMD ["python", "bot.py"]
