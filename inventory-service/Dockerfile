FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

ENV DB_PATH=/data/inventory.db
VOLUME /data
EXPOSE 5000

RUN useradd -r app && mkdir -p /data && chown app /data
USER app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
