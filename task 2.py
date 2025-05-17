import time
from collections import defaultdict
import random

class ThrottlingRateLimiter:
    def __init__(self, min_interval=10.0):
        """
        :param min_interval: мінімальний інтервал між повідомленнями одного користувача (в секундах)
        """
        self.min_interval = min_interval
        self.user_last_message_time = defaultdict(lambda: 0.0)

    def record_message(self, user_id):
        """
        Повертає True, якщо повідомлення дозволено; False — якщо користувач ще не дочекався інтервалу.
        """
        current_time = time.time()
        last_time = self.user_last_message_time[user_id]

        if current_time - last_time >= self.min_interval:
            self.user_last_message_time[user_id] = current_time
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id):
        """
        Повертає час (у секундах), який залишився до дозволу наступного повідомлення.
        Якщо вже можна надсилати — повертає 0.0
        """
        current_time = time.time()
        last_time = self.user_last_message_time[user_id]
        elapsed = current_time - last_time
        remaining = self.min_interval - elapsed
        return max(0.0, remaining)


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()