import redis
import os


class RedisClient:
    _instance = None  # برای پیاده‌سازی Singleton

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = os.getenv('REDIS_PORT', 6379)
        self.password = os.getenv('REDIS_PASSWORD', None)
        self.db = os.getenv('REDIS_DB', 0)

        self.client = redis.StrictRedis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            decode_responses=True
        )

    def set(self, key, value, ex=None):
        """ذخیره مقدار در Redis"""
        self.client.set(key, value, ex=ex)

    def get(self, key):
        """دریافت مقدار از Redis"""
        return self.client.get(key)

    def delete(self, key):
        """حذف مقدار از Redis"""
        self.client.delete(key)

    def exists(self, key):
        """بررسی وجود کلید"""
        return self.client.exists(key)

    def set_with_ttl(self, key, value, ttl):
        """ذخیره مقدار با TTL"""
        self.client.setex(key, ttl, value)

    def ttl(self, key):
        """دریافت TTL کلید"""
        return self.client.ttl(key)
    
    def flush(self):
        """پاک کردن تمام مقادیر Redis (با احتیاط استفاده شود)"""
        self.client.flushdb()


# تست ساده
if __name__ == "__main__":
    redis_client = RedisClient()
    redis_client.set('smtp_host', 'smtp.example.com', ex=3600)
    print(redis_client.get('smtp_host'))  # خروجی: smtp.example.com
