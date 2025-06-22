from flask import Flask, Response
import redis
import psycopg2
import os
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Initialize Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNTER = Counter('app_requests_total', 'Total number of requests')

# Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.StrictRedis(host=redis_host, port=6379, decode_responses=True)

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )

@app.route("/")
def home():
    REQUEST_COUNTER.inc()
    redis_client.incr("hits")
    hits = redis_client.get("hits")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW()")
        now = cur.fetchone()[0]
        cur.close()
        conn.close()
    except Exception as e:
        now = f"DB Error: {e}"

    return f"Hello from Flask!<br>Redis hits: {hits}<br>Postgres time: {now}"

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

