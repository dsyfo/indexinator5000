#!/usr/bin/python
import gtk
import os
import sys
import re
import hashlib
import random
import pickle

BLOCK_SIZE = 1024
IMG_HEIGHT = 600
IMG_WIDTH = 600

DEFAULT_ADDTAG = "Enter a new tag here."
DEFAULT_REMTAG = "Remove an old tag here."
DEFAULT_PATHENTRY = "Enter the name of a file to edit here."
DEFAULT_NAMEENTRY = "Enter a filename for this image."

DATA_FILE = "5000.dat"
img_dir = "Pictures"

class Catalogue:
    def __init__(self, input_file = None):
        if not input_file:
            input_file = DATA_FILE
        self.data_file = os.path.join(os.getcwd(), input_file)
        self.images = {}
        self.tags = []
        self.current = {}
        self.checked = []

    def get_img(self, name, path = ""):
        """
        Given an image name and a directory, retrieves an image and checks
        whether it has been archived previously, and creates an entry if not.
        """
        hasher = hashlib.md5()
        try:
            if len(path) > 0:
                temp = os.path.join(path, name)
            else:
                temp = name
            f = file(temp, 'r')
        except IOError:
            print "Could not find %s%s" % (path, name)
            return None
        buf = f.read(BLOCK_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCK_SIZE)
        md5 = hasher.digest()
        if md5 in self.images:
            self.current = self.images[md5]
            return True
        else:
            self.current = {'md5': md5, \
                            'name': '', \
                            'tags': [],  }
            return False

    def add_current(self):
        """ Adds the entry for the current image to the images archive. """
        self.images[self.current['md5']] = self.current

    def save(self):
        """ Writes all archived data to the file. """
        data = {'images': self.images,
                'tags': self.tags,
                'checked': self.checked}
        pickle.dump(data, file(self.data_file, 'w+'))

    def load(self):
        """ Loads an archive from the file. """
        try:
            data = pickle.load(file(self.data_file, 'r+'))
            self.images = data['images']
            self.tags = data['tags']
            if 'checked' in data:
                self.checked = data['checked']
        except IOError:
            print "File %s not found." % self.data_file


cat = Catalogue()
cat.load()


