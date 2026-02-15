class MessageQueue:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.message_queue = {} # Dict[int, Dict[int, List[int]]] 
        return cls._instance

    def add_message(self, chat_id: int, user_id: int, message_id: int):
        """Добавление сообщения в очередь."""
        self.message_queue.setdefault(chat_id, {}).setdefault(user_id, []).append(message_id)

    
    def remove_message(self, chat_id: int, user_id: int, message_id: int):
        """Удаление сообщения из очереди."""
        if chat_id in self.message_queue and user_id in self.message_queue[chat_id]:
            if message_id in self.message_queue[chat_id][user_id]:
                self.message_queue[chat_id][user_id].remove(message_id)
    
    
    def get_next_message(self, chat_id: int, user_id: int) -> int:
        """Получить следующее сообщение в очереди."""
        if chat_id in self.message_queue and user_id in self.message_queue[chat_id]:
            messages = self.message_queue[chat_id][user_id]
            if messages:
                return messages[0]
        return None

    def remove_next_message(self, chat_id: int, user_id: int):
        """Удаление следующего сообщения из очереди."""
        if chat_id in self.message_queue and user_id in self.message_queue[chat_id]:
            messages = self.message_queue[chat_id][user_id]
            if messages: messages.pop(0)

    def clear_queue(self, chat_id: int, user_id: int):
        """Очистка очереди для конкретного пользователя в чате."""
        if chat_id in self.message_queue and user_id in self.message_queue[chat_id]:
            self.message_queue[chat_id][user_id] = []
    
    def is_queue_empty(self, chat_id: int, user_id: int) -> bool:
        """Проверка, пуста ли очередь для пользователя."""
        return not self.message_queue.get(chat_id, {}).get(user_id, [])

    def get_all_queues(self):
        """Возвращает всю очередь сообщений."""
        return self.message_queue
