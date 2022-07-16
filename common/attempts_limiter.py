from django.core.cache import cache


class ExceededAttemptsLimit(Exception):
    pass


class AttemptsLimiter:
    def __init__(self, key, max_attempts, period, ban_period=None):
        self.key = key
        self.max_attempts = max_attempts
        self.period = period
        self.ban_period = ban_period or period

    @property
    def _attempt_key(self):
        return f'attempt:{self.key}'

    @property
    def _attempt_ban_key(self):
        return f'attempt_ban:{self.key}'

    def hold_attempt(self):
        if self.is_banned:
            raise ExceededAttemptsLimit
        attempts_count = self.attempts_count + 1
        cache.set(self._attempt_key, attempts_count, self.period)
        if attempts_count >= self.max_attempts:
            self.ban()
            cache.delete(self._attempt_key)
            raise ExceededAttemptsLimit

    @property
    def attempts_count(self):
        return cache.get(self._attempt_key, 0)

    def ban(self):
        cache.set(self._attempt_ban_key, 1, self.ban_period)

    @property
    def is_banned(self):
        return bool(cache.get(self._attempt_ban_key, False))
