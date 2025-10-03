from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class ProgramModel(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.filename = None
        self.filename_display = ui.fileNameLabel

    def OpenFileDialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options
        )
        if file_name:
            self.filename_display.setText(file_name)