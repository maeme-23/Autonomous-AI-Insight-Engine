import redis
import json
import logging
from typing import Optional, Dict, Any

class Cache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 3600):
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl  # Time-to-live in seconds
        self.client = None

    def initialize(self):
        """Initialize the Redis client"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            # Test the connection
            self.client.ping()
            logging.info("Redis cache initialized successfully")
        except Exception as e:
            logging.error(f"Redis initialization failed: {str(e)}")
            self.client = None

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Get a cached response for the query"""
        if not self.client:
            return None
            
        try:
            cached = self.client.get(query)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logging.error(f"Cache get failed: {str(e)}")
            return None

    def set(self, query: str, response: Dict[str, Any]):
        """Cache a response for the query"""
        if not self.client:
            return
            
        try:
            self.client.setex(query, self.ttl, json.dumps(response))
            logging.info(f"Cached response for query: {query}")
        except Exception as e:
            logging.error(f"Cache set failed: {str(e)}")

    def cleanup(self):
        """Close the Redis connection"""
        if self.client:
            self.client.close()
            self.client = None
            logging.info("Redis connection closed")