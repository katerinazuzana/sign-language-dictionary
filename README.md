# Czech Sign Language Dictionary

> A bilingual dictionary for translating expressions to and from Czech and Czech Sign Language.

The Dictionary is built in Python 3 using the tkinter library and SQLite database.



![screenshot](screenshot.png)

**Note:** As I don't have permission to share publically the videos with sign language translations, the videos in the application don't capture actual signing persons -- there are demo animations (with a piece of text running across the screen) instead.

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
```
python main.py
```
after installing the dependencies:

**Pillow and NumPy**

```
$ pip3 install Pillow numpy
```
**OpenCV**

To install OpenCV, see for example Adrian Rosebrock's [tutorial](https://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/) (for Ubuntu)

**Clearlooks theme** (Optional)
```
cd ~
git clone https://github.com/RedFantom/ttkthemes.git
mkdir -p ~/.local/share/ttkthemes
cp -r ttkthemes/ttkthemes/themes/clearlooks ~/.local/share/ttkthemes
mv ~/.local/share/ttkthemes/clearlooks/clearlooks.tcl ~/.local/share/ttkthemes/clearlooks/clearlooks8.5.tcl
echo "export TCLLIBPATH=~/.local/share/ttkthemes" >> ~/.bashrc
rm -rf ttkthemes
```
(based on Stephan Sokolow's blog post [Installing a new Ttk/Tile theme](http://blog.ssokolow.com/archives/2011/10/01/installing-a-new-ttktile-theme/))

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
