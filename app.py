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
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

@app.route("/")
def home():
    try:
        # Check cache
        cached_data = cache.get("users")
        if cached_data:
            return f"From Cache 🚀: {cached_data}"

        # DB fetch
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

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
