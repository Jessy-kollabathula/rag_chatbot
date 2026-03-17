import redis
import json

# -------------------------
# Redis Connection
# -------------------------
try:
    redis_client = redis.Redis(
        host="redis-18703.c92.us-east-1-3.ec2.cloud.redislabs.com",
        port=18703,
        username="default",
        password="adoDsO99RqFRT80vBMFWhVg1pMLEHbWl",
        decode_responses=True
    )

    redis_client.ping()
    print("Redis connected")

except Exception as e:
    print("Redis connection failed:", e)


# -------------------------
# Chat List Functions
# -------------------------
def save_chat_list(user_id, chats):
    redis_client.set(f"user:{user_id}:chats", json.dumps(chats))


def get_chat_list(user_id):
    data = redis_client.get(f"user:{user_id}:chats")
    if data:
        return json.loads(data)
    return []


# -------------------------
# Chat Messages
# -------------------------
def save_chat_messages(chat_id, messages):
    redis_client.set(f"chat:{chat_id}", json.dumps(messages))


def get_chat_messages(chat_id):
    data = redis_client.get(f"chat:{chat_id}")
    if data:
        return json.loads(data)
    return []