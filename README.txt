Czech Sign Language Dictionary


The Czech Sign Language Dictionary application is developed to provide a GUI where czech expressions are translated to czech sign language.

There are two ways how to input the expression that the user wishes to be translated. Either the expression can be typed into an entry field, or the user chooses a category, and possibly a subcategory, and then selects an expression from the displayed options. The Dictionary application then searches the database for the given expression.

* If the expression has been found, a video with its translation to sign language is played.
* If there are more than one possible translation of the given expression, the first translation is played and all the translations are displayed in small size below the main video screen. By double clicking on a small sized video, it can be played in the main video screen.
* If the expression has not been found in the database, the user is offered other expressions, that are in the database and that contain the original expression, to be translated instead.

The program is written in Python3, using the tkinter, pillow and OpenCV libraries, as well as sqlite3 database.


The directory containing this README file and the application itself is located at:
url of the main source

This serves as a sample code for the purpose of .......... application and is not intended for public use. Hence, the above mentioned videos do not contain the actual sign language translations, but demo animations instead.


Credit

In the Sign Language Dictionary application the following icons (located at ./dictionary/images directory) are used:

hint_icon.png is an icon (findicons.com/icon/455110/light_bulb_on) by Janik Baumgartner (kinaj.com) licensed under CC BY (creativecommons.org/licenses/by/4.0/)

add_icon.png, close_icon.png, del_draw.png, del_icon.png, search_icon.png, submit_icon.png, valid.png are icons from the Koloria icons set: www.graphicrating.com/2012/06/14/koloria-free-icons-set/

replay_arrow.png is an icon (findicons.com/icon/454622/arrow_circle_right) by The Working Group (blog.twg.ca) licensed under CC BY-SA (creativecommons.org/licenses/by-sa/4.0/)




The Dictionary application is started by running the 'main.py' python script.

