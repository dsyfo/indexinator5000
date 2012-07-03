indexinator5000
===============

Image tagging system written in python.

INSTRUCTIONS
===========

IMPORTANT NOTE: This script works for Linux ONLY. It will create a large number of folders containing symbolic links to your images.

1. Gather the images you want to sort. Put all of the images into a folder in the current directory, let's say "Pictures", or create a softlink to it.


2. Run the Indexinator5000 on the above folder. Use the command:
    python indexinator5000.py Pictures
...if your chosen folder is "Pictures". A random image will appear. You can add tags to it by typing into the textbox marked "Enter a new tag here." Tags you've already used before will appear in the middle column.

ADVANCED TIPS: You can rapidly tag images by beginning to type the tag you want. Typing "`" will automatically select the tag at the top of the list and typing "~" will save the information you've entered and bring up the next image.


3. Create a directory configuration file. This is a file containing a list of directories you want to sort your images into and which tags you want to go into which folders. Here is an example configuration file:

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


4. Run the helper program to sort the images. This step will create the directories in your configuration file and symbolic links to your tagged images. Use the command:
    python helperinator5000.py Pictures Sorted homestuck.cfg
...if those are the names of your images folder, the destination folder, and your config file, respectively. The program will automatically create your sorted directory tree for you, assuming you tagged the images and put the rules into your configuration file correctly.


CONTACT INFORMATION
===========
http://polynomialspacenebula.tumblr.com/
onexorone@gmail.com
