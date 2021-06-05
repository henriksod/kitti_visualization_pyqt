from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import OpenGL.GL as gl
#import OpenGL.GLUT as glut
#import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo
from OpenGL.GL import shaders
import ctypes
import numpy as np

def float_size(n=1):
    return ctypes.sizeof(ctypes.c_float) * n


def pointer_offset(n=0):
    return ctypes.c_void_p(float_size(n))

class CameraWindow(QWidget):
    def __init__(self, opt, data, config, parent=None):
        QWidget.__init__(self)
        self.parent = parent
        self.config = config
        
        self.data = data
        self.scanIdx = 0
        
        self.cameraWidget = _CameraWidget(opt, data)
        layout = QStackedLayout()
        layout.addWidget(self.cameraWidget)
        self.setLayout(layout)
        self.setWindowTitle("Camera")
        self.setGeometry(self.config.get('camera_window_x',default=600),
                         self.config.get('camera_window_y',default=200),
                         self.config.get('camera_window_width', default=self.cameraWidget.frame.size[0]),
                         self.config.get('camera_window_height', default=self.cameraWidget.frame.size[1]))
        
    def setScanIdx(self, from_window, val):
        if (not (self.cameraWidget.scanIdx == val)) and len(self.data.cam1_files) > val >= 0:
            if from_window == self:
                self.parent.setScanIdx(self, val)
            self.cameraWidget.frame = self.data.get_cam2(val)
            self.cameraWidget.UpdateBuffer()
            self.cameraWidget.scanIdx = val
            self.scanIdx = val

    def getScanIdx(self): return self.scanIdx

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.setScanIdx(self, self.getScanIdx() + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.setScanIdx(self, self.getScanIdx() - 1)
        elif event.key() == QtCore.Qt.Key_Up:
            self.cameraWidget.zoom += .01
            print(self.cameraWidget.zoom, flush=True)
        elif event.key() == QtCore.Qt.Key_Down:
            self.cameraWidget.zoom -= .01
            print(self.cameraWidget.zoom, flush=True)
        event.accept()

    def save(self):
        self.config.put('camera_window_x', self.geometry().x())
        self.config.put('camera_window_y', self.geometry().y())
        self.config.put('camera_window_width', self.geometry().width())
        self.config.put('camera_window_height', self.geometry().height())

    def dispose(self):
        self.deleteLater()

class _CameraWidget(QOpenGLWidget):
    def __init__(self, opt, data, parent=None):
        QOpenGLWidget.__init__(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        self.data = data
        self.fbo = None
        self.texname = None
        self.frame = self.data.get_cam2(0)
        self.scanIdx = 0
        self.w = 500
        self.h = 500
        self.zoom = 0.01
        self.aspect_ratio = 1

    def initializeGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.generateTexture()
        self.resizeGL(self.w, self.h)

    def generateTexture(self):
        imdata = np.asarray(self.frame, np.uint8)
        if len(imdata.shape) < 3:
            imdata = np.stack((imdata,) * 3, axis=-1)
        self.texname = gl.glGenTextures(1)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texname)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)

        # Create the mipmapped texture
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, self.frame.size[0], self.frame.size[1], 0, gl.GL_RGB,
                        gl.GL_UNSIGNED_BYTE, imdata)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def drawImage(self, tex, x, y, w, h, angle):
        gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)
        gl.glPushMatrix()
        gl.glTranslatef(x,y,0.0)
        gl.glRotatef(angle, 0.0, 0.0, 1.0)

        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
        gl.glEnable(gl.GL_TEXTURE_2D)

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0.0, 0.0)
        gl.glVertex3f(x, y, 0.0)
        gl.glTexCoord2f(0.0, 1.0)
        gl.glVertex3f(x, y + h, 0.0)
        gl.glTexCoord2f(1.0, 1.0)
        gl.glVertex3f(x + w, y + h, 0.0)
        gl.glTexCoord2f(1.0, 0.0)
        gl.glVertex3f(x + w, y, 0.0)
        gl.glEnd()

        gl.glPopMatrix()

    def UpdateBuffer(self):
        self.generateTexture()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texname)

    def draw_texture_to_quad(self):
        gl.glClearColor(1., 0., 0., 1.0)
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.w, self.h, 0, -50.0, 50.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        self.drawImage(self.texname, 0.0, 0.0, self.w, self.h, 0.0)
        
    def paintGL(self):
        self.draw_texture_to_quad()
    
    def resizeGL(self, w, h):
        #self.aspect_ratio = self.frame.size[1] / self.frame.size[0]
        #self.w = int(w * self.aspect_ratio)
        #self.h = int(h * (1-self.aspect_ratio))

        #print(self.w, flush=True)
        self.w = w
        self.h = h
        gl.glViewport(0, 0, self.w, self.h)
        
        #side = min(self.w, self.h)
        #if side < 0:
        #    return

        #gl.glViewport((self.w - side) // 2, (self.h - side) // 2, side, side)
