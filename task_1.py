import time
from collections import defaultdict, deque
import random

class SlidingWindowRateLimiter:
    def __init__(self, window_size=10, max_requests=1):
        self.window_size = window_size  # у секундах
        self.max_requests = max_requests
        self.user_messages = defaultdict(deque)  # зберігає таймстемпи повідомлень по кожному користувачу

    def _cleanup_window(self, user_id):
        """Очистити застарілі повідомлення поза межами вікна."""
        current_time = time.time()
        window_start = current_time - self.window_size
        user_queue = self.user_messages[user_id]

        # Видалити всі повідомлення старші за початок вікна
        while user_queue and user_queue[0] < window_start:
            user_queue.popleft()

    def can_send_message(self, user_id):
        """Перевірити, чи може користувач надіслати повідомлення."""
        self._cleanup_window(user_id)
        return len(self.user_messages[user_id]) < self.max_requests

    def record_message(self, user_id):
        """Спроба записати повідомлення. Повертає True, якщо дозволено."""
        current_time = time.time()
        window_start = current_time - self.window_size

        # Очистити старі повідомлення поза межами вікна
        messages = self.user_messages[user_id]
        while messages and messages[0] < window_start:
            messages.popleft()

        if len(messages) < self.max_requests:
            messages.append(current_time)
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id):
        """Скільки часу залишилось до наступного дозволеного повідомлення."""
        self._cleanup_window(user_id)
        if len(self.user_messages[user_id]) < self.max_requests:
            return 0
        # Обчислити час до виходу першого повідомлення з вікна
        first_message_time = self.user_messages[user_id][0]
        return max(0, self.window_size - (time.time() - first_message_time))



# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()