import os
import asyncio
from typing import AsyncIterator

try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None


class MemoryBroker:
    def __init__(self):
        self.channels = {}

    async def publish(self, channel: str, message: str):
        q = self.channels.get(channel)
        if q:
            await q.put(message)

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        q = asyncio.Queue()
        self.channels.setdefault(channel, q)
        try:
            while True:
                # wait with timeout to avoid blocking forever
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=1.0)
                    yield msg
                except asyncio.TimeoutError:
                    # no message; yield control back to caller loop
                    await asyncio.sleep(0)
                    continue
        finally:
            # best-effort cleanup
            pass

    async def get_message(self, channel: str, timeout: float = 1.0):
        q = self.channels.setdefault(channel, asyncio.Queue())
        try:
            msg = await asyncio.wait_for(q.get(), timeout=timeout)
            return msg
        except asyncio.TimeoutError:
            return None


class RedisBroker:
    def __init__(self, url: str):
        self._url = url
        self._client = aioredis.from_url(url)

    async def publish(self, channel: str, message: str):
        try:
            await self._client.publish(channel, message)
        except Exception:
            pass

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        try:
            pubsub = self._client.pubsub()
            await pubsub.subscribe(channel)
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg and msg.get('type') == 'message':
                    data = msg.get('data')
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    yield data
                else:
                    await asyncio.sleep(0.1)
        except Exception:
            # fallback: nothing
            return

    async def get_message(self, channel: str, timeout: float = 1.0):
        try:
            pubsub = self._client.pubsub()
            await pubsub.subscribe(channel)
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=timeout)
            if msg and msg.get('type') == 'message':
                data = msg.get('data')
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return data
            return None
        except Exception:
            return None


_broker = None

def get_broker():
    global _broker
    if _broker is not None:
        return _broker
    redis_url = os.getenv('REDIS_URL')
    if redis_url and aioredis is not None:
        try:
            _broker = RedisBroker(redis_url)
            return _broker
        except Exception:
            pass
    _broker = MemoryBroker()
    return _broker
