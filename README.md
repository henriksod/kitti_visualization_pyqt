# kitti_visualization_pyqt
Visualization of Kitti Dataset lidar and camera with OpenGL and PyQt

## How to run
- Clone this repo
- `cd kitti_visualization_pyqt`
- Create venv `python -m venv .venv`
- Load venv from e.g. Git Bash on Windows `. .venv/Scripts/activate` or on Linux `. .venv/bin/activate`
- Install requirements `pip install -r requirements.txt`
- Download 3.1.5 wheel from [OpenGL](https://www.lfd.uci.edu/~gohlke/pythonlibs/) and run `pip install PyOpenGL-3.1.5-cpXX-cpXX-win_amd64.whl`
- Download a drive from [kitti raw data](http://www.cvlibs.net/datasets/kitti/raw_data.php), e.g. [this one](https://s3.eu-central-1.amazonaws.com/avg-kitti/raw_data/2011_09_26_drive_0009/2011_09_26_drive_0009_sync.zip). Make sure to pick `synced+rectified data`.
- Run e.g. `python main.py --source ~/data/ --date 2011_09_26 --drive 0009 --config config.yaml`
