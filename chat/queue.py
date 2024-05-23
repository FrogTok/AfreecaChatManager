import queue


class ChatQueue:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChatQueue, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.queue = queue.Queue()

    def enqueue_message(self, message):
        """채팅 메세지 큐에 추가"""
        self.queue.put(message)

    def dequeue_message(self):
        """채팅 메세지 큐에서 꺼내기"""
        try:
            return self.queue.get(block=False)
        except queue.Empty:
            return None


class MemberChatQueue:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MemberChatQueue, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.members = {}

    def add_member(self, member_id):
        """새 멤버를 추가합니다. 각 멤버는 자신의 메시지 큐를 가집니다."""
        if member_id not in self.members:
            self.members[member_id] = queue.Queue()

    def remove_member(self, member_id):
        """멤버를 제거하고 해당 멤버의 채팅 기록도 삭제합니다."""
        if member_id in self.members:
            del self.members[member_id]

    def enqueue_message(self, member_id, message):
        """특정 멤버의 메시지 큐에 메시지를 추가합니다."""
        if member_id in self.members:
            self.members[member_id].put(message)
        else:
            print("멤버가 존재하지 않습니다.")

    def dequeue_message(self, member_id):
        """특정 멤버의 메시지 큐에서 메시지를 제거하고 반환합니다."""
        try:
            if member_id in self.members and self.members[member_id]:
                return self.members[member_id].get()
            return None
        except queue.Empty:
            return None

    def get_member_messages(self, member_id):
        """특정 멤버의 모든 메시지를 리스트로 반환합니다."""
        if member_id in self.members:
            return list(self.members[member_id])
        return []

    def is_empty(self, member_id):
        """특정 멤버의 메시지 큐가 비어있는지 확인합니다."""
        return not self.members.get(member_id, None)
