indexinator5000
===============

Image tagging system written in python.

INSTRUCTIONS
===========

0. DOWNLOAD AND INSTALL THE REQUIRED PACKAGES
If you're a linux user you probably don't have to worry about this because you have a package manager, and python and pygtk are already installed on your system.
If you're a windows user, here's everything you'll need.
    Python 2.6/2.7      - http://www.python.org/download/
    Gtk+                - http://ftp.gnome.org/pub/gnome/binaries/win32/gtk+/2.24/gtk+_2.24.10-1_win32.zip
    PyGtk               - http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/
    PyCairo             - http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/
    PyGObject           - http://ftp.gnome.org/pub/GNOME/binaries/win32/pygobject/
    (OPTIONAL) PyWin32  - Can create Windows shortcuts (with thumbnails) instead of *.url files.
Install all that, and learn how to run *.py files in Python.
And of course, download indexinator5000.py, helperinator5000.py, and merginator5000.py from this github repository.


1. GATHER THE IMAGES YOU WANT TO SORT
Put all of the images into a folder in the same directory as Indexinator, let's say "Pictures", or create a softlink to it.


2. RUN INDEXINATOR5000 TO BEGIN CATALOGUING IMAGES
Run the Indexinator5000 on the above folder of untagged images. Linux users run the command:
    python indexinator5000.py Pictures

...if your chosen folder is "Pictures". A random image will appear. You can add tags to it by typing into the textbox marked "Enter a new tag here." Tags you've already used before will appear in the middle column. Every time you submit new tags for an image, the data is saved in a file called "5000.dat".

ADVANCED TIPS: You can rapidly tag images by beginning to type the tag you want. Typing "`" will automatically select the tag at the top of the list and typing "~" will save the information you've entered and bring up the next image.


3. CREATE A DIRECTORY CONFIGURATION FILE
This is a file containing a list of directories you want to sort your images into and which tags you want to go into which folders. Here is an example configuration file:

homestuck: homestuck
    trolls: karkat | terezi | kanaya | tavros | sollux
    kids: john | rose | dave | jade
    shipping: shipping
        johnkat: john & karkat
        hivebent: vriska & tavros | equius & aradia
        otp: john & vriska | jade & karkat
other: !homestuck
    reaction images: reaction images
        angry: mad
        sad: sad

Here's how this configuration file works. All images tagged with homestuck go into a homestuck folder. If the images are tagged with "karkat", they go into the trolls folder. If they're tagged with "john", they go into the kids folder. If the images are tagged with both "john" and "karkat" AND "shipping", they will go into the johnkat folder.
Any image not tagged with "homestuck" goes into the other folder. If they are reaction images, they will go into the reaction images folder. You can see the pattern.
Give your configuration a fitting name, like "homestuck.cfg".


4. RUN THE HELPER PROGRAM TO SORT TAGGED IMAGES
This step will create the directories in your configuration file and symbolic links to your tagged images. Linux users run the command:
    python helperinator5000.py Pictures Sorted homestuck.cfg

...if those are the names of your images folder, the destination folder, and your config file, respectively. The program will automatically create your sorted directory tree for you, assuming you tagged the images and put the rules into your configuration file correctly.


CONTACT INFORMATION
===========
http://polynomialspacenebula.tumblr.com/
onexorone@gmail.com
