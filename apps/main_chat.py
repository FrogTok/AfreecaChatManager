import asyncio
import threading
import tkinter as tk
from chat.queue import ChatQueue
from chat.message import MessageLoop


class ChatApp(tk.Tk):
    def __init__(self, bid, bno):
        super().__init__()
        self.chat_queue = ChatQueue()

        self.title("Chat Application")

        self.canvas = tk.Canvas(self, bg="white", width=400, height=300)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chat_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.max_messages = 1000

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.chat_frame.bind("<Configure>", self.on_frame_configure)

        self.message_loop = MessageLoop(bid=bid, bno=bno)
        self.message_loop.start()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start the asyncio event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_asyncio, args=(self.loop,))
        self.thread.start()

    def run_asyncio(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_messages())

    async def fetch_messages(self):
        while not self.message_loop.stop_event.is_set():
            await self.update_chat()
            await asyncio.sleep(1)

    async def update_chat(self):
        line_list = []
        for _ in range(200):
            chat = self.chat_queue.dequeue_message()
            if chat is None:
                break
            line_list.append(
                tk.Label(self.chat_frame, anchor="w", justify="left", text=chat, bg="lightgrey", wraplength=380)
            )

        if line_list:
            self.after(0, self.draw_chat_message, line_list)

    def draw_chat_message(self, line_list):
        if self.chat_frame.winfo_exists():
            for line in line_list:
                line.pack(padx=10, pady=5, fill="x")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.after_idle(self.canvas.yview_moveto, (1.0,))

            # Check if we need to remove the oldest message
            while len(self.chat_frame.winfo_children()) > self.max_messages:
                self.remove_oldest_message()

    def remove_oldest_message(self):
        if self.chat_frame.winfo_exists():
            oldest_message = self.chat_frame.winfo_children()[0]
            oldest_message.destroy()

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_close(self):
        self.message_loop.stop()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        self.destroy()
