from flask import Flask, render_template
from models import get_db_connection
import redis
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Redis connection
cache = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True
)

@app.route("/")
def home():
    # Check cache first
    cached_data = cache.get("users")

    if cached_data:
        return f"From Cache 🚀: {cached_data}"

    # Fetch from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, bio FROM users")
    users = cursor.fetchall()

    result = str(users)

    # Store in Redis
    cache.set("users", result, ex=60)

    cursor.close()
    conn.close()

    return render_template("index.html", users=users)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
