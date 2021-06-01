from mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication
import pykitti
import sys
import argparse
from config import Config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str, default='', required=True, help='source') # path to kitti data folder
    parser.add_argument('--date', type=str, default='', required=True, help='date') # which date to grab data from
    parser.add_argument('--drive', type=str, default='', required=True, help='drive') # which drive number to grab data from
    parser.add_argument('-c', '--config', type=str, default='', required=True, help='config') # config file
    opt = parser.parse_args()
    
    data = pykitti.raw(opt.source, opt.date, opt.drive) # frames=range(0, 50, 5)
    # dataset.calib:         Calibration data are accessible as a named tuple
    # dataset.timestamps:    Timestamps are parsed into a list of datetime objects
    # dataset.oxts:          List of OXTS packets and 6-dof poses as named tuples
    # dataset.camN:          Returns a generator that loads individual images from camera N
    # dataset.get_camN(idx): Returns the image from camera N at idx  
    # dataset.gray:          Returns a generator that loads monochrome stereo pairs (cam0, cam1)
    # dataset.get_gray(idx): Returns the monochrome stereo pair at idx  
    # dataset.rgb:           Returns a generator that loads RGB stereo pairs (cam2, cam3)
    # dataset.get_rgb(idx):  Returns the RGB stereo pair at idx  
    # dataset.velo:          Returns a generator that loads velodyne scans as [x,y,z,reflectance]
    # dataset.get_velo(idx): Returns the velodyne scan at idx

    config = Config(opt.config)

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    w = MainWindow(opt, data, config)
    w.show()
    sys.exit(app.exec_())