from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtGui import QIcon
from chat.requests import get_bno, request_bj
from utils import get_root_directory_path
from apps.main_chat import ChatApp
import sys
import os
from dto import Bj


class BIDInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("방송 채팅 매니저")
        icon_path = os.path.join(get_root_directory_path(), "assets/afreeca.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(260, 100)

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
            bj : Bj = request_bj(bid)
            broad_no = get_bno(bj.id)
            if broad_no:
                self.close()  # bid 입력 창 닫기
                self.start_chat_loop(bj, broad_no)
            else:
                QMessageBox.critical(self, "오류", "bj가 방송중이지 않거나 유효하지 않은 id입니다.")
        else:
            QMessageBox.critical(self, "오류", "bj의 id를 입력해주세요.")

    def start_chat_loop(self, bj: Bj, broad_no: int):
        self.chat_app = ChatApp(bj, broad_no)
        self.chat_app.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    bid_input_app = BIDInputApp()
    bid_input_app.show()
    sys.exit(app.exec())
