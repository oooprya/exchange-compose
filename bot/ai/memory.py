from collections import defaultdict

class Memory:

    def __init__(self):
        self.sessions = defaultdict(list)

    def add(self, chat_id, role, text):

        self.sessions[chat_id].append({
            "role": role,
            "content": text
        })

        # Храним последние 20 сообщений
        self.sessions[chat_id] = self.sessions[chat_id][-20:]

    def get(self, chat_id):
        return self.sessions[chat_id]

    def clear(self, chat_id):
        self.sessions.pop(chat_id, None)


memory = Memory()