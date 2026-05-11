from dotenv import load_dotenv
load_dotenv()
import os
import redis
connection = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)