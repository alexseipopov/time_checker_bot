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
Здесь /app/data - это путь, где будет производиться монтирование Docker volume в контейнере. Все данные, сохраненные в этой директории, будут сохранены в Docker volume my_data_volume.

Шаг 3: Запустите контейнер с монтированием Docker volume (при использовании Dockerfile)
Выполните следующую команду для запуска контейнера с монтированием Docker volume:

javascript
Copy code
docker run -d -v my_data_volume:/app/data my_telegram_bot
Здесь my_data_volume - это имя Docker volume, которое вы создали на первом шаге, и /app/data - это путь, куда будет производиться монтирование внутри контейнера. В результате файл БД SQLite (my_database.db) будет доступен в контейнере и все изменения, внесенные в базу данных, будут сохраняться в Docker volume my_data_volume.

Помните, что вы должны убедиться, что путь к вашему файлу БД верный и что файл имеет права на чтение и запись. Если вы используете docker-compose, то подход будет аналогичным, но вместо команды docker run, используйте файл docker-compose.yml.





