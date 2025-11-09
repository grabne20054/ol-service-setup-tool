import redis

class RedisCacheConnector:
    def __init__(self, host, port=6379):
        try:
            self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
            self.redis_client.ping()
            print(f"Successfully connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis at {host}:{port}: {e}")
            self.redis_client = None

    def set(self, key, value, ttl=60*3):
        if self.redis_client:
            self.redis_client.set(key, value, ex=ttl)
        else:
            raise Exception("Redis client is not connected")

    def get(self, key):
        if self.redis_client:
            return self.redis_client.get(key)
        else:
            raise Exception("Redis client is not connected")

    def close(self):
        self.redis_client.close()

    def get_client(self):
        if self.redis_client:
            return self.redis_client
        else:
            raise Exception("Redis client is not connected")
    
    