import threading

# thread safe classe to store a conversationId in memory
class ConversationIdStorage:
    def __init__(self):
        self.conversation_ids = set()
        self.lock = threading.Lock()

    def add(self, conversation_id):
        with self.lock:
            self.conversation_ids.add(conversation_id)

    def remove(self, conversation_id):
        with self.lock:
            self.conversation_ids.remove(conversation_id)

    def get_all(self):
        with self.lock:
            return list(self.conversation_ids)

    def has(self, conversation_id):
        with self.lock:
            return conversation_id in self.conversation_ids