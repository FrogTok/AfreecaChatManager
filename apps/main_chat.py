import asyncio
import os
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QScrollArea, QWidget, QLabel, QListView
from PySide6.QtCore import Qt, QTimer, QMetaObject, Slot, QStringListModel
from PySide6.QtGui import QIcon, QPixmap
from requests import HTTPError
from chat.queue import ChatQueue
from chat.message import MessageThread
from chat.requests import download_image, get_bno
import sys

from utils import get_root_directory_path


class ChatApp(QMainWindow):
    def __init__(self, bid, bno):
        super().__init__()
        self.chat_queue = ChatQueue()

        self.setWindowTitle("아프리카 채팅매니저")
        self.resize(600, 400)
        try:
            image_data = download_image(f"https://profile.img.afreecatv.com/LOGO/{bid[:2]}/{bid}/{bid}.jpg")
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.setWindowIcon(QIcon(pixmap))
        except HTTPError:
            icon_path = os.path.join(get_root_directory_path(), "assets/afreeca.ico")
            self.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.chat_view = QListView()
        self.chat_model = QStringListModel()
        self.chat_view.setModel(self.chat_model)
        self.layout.addWidget(self.chat_view)

        self.max_messages = 10000
        self.message_buffer = []

        self.message_thread = MessageThread(bid=bid, bno=bno)
        self.message_thread.start()

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_asyncio, args=(self.loop,))
        self.thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chat)
        self.timer.start(100)  # 100ms마다 업데이트

    def run_asyncio(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_messages())

    async def fetch_messages(self):
        while not self.message_thread.stop_event.is_set():
            try:
                await asyncio.sleep(1)
            except Exception as e:
                print(f"  ERROR: fetch_messages() error - {e}")
                break

    def update_chat(self):
        for _ in range(200):  # 최대 200개의 메시지를 한 번에 처리
            chat = self.chat_queue.dequeue_message()
            if chat is None:
                break
            self.message_buffer.append(chat)

        if self.message_buffer:
            self.add_chat_messages(self.message_buffer)
            self.message_buffer = []

    def add_chat_messages(self, messages):
        if messages:
            current_messages = self.chat_model.stringList()
            current_messages.extend(messages)

            if len(current_messages) > self.max_messages:
                current_messages = current_messages[-self.max_messages:]

            self.chat_model.setStringList(current_messages)
            QMetaObject.invokeMethod(self, "update_layout", Qt.QueuedConnection)

    @Slot()
    def update_layout(self):
        self.chat_view.scrollToBottom()  # 스크롤을 제일 아래로 내림
        self.chat_view.update()

    def closeEvent(self, event):
        self.message_thread.stop()
        self.message_thread.join()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        event.accept()


if __name__ == "__main__":
    bid = "243000"
    bno = get_bno(bid)
    app = QApplication(sys.argv)
    window = ChatApp(bid, bno)
    window.show()
    sys.exit(app.exec())