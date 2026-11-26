FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

ENV DB_PATH=/data/inventory.db
EXPOSE 5000

# chown must run before VOLUME, otherwise the ownership change is discarded
RUN useradd -r app && mkdir -p /data && chown app /data
VOLUME /data
USER app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
