import asyncio
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QScrollArea, QWidget, QLabel
from PySide6.QtCore import Qt, QTimer
from chat.queue import ChatQueue
from chat.message import MessageLoop
from chat.requests import get_bno
import sys


class ChatApp(QMainWindow):
    def __init__(self, bid, bno):
        super().__init__()
        self.chat_queue = ChatQueue()

        self.setWindowTitle("Chat Application")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.chat_frame = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_frame.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_frame)

        self.max_messages = 1000000

        self.message_loop = MessageLoop(bid=bid, bno=bno)
        self.message_loop.start()

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_asyncio, args=(self.loop,))
        self.thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chat)
        self.timer.start(1000)

        self.chat_frame.layout().setSizeConstraint(QVBoxLayout.SetMinimumSize)

    def run_asyncio(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_messages())

    async def fetch_messages(self):
        while not self.message_loop.stop_event.is_set():
            await asyncio.sleep(1)

    def update_chat(self):
        line_list = []
        for _ in range(200):
            chat = self.chat_queue.dequeue_message()
            if chat is None:
                break
            label = QLabel(chat)
            label.setWordWrap(True)
            label.setStyleSheet("background-color: lightgrey; padding: 5px;")
            line_list.append(label)

        if line_list:
            self.add_chat_messages(line_list)

    def add_chat_messages(self, line_list):
        if self.chat_frame:
            for line in line_list:
                self.chat_layout.addWidget(line)

            # 레이아웃 강제 업데이트
            self.chat_layout.update()
            self.scroll_area.update()
            self.chat_frame.update()

            # 이벤트 루프 업데이트
            QApplication.processEvents()

            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

            while self.chat_layout.count() > self.max_messages:
                item = self.chat_layout.itemAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                self.chat_layout.removeItem(item)

    def closeEvent(self, event):
        self.message_loop.stop()
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
# import asyncio
# import threading
# import tkinter as tk
# from chat.queue import ChatQueue
# from chat.message import MessageLoop


# class ChatApp(tk.Tk):
#     def __init__(self, bid, bno):
#         super().__init__()
#         self.chat_queue = ChatQueue()

#         self.title("Chat Application")

#         self.canvas = tk.Canvas(self, bg="white", width=400, height=300)
#         self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
#         self.canvas.configure(yscrollcommand=self.scrollbar.set)

#         self.chat_frame = tk.Frame(self.canvas)
#         self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
#         self.max_messages = 100

#         self.scrollbar.pack(side="right", fill="y")
#         self.canvas.pack(side="left", fill="both", expand=True)

#         self.chat_frame.bind("<Configure>", self.on_frame_configure)

#         self.message_loop = MessageLoop(bid=bid, bno=bno)
#         self.message_loop.start()

#         self.protocol("WM_DELETE_WINDOW", self.on_close)

#         # Start the asyncio event loop in a separate thread
#         self.loop = asyncio.new_event_loop()
#         self.thread = threading.Thread(target=self.run_asyncio, args=(self.loop,))
#         self.thread.start()

#     def run_asyncio(self, loop):
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(self.fetch_messages())

#     async def fetch_messages(self):
#         while not self.message_loop.stop_event.is_set():
#             await self.update_chat()
#             await asyncio.sleep(1)

#     async def update_chat(self):
#         line_list = []
#         for _ in range(200):
#             chat = self.chat_queue.dequeue_message()
#             if chat is None:
#                 break
#             line_list.append(
#                 tk.Label(self.chat_frame, anchor="w", justify="left", text=chat, bg="lightgrey", wraplength=380)
#             )

#         if line_list:
#             self.after(0, self.draw_chat_message, line_list)

#     def draw_chat_message(self, line_list):
#         if self.chat_frame.winfo_exists():
#             for line in line_list:
#                 line.pack(padx=10, pady=5, fill="x")
#             # self.canvas.configure(scrollregion=self.canvas.bbox("all"))
#             self.canvas.after_idle(self.canvas.yview_moveto, (1.0,))

#             # Check if we need to remove the oldest message
#             while len(self.chat_frame.winfo_children()) > self.max_messages:
#                 self.remove_oldest_message()

#     def remove_oldest_message(self):
#         if self.chat_frame.winfo_exists():
#             oldest_message = self.chat_frame.winfo_children()[0]
#             oldest_message.destroy()

#     def on_frame_configure(self, event=None):
#         self.canvas.configure(scrollregion=self.canvas.bbox("all"))

#     def on_close(self):
#         self.message_loop.stop()
#         self.loop.call_soon_threadsafe(self.loop.stop)
#         self.thread.join()
#         self.destroy()
