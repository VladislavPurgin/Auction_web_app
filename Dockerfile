FROM python:3.13-slim

WORKDIR /app

# Встановлюємо залежності для psycopg2 та асинхронності
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]