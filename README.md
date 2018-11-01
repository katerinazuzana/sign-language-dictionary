# Czech Sign Language Dictionary
> A bilingual dictionary for translating expressions to and from czech and czech sign language.

The Dictionary is built in Python 3 using the tkinter library and SQLite database.

**Note:** As I don't have permission to share publically the videos with sign language translations, the videos in the application don't capture actual signing persons -- there are demo animations (with a piece of text running across the screen) instead.

![screenshot](screenshot.png)

## Requirements

* Linux
* Python 3.5+
* Pillow - the PIL fork: https://python-pillow.org/
* OpenCV: https://opencv.org/
* NumPy: http://www.numpy.org/
* (Optional) [Clearlooks ttk theme](https://github.com/RedFantom/ttkthemes/tree/master/ttkthemes/themes/clearlooks)

## Installation

Linux:

The application can be run from `dictionary` directory by:
```python main.py
```
after installing the dependencies:

**Pillow and NumPy**
```$ pip3 install Pillow numpy
```
**OpenCV**
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential \
    cmake \
    libavformat-dev \
    libswscale-dev \
    pkg-config
cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.2.zip
unzip opencv.zip
mkdir -p ~/opencv-3.4.2/build
cd /opencv-3.4.2/build
cmake -DCMAKE\_BUILD_TYPE=RELEASE \
    -DCMAKE\_INSTALL_PREFIX=/usr/local \
    -DPYTHON_EXECUTABLE=$(which python3) ..
make -j$(nproc)
sudo make install
rm ~/opencv.zip
rm -r /opencv-3.4.2
```
**Clearlooks theme** (Optional)
```
cd ~
git clone https://github.com/RedFantom/ttkthemes.git
mkdir -p /usr/share/ttkthemes
cp -r ttkthemes/ttkthemes/themes/clearlooks /usr/share/ttkthemes
mv /usr/share/ttkthemes/clearlooks/clearlooks.tcl /usr/share/ttkthemes/clearlooks/clearlooks8.5.tcl
echo "export TCLLIBPATH=/usr/share/ttkthemes" >> ~/.bashrc
rm -r ttkthemes
```

### Running from a docker container
Another way of running the application is from a docker container:
```
docker build -t dictionary .
docker run --rm -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY dictionary
```

## Meta

Katerina Zuzanakova - katerina.zuzanakova@gmail.com

Distributed under the MIT license. See ``LICENSE.md`` for more information.

https://github.com/katerinazuzana/sign-language-dictionary
