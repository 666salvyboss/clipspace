import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal, Slot
from gui_core import GuiCore


class GuiApp(QWidget):
    data_loaded = Signal(list)  # Signal to pass list from thread to UI
    deleted_done = Signal()     # NEW: Signal to confirm deletion complete

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard Manager")
        self.setMinimumSize(500, 500)

        font = QFont("Arial", 12)

        self.status_label = QLabel("Work at your pace")
        self.status_label.setFont(font)
        self.status_label.hide()

        self.refresh_copy_btn = QPushButton("Show Copy History")
        self.refresh_pin_btn = QPushButton("Show Pin History")
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.copy_list = QListWidget()

        for btn in [self.refresh_copy_btn, self.refresh_pin_btn, self.delete_selected_btn]:
            btn.setFont(font)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_copy_btn)
        button_layout.addWidget(self.refresh_pin_btn)
        button_layout.addWidget(self.delete_selected_btn)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.copy_list)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Connect signals
        self.refresh_copy_btn.clicked.connect(self.load_copy_history)
        self.refresh_pin_btn.clicked.connect(self.load_pin_history)
        self.delete_selected_btn.clicked.connect(self.delete_selected)
        self.data_loaded.connect(self._populate_list)
        self.deleted_done.connect(self._show_deleted_message)  # CONNECT SIGNAL

        self.current_mode = "copy"

    def load_copy_history(self):
        self.status_label.setText("Loading copy history...")
        self.status_label.show()
        self.copy_list.clear()
        self.current_mode = "copy"
        threading.Thread(target=self._load_copy_history_thread, daemon=True).start()

    def _load_copy_history_thread(self):
        items = GuiCore.show_copy_history()
        self.data_loaded.emit(items)  # Emit signal with data

    def load_pin_history(self):
        self.status_label.setText("Loading pin history...")
        self.status_label.show()
        self.copy_list.clear()
        self.current_mode = "pin"
        threading.Thread(target=self._load_pin_history_thread, daemon=True).start()

    def _load_pin_history_thread(self):
        items = GuiCore.pin_history()
        self.data_loaded.emit(items)  # Emit signal with data

    @Slot(list)
    def _populate_list(self, items):
        self.copy_list.clear()  # Clear existing items
        for text in items:
            item = QListWidgetItem()
            checkbox = QCheckBox(text)
            self.copy_list.addItem(item)
            self.copy_list.setItemWidget(item, checkbox)
        self.status_label.hide()

    def delete_selected(self):
        items_to_delete = []
        for index in range(self.copy_list.count()):
            item = self.copy_list.item(index)
            widget = self.copy_list.itemWidget(item)
            if widget and widget.isChecked():
                clean_text = widget.text().split(" - ")[0].strip()
                items_to_delete.append(clean_text)

        if not items_to_delete:
            QMessageBox.information(self, "Info", "No item selected.")
            return

        threading.Thread(target=self._delete_items_thread, args=(items_to_delete,), daemon=True).start()

    def _delete_items_thread(self, items):
        for item_text in items:
            if self.current_mode == "copy":
                GuiCore.delete_copy(item_text)
            elif self.current_mode == "pin":
                GuiCore.delete_specific_pin(item_text)

        self.data_loaded.emit([])     # Clear list
        self.deleted_done.emit()      # Trigger status update

    @Slot()
    def _show_deleted_message(self):
        self.status_label.setText("Deleted successfully.")
        self.status_label.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GuiApp()
    window.show()
    sys.exit(app.exec())

