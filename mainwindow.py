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
        self.data = data
        self.children = []

        self.scanIdx = 0
        self.timestep = 50
        
        self.layout = QVBoxLayout()

        self.controls = QWidget(self)
        self.controlsLayout = QHBoxLayout()
        self.fsr_button = QPushButton("<<")
        self.fsr_button.clicked.connect(self.on_to_start)
        self.controlsLayout.addWidget(self.fsr_button)
        self.sr_button = QPushButton("<")
        self.sr_button.clicked.connect(self.on_step_reverse)
        self.controlsLayout.addWidget(self.sr_button)
        self.tp_button = QPushButton("▶")
        self.tp_button.clicked.connect(self.on_toggle_play)
        self.controlsLayout.addWidget(self.tp_button)
        self.sf_button = QPushButton(">")
        self.sf_button.clicked.connect(self.on_step_forward)
        self.controlsLayout.addWidget(self.sf_button)
        self.fsf_button = QPushButton(">>")
        self.fsf_button.clicked.connect(self.on_to_end)
        self.controlsLayout.addWidget(self.fsf_button)
        self.controls.setLayout(self.controlsLayout)

        self.layout.addWidget(self.controls)

        self.timeStep = QWidget(self)
        self.timeStepLayout = QHBoxLayout()
        self.l1 = QLabel("time step ms:")
        self.timeStepLayout.addWidget(self.l1)
        self.sp = QSpinBox()
        self.sp.setRange(1,100)
        self.sp.setValue(self.timestep)
        self.timeStepLayout.addWidget(self.sp)
        self.sp.valueChanged.connect(self.timestep_valuechange)
        self.timeStep.setLayout(self.timeStepLayout)

        self.layout.addWidget(self.timeStep)

        self.se_button = QPushButton("Save & Exit")
        self.se_button.clicked.connect(self.on_exit)
        self.layout.addWidget(self.se_button)

        self.velodyneWindow = VelodyneWindow(opt, data, config, parent=self)
        self.children.append(self.velodyneWindow)
        self.velodyneWindow.installEventFilter(self)
        self.velodyneWindow.show()

        self.cameraWindow = CameraWindow(opt, data, config, parent=self)
        self.children.append(self.cameraWindow)
        self.cameraWindow.installEventFilter(self)
        self.cameraWindow.show()

        self.window = QWidget()
        self.window.setLayout(self.layout)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Kitti Visualization")
        self.setGeometry(self.config.get('main_window_x', default=200),
                         self.config.get('main_window_y', default=600),
                         self.config.get('main_window_width', default=400),
                         self.config.get('main_window_height', default=200))

        self.play_toggle = True
        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.setInterval(self.timestep)  # in milliseconds, so 5000 = 5 seconds
        self.timer.timeout.connect(self.on_step_forward)

    def setScanIdx(self, from_window, val):
        if len(self.data.velo_files) > val >= 0:
            self.scanIdx = val
            for c in self.children:
                if not c == from_window:
                    c.setScanIdx(from_window, val)
        else:
            self.timer.stop()

    def getScanIdx(self):
        return self.scanIdx

    def on_toggle_play(self):
        if self.play_toggle:
            self.tp_button.setText("⏸")
            self.timer.start()
        else:
            self.tp_button.setText("▶")
            self.timer.stop()
        self.play_toggle = not self.play_toggle

    def on_step_reverse(self):
        self.setScanIdx(self, self.getScanIdx() - 1)

    def on_step_forward(self):
        self.setScanIdx(self, self.getScanIdx() + 1)

    def on_to_start(self):
        self.setScanIdx(self, 0)

    def on_to_end(self):
        self.setScanIdx(self, len(self.data.velo_files)-1)

    def timestep_valuechange(self):
        self.timestep = self.sp.value()
        self.timer.setInterval(self.timestep)

    def on_exit(self):
        self.save()
        for c in self.children:
            c.dispose()
        self.deleteLater()

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
        self.config.put('main_window_x', self.geometry().x())
        self.config.put('main_window_y', self.geometry().y())
        self.config.put('main_window_width', self.geometry().width())
        self.config.put('main_window_height', self.geometry().height())
        for c in self.children:
            c.save()
        self.config.save()

