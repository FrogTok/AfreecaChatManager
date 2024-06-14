from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from chat.requests import get_bno
from apps.main_chat import ChatApp
import sys

from dto import Bj


class BIDInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ID 입력")

        self.layout = QVBoxLayout()

        self.label = QLabel("BJ의 ID를 입력하세요:")
        self.layout.addWidget(self.label)

        self.bid_entry = QLineEdit()
        self.layout.addWidget(self.bid_entry)

        self.connect_button = QPushButton("접속")
        self.connect_button.clicked.connect(self.check_broadcast)
        self.layout.addWidget(self.connect_button)

        self.setLayout(self.layout)

    def check_broadcast(self):
        bid = self.bid_entry.text()
        if bid:
            bj = Bj(id=bid)
            bno = get_bno(bj.bid)
            if bno:
                self.close()  # bid 입력 창 닫기
                self.start_chat_loop(bid, bno)
            else:
                QMessageBox.critical(self, "오류", "bj가 방송중이지 않거나 유효하지 않은 id입니다.")
        else:
            QMessageBox.critical(self, "오류", "bj의 id를 입력해주세요.")

    def start_chat_loop(self, bid, bno):
        self.chat_app = ChatApp(bid, bno)
        self.chat_app.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    bid_input_app = BIDInputApp()
    bid_input_app.show()
    sys.exit(app.exec())
