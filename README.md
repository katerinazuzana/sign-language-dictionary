# Czech Sign Language Dictionary
> A bilingual dictionary for translating expressions to and from czech and czech sign language.

The Dictionary is built in Python 3 using the tkinter library and SQLite database.

Note: As I don't have permission to share publically the videos with sign language translations, the videos in the application don't capture actual signing persons, but there are demo animations (with a piece of text running across the screen) instead.

![screenshot](screenshot.png)

## Requirements

* Linux - tested on Ubuntu 16.04
* Python 3
* Pillow - the PIL fork: https://python-pillow.org/
* OpenCV: https://opencv.org/
* NumPy: http://www.numpy.org/
* (Optional) [Clearlooks ttk theme](https://github.com/RedFantom/ttkthemes/tree/master/ttkthemes/themes/clearlooks)

## Installation / environment setup

Linux:

The application can be run from source:
```python dictionary/main.py
```
after installing the dependencies:

**Pillow and NumPy**
```$ pip install Pillow numpy
```
**OpenCV**
Install for example by following Adrian Rosebrock's [tutorial](https://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/)

**Clearlooks theme** (Optional)
To install a ttk theme, see the Stephan Sokolow's blog post [Installing a new Ttk/Tile theme](http://blog.ssokolow.com/archives/2011/10/01/installing-a-new-ttktile-theme/)

## Meta

Katerina Zuzanakova – katerina.zuzanakova@gmail.com

Distributed under the MIT license. See ``LICENSE.md`` for more information.

[https://github.com/yourname/github-link](https://github.com/)

