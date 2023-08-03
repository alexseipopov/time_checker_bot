FROM python:3.8

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости проекта
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта в контейнер
COPY . .

# Задаем точку монтирования для Docker volume
VOLUME /app/data

# Запускаем бота
CMD ["python", "bot.py"]

