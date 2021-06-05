from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import OpenGL.GL as gl
#import OpenGL.GLUT as glut
#import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo
import ctypes
import numpy as np

class VelodyneWindow(QWidget):
    def __init__(self, opt, data, config, parent=None):
        QWidget.__init__(self)
        self.parent = parent
        self.config = config
        
        self.data = data
        self.scan = self.data.get_velo(0)
        self.scanIdx = 0
        
        reshaped_scan = np.zeros((self.scan.shape[0],6))
        reshaped_scan[:,:-2] = self.scan
        reshaped_scan[:,3] = reshaped_scan[:,3] / (np.max(reshaped_scan[:,3]) + 1)
        reshaped_scan[:,4] = reshaped_scan[:,2] / (np.max(reshaped_scan[:,2]) + 1)
        vertices = reshaped_scan[:,0:3].astype('float32')#.tolist()
        colors = reshaped_scan[:,3:6].astype('float32')
        
        self.velodyneWidget = _VelodyneWidget(opt, vertices, colors)
        layout = QStackedLayout()
        layout.addWidget(self.velodyneWidget)
        self.setLayout(layout)
        self.setWindowTitle("Velodyne")
        self.setGeometry(self.config.get('velodyne_window_x',default=200),
                         self.config.get('velodyne_window_y',default=200),
                         self.config.get('velodyne_window_width',default=400),
                         self.config.get('velodyne_window_height',default=400))
        self.velodyneWidget.zoom = self.config.get('velodyne_view_zoom', default=0.5)
        self.velodyneWidget.ang = self.config.get('velodyne_view_yaw', default=0)
        self.velodyneWidget.ang2 = self.config.get('velodyne_view_pitch', default=0)
    
    def setScanIdx(self, from_window, val):
        if (not (self.velodyneWidget.scanIdx == val)) and len(self.data.velo_files) > val >= 0:
            if from_window == self:
                self.parent.setScanIdx(self, val)
            self.scan = self.data.get_velo(val)
            reshaped_scan = np.zeros((self.scan.shape[0],6))
            reshaped_scan[:,:-2] = self.scan
            reshaped_scan[:,3] = reshaped_scan[:,3] / (np.max(reshaped_scan[:,3]) + 1)
            reshaped_scan[:,4] = reshaped_scan[:,2] / (np.max(reshaped_scan[:,2]) + 1)
            self.velodyneWidget.vertices = reshaped_scan[:,0:3].astype('float32')#.tolist()
            colors = reshaped_scan[:,3:6].astype('float32')
            self.velodyneWidget.UpdateBuffer()
            self.velodyneWidget.scanIdx = val
            self.scanIdx = val

    def getScanIdx(self): return self.scanIdx
    
    def setZoom(self, val):
        self.velodyneWidget.zoom = val
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.setScanIdx(self, self.getScanIdx() + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.setScanIdx(self, self.getScanIdx() - 1)
        elif event.key() == QtCore.Qt.Key_Up:
            self.velodyneWidget.zoom += .01
        elif event.key() == QtCore.Qt.Key_Down:
            self.velodyneWidget.zoom -= .01
        elif event.key() == QtCore.Qt.Key_A:
            self.velodyneWidget.ang += 1
        elif event.key() == QtCore.Qt.Key_D:
            self.velodyneWidget.ang -= 1
        elif event.key() == QtCore.Qt.Key_W:
            self.velodyneWidget.ang2 += 1
        elif event.key() == QtCore.Qt.Key_S:
            self.velodyneWidget.ang2 -= 1
        event.accept()

    def save(self):
        self.config.put('velodyne_window_x', self.geometry().x())
        self.config.put('velodyne_window_y', self.geometry().y())
        self.config.put('velodyne_window_width', self.geometry().width())
        self.config.put('velodyne_window_height', self.geometry().height())
        self.config.put('velodyne_view_zoom', self.velodyneWidget.zoom)
        self.config.put('velodyne_view_yaw', self.velodyneWidget.ang)
        self.config.put('velodyne_view_pitch', self.velodyneWidget.ang2)

    def dispose(self):
        self.velodyneWidget.pos_vbo.delete()
        self.velodyneWidget.col_vbo.delete()
        self.deleteLater()

class _VelodyneWidget(QOpenGLWidget):
    def __init__(self, opt, vertices, colors, parent=None):
        QOpenGLWidget.__init__(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        self.vertices = vertices
        self.colors = colors
        self.scanIdx = 0
        self.pos_vbo = None
        self.col_vbo = None
        self.zoom = 0.5
        self.ang = 0.0
        self.ang2 = 0.0
        self.w = 500
        self.h = 500
        self.viewMatrix = None
    
    def CreateBuffer(self):
        self.pos_vbo = glvbo.VBO(data=self.vertices, usage=gl.GL_DYNAMIC_DRAW, target=gl.GL_ARRAY_BUFFER)
        self.col_vbo = glvbo.VBO(data=self.colors, usage=gl.GL_DYNAMIC_DRAW, target=gl.GL_ARRAY_BUFFER)
    
    def UpdateBuffer(self):
        self.pos_vbo.set_array(self.vertices)
        self.col_vbo.set_array(self.colors)
    
    def initializeGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.CreateBuffer()
    
    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-self.w*self.zoom/2, self.w*self.zoom/2, self.h*self.zoom/2, -self.h*self.zoom/2, -50.0, 50.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glRotated(self.ang, 0.0, 1.0, 0.0)
        gl.glRotated(self.ang2, 1.0, 0.0, 0.0)
        
        gl.glPointSize(2)

        self.pos_vbo.bind()
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        self.col_vbo.bind()
        gl.glEnableVertexAttribArray(3)
        gl.glVertexAttribPointer(3, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self.vertices))
    
    def resizeGL(self, w, h):
        self.w = w
        self.h = h
        
        side = min(w, h)
        if side < 0:
            return

        gl.glViewport((w - side) // 2, (h - side) // 2, side, side)
