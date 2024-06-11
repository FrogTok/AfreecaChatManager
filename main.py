import sys
from apps.url_input import BIDInputApp
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
bid_input_app = BIDInputApp()
bid_input_app.show()
sys.exit(app.exec())