class Base:
    def __init__(self):
        self.session_count = 1
        self.avtags = []
        self.usetags = []
        self.filstr = ""

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)

        window.connect("key_press_event", self.key_press)

        self.imglist = os.listdir(img_dir)
        re_pic = re.compile("^.*\.(gif|jpg|jpeg|png|bmp)$")
        self.imglist = [name for name in self.imglist if re_pic.match(name) != None]
        if cat.checked:
            self.unchecked = list(set(self.imglist) - set(cat.checked))
        else:
            print "Please wait... checking for archived images."
            self.unchecked = [i for i in self.imglist if not cat.get_img(i, img_dir)]
            cat.checked = list(set(self.imglist) - set(self.unchecked))
        random.shuffle(self.unchecked)

        bigbox = gtk.HBox(False, 0)
        bigbox.show()
        imgbox = gtk.VBox(False, 0)
        imgbox.show()
        bigbox.pack_start(imgbox)

        self.image = gtk.Image()
        self.image.set_size_request(IMG_HEIGHT,IMG_WIDTH)
        imgbox.pack_start(self.image, expand=True, fill=False)

        pathentry = gtk.Entry()
        pathentry.show()
        imgbox.pack_start(pathentry, expand=False, fill=False)
        pathentry.connect("activate", self.get_path, pathentry)
        pathentry.set_text(DEFAULT_PATHENTRY)

        tagbox = gtk.HBox(False, 0)
        tagbox.show()
        bigbox.pack_start(tagbox)

        tagboxleft = gtk.VBox(False, 0)
        tagboxleft.show()
        tagbox.pack_start(tagboxleft)

        tagboxright = gtk.VBox(False, 0)
        tagboxright.show()
        tagbox.pack_start(tagboxright)

        avtagwindow = gtk.ScrolledWindow()
        avtagwindow.show()
        tagboxleft.pack_start(avtagwindow)
        avtagwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.avtagbox = gtk.VBox(False, 0)
        avtagwindow.add_with_viewport(self.avtagbox)
        self.populate_avtagbox()

        self.usetagbox = gtk.VBox(False, 0)
        self.usetagbox.show()
        tagboxright.pack_start(self.usetagbox, expand=True, fill=True)

        self.nameentry = gtk.Entry()

        submit = gtk.Button("Submit")
        submit.show()
        submit.connect("clicked", self.go_submit)
        tagboxright.pack_end(submit, expand=False, fill=False, padding=6)

        self.nameentry.show()
        self.nameentry.connect("activate", self.go_submit)
        tagboxright.pack_end(self.nameentry, expand=False, fill=False, padding=0)
        self.nameentry.set_text(DEFAULT_NAMEENTRY)

        self.filename = gtk.Label("")
        self.filename.set_size_request(0,30)
        self.filename.show()
        tagboxright.pack_end(self.filename, expand=False, fill=False, padding=0)

        self.rementry = gtk.Entry()
        self.rementry.show()
        tagboxright.pack_end(self.rementry, expand=False, fill=False, padding=3)
        self.rementry.connect("activate", self.rem_tag)
        self.rementry.set_text(DEFAULT_REMTAG)

        self.addentry = gtk.Entry()
        self.addentry.show()
        tagboxright.pack_end(self.addentry, expand=False, fill=False, padding=3)
        self.addentry.connect("activate", self.add_tag)
        self.addentry.set_text(DEFAULT_ADDTAG)

        get_next = gtk.Button("Get Random Image")
        get_next.show()
        get_next.connect("clicked", self.get_next)
        tagboxright.pack_end(get_next, expand=False, fill=False, padding=4)

        window.add(bigbox)
        window.show()

        self.get_next()


    def key_press(self, widget, event):
        """
        This function is called whenever a key is pressed. Currently it contains code
        for quick-picking tags and submitting images. (begin typing a tag name to filter
        the list of tags, press ` to add the topmost tag, press ~ to submit the entry.)
        """
        accepted = range(ord('a'), ord('z')+1) + [ord(' ')]
        if event.keyval in accepted:
            self.filstr += chr(event.keyval)
            self.populate_avtagbox()
        elif event.keyval == ord('`'):
            if len(self.avtags) > 0:
                self.select_tag(self.avtags[0])
        elif event.keyval == ord('~'):
            self.go_submit()
        elif self.filstr != "":
            self.filstr = ""
            self.populate_avtagbox()
        else:
            pass
            # print event.keyval


    def populate_avtagbox(self):
        """
        Reloads the list of available tags, filtering out the tags that begin with
        the string in self.filstr.
        """
        for x in self.avtags:
            x.destroy()
        self.avtags = []
        for tag in filter(lambda w: w[:len(self.filstr)] == self.filstr, cat.tags):
            x = gtk.Button(tag)
            self.avtags += [x]
            x.show()
            x.connect("clicked", lambda w: self.select_tag(w))
            self.avtagbox.pack_start(x, expand=False, fill=False)
        self.avtagbox.show()


    def populate_usetagbox(self):
        """ Reloads the list of currently used tags. """
        for x in self.usetags:
            x.destroy()
        self.usetags = []
        for tag in cat.current['tags']:
            x = gtk.Button(tag)
            self.usetags += [x]
            x.show()
            x.connect("clicked", lambda w: self.unselect_tag(w))
            self.usetagbox.pack_start(x, expand=False, fill=False)
        self.usetagbox.show()


    def select_tag(self, button):
        """ Adds a tag from the list of available tags to the list of used tags. """
        tag = button.get_label()
        if tag not in cat.current['tags']:
            cat.current['tags'] = sorted(cat.current['tags'] + [tag])
        self.populate_usetagbox()
        self.filstr = ""
        self.populate_avtagbox()


    def unselect_tag(self, button):
        """ Removes a tag from the list of used tags. """
        tag = button.get_label()
        cat.current['tags'] = [i for i in cat.current['tags'] if i != tag]
        self.populate_usetagbox()


    def add_tag(self, _):
        """ Adds a new tag to both lists (available and used) """
        tag = self.addentry.get_text().lower()
        for c in "!|&`~:":
            tag.replace(c, "?")
        if tag == "" or tag == DEFAULT_ADDTAG:
            return
        if tag not in cat.current['tags']:
            cat.current['tags'] = sorted(cat.current['tags'] + [tag])
        if tag not in cat.tags:
            cat.tags = sorted(cat.tags + [tag])
        self.addentry.set_text("")
        self.populate_usetagbox()
        self.populate_avtagbox()


    def rem_tag(self, _):
        """ Removes an existing tag from both lists (available and used) """
        tag = self.rementry.get_text()
        cat.current['tags'] = [i for i in cat.current['tags'] if i != tag]
        cat.tags = [i for i in cat.tags if i != tag]
        self.rementry.set_text("")
        self.populate_usetagbox()
        self.populate_avtagbox()


    def get_path(self, _, entry):
        """ Not currently used, but would give current working directory. """
        path = entry.get_text()
        if path == DEFAULT_PATHENTRY:
            return
        self.get_next(name = path)


    def get_next(self, _ = None, name = None):
        """
        Retrieves the next image and associated data when "submit" or
        "get random image" is pressed.
        """
        found = False
        if not name:
            while not found and len(self.unchecked) > 0:
                name = self.unchecked.pop()
                if not cat.get_img(name, img_dir):
                    found = True
            if not found:
                name = self.imglist[random.randint(0,len(self.imglist)-1)]
                cat.get_img(name, img_dir)
        elif not cat.get_img(name, img_dir):
            return
        if name not in cat.checked:
            cat.checked += [name]
        self.populate_usetagbox()
        self.populate_avtagbox()
        if cat.current['name'] == "":
            cat.current['name'] = name
        self.nameentry.set_text(cat.current['name'])
        self.filename.set_text("#%d: %s" % (self.session_count, name))
        self.display_img(name)


    def go_submit(self, _ = None):
        """ Saves the current image's data and loads the next image. """
        if cat.current:
            self.session_count += 1
            name = self.nameentry.get_text()
            if name == DEFAULT_NAMEENTRY:
                name = ""
            cat.current['name'] = name
            cat.current['tags'] = [x.get_label() for x in self.usetags]
            cat.add_current()
            cat.save()
            self.get_next()


    def display_img(self, name):
        """ Resizes and displays an image in the GUI. """
        self.imgname = name
        path = os.path.join(img_dir, self.imgname)
        scalebuf = gtk.gdk.pixbuf_new_from_file(path)
        if scalebuf.get_width() > scalebuf.get_height():
            multiplier = scalebuf.get_width() / float(IMG_WIDTH)
        else:
            multiplier = scalebuf.get_height() / float(IMG_HEIGHT)
        scalebuf = scalebuf.scale_simple(int(scalebuf.get_width() / multiplier), \
                int(scalebuf.get_height() / multiplier), \
                gtk.gdk.INTERP_BILINEAR)
        self.image.set_from_pixbuf(scalebuf)
        self.image.set_size_request(IMG_HEIGHT,IMG_WIDTH)
        self.image.show()


    def main(self):
        gtk.main()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        img_dir = sys.argv[1]
    else:
        img_dir = raw_input("Enter the name of the folder containing images. ")
    img_dir = os.path.join(os.getcwd(), img_dir)
    base = Base()
    base.main()
