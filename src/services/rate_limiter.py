class LoginRateLimiter:
    def __init__(self, redis):
        self.redis = redis
        self.max_attempts = 5
        self.block_seconds = 600

    @staticmethod
    def _fail_key(username: str) -> str:
        return f"failed_login:{username}"

    @staticmethod
    def _block_key(username: str) -> str:
        return f"blocked_user:{username}"

    async def is_blocked(self, username: str) -> bool:
        return await self.redis.exists(self._block_key(username))

    async def incr_attempts(self, username: str) -> int:
        key = self._fail_key(username)
        attempts = await self.redis.incr(key)
        if attempts == 1:
            await self.redis.expire(key, self.block_seconds)
        if attempts >= self.max_attempts:
            await self.redis.set(self._block_key(username), "1", ex=self.block_seconds)
            await self.redis.delete(key)
        return attempts

    async def reset_attempts(self, username: str):
        await self.redis.delete(self._fail_key(username))
