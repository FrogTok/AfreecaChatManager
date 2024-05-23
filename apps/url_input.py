import tkinter as tk
from chat.requests import get_bno
from apps.main_chat import ChatApp
from tkinter import messagebox


class BIDInputApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ID 입력")

        self.label = tk.Label(self, text="BJ의 ID를 입력하세요:")
        self.label.pack(pady=10)

        self.bid_entry = tk.Entry(self, width=40)
        self.bid_entry.pack(pady=10)

        self.connect_button = tk.Button(self, text="접속", command=self.check_broadcast)
        self.connect_button.pack(pady=10)

    def check_broadcast(self):
        bid = self.bid_entry.get()
        # 여기서 bid, bno의 유효성을 검사합니다.
        # 현재 방송중이 아니거나 유효하지 않은 bid면 오류데수
        if bid:
            bno = get_bno(bid)
            if bno:
                self.destroy()  # bid 입력 창 닫기
                self.start_chat_loop(bid, bno)
            else:
                messagebox.showerror("오류", "bj가 방송중이지 않거나 유효하지 않은 id입니다.")
        else:
            messagebox.showerror("오류", "bj의 id를 입력해주세요.")

    def start_chat_loop(self, bid, bno):
        chat_app = ChatApp(bid, bno)
        chat_app.mainloop()
