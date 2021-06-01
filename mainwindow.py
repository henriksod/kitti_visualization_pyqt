from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from velodynewindow import VelodyneWindow
from camerawindow import CameraWindow

class MainWindow(QMainWindow):
    def __init__(self, opt, data, config, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.config = config
        
        self.layout = QVBoxLayout()
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.resize(280,40)
        self.layout.addWidget(self.textbox)
        self.button = QPushButton("Update")
        self.button.clicked.connect(self.on_click)
        self.layout.addWidget(self.button)
        self.velodyneWindow = VelodyneWindow(opt, data, config, parent=self)
        self.velodyneWindow.installEventFilter(self)
        self.velodyneWindow.show()
        self.cameraWindow = CameraWindow(opt, data, config, parent=self)
        self.cameraWindow.installEventFilter(self)
        self.cameraWindow.show()
        self.window = QWidget()
        self.window.setLayout(self.layout)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Kitti Visualization")
        self.setGeometry(200, 600, 400, 200)

    def on_click(self):
        self.velodyneWindow.setZoom(float(self.textbox.text()))

    def closeEvent(self, e: QCloseEvent) -> None:
        
        reply = QMessageBox.question(self,
                                     "Exit",
                                     "Save configuration?",
                                     QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes,
                                     QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.save()
            self.velodyneWindow.dispose()
            self.cameraWindow.dispose()
            e.accept()
        elif reply == QMessageBox.No:
            self.velodyneWindow.dispose()
            self.cameraWindow.dispose()
            e.accept()
        else:
            e.ignore()

    def save(self):
        self.velodyneWindow.save()
        self.cameraWindow.save()
        self.config.save()

