#!/usr/bin/python
import pygtk
pygtk.require('2.0')
import gtk
import os
import sys
import re
import hashlib
import random
import pickle

IMG_DIR = "Pictures"
BLOCK_SIZE = 1024
IMG_HEIGHT = 700
IMG_WIDTH = 700

DEFAULT_ADDTAG = "Enter a new tag here."
DEFAULT_REMTAG = "Remove an old tag here."
DEFAULT_PATHENTRY = "path/to/specific/image"
DEFAULT_NAMEENTRY = "Enter a filename for this image."

DATA_FILE = "indexinator5000.dat"

class Catalogue:
    def __init__(self):
        self.images = {}
        self.tags = []
        self.current = {}

    def get_img(self, name, path = ""):
        hasher = hashlib.md5()
        if len(path) > 0 and path[len(path)-1] != '/':
            path = path + '/'
        try:
            f = file(path + name, 'r')
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
        self.images[self.current['md5']] = self.current

    def save(self):
        data = {'images': self.images,
                'tags': self.tags}
        pickle.dump(data, file(DATA_FILE, 'w+'))

    def load(self):
        try:
            data = pickle.load(file(DATA_FILE, 'r+'))
            self.images = data['images']
            self.tags = data['tags']
        except IOError:
            print "File %s not found." % DATA_FILE


cat = Catalogue()
cat.load()


class Base:
    def __init__(self):
        self.session_count = 1
        self.avtags = []
        self.usetags = []

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)

        #window.connect("key_press_event", self.temp)

        self.imglist = os.listdir(IMG_DIR)
        re_pic = re.compile("^.*\.(gif|jpg|jpeg|png|bmp)$")
        self.imglist = [name for name in self.imglist if re_pic.match(name) != None]
        self.unchecked = list(self.imglist)
        random.shuffle(self.unchecked)

        bigbox = gtk.HBox(False, 0)
        bigbox.show()
        imgbox = gtk.VBox(False, 0)
        imgbox.show()
        bigbox.pack_start(imgbox)

        self.image = gtk.Image()
        self.image.set_size_request(IMG_HEIGHT,IMG_WIDTH)
        imgbox.pack_start(self.image, expand=True, fill=False)

        # pathentry = gtk.Entry()
        # pathentry.show()
        # databox.pack_start(pathentry, expand=False, fill=False)
        # pathentry.connect("activate", self.get_path, pathentry)
        # pathentry.set_text(DEFAULT_PATHENTRY)

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
        submit.connect("clicked", lambda w: self.submit(self.nameentry))
        tagboxright.pack_end(submit, expand=False, fill=False, padding=6)

        self.nameentry.show()
        tagboxright.pack_end(self.nameentry, expand=False, fill=False, padding=0)
        self.nameentry.set_text(DEFAULT_NAMEENTRY)

        self.filename = gtk.Label("")
        self.filename.set_size_request(0,30)
        self.filename.show()
        tagboxright.pack_end(self.filename, expand=False, fill=False, padding=0)

        rementry = gtk.Entry()
        rementry.show()
        tagboxright.pack_end(rementry, expand=False, fill=False, padding=3)
        rementry.connect("activate", self.rem_tag, rementry)
        rementry.set_text(DEFAULT_REMTAG)

        addentry = gtk.Entry()
        addentry.show()
        tagboxright.pack_end(addentry, expand=False, fill=False, padding=3)
        addentry.connect("activate", self.add_tag, addentry)
        addentry.set_text(DEFAULT_ADDTAG)

        get_next = gtk.Button("Get Random Image")
        get_next.show()
        get_next.connect("clicked", lambda w: self.get_next())
        tagboxright.pack_end(get_next, expand=False, fill=False, padding=4)

        window.add(bigbox)
        window.show()

        self.get_next()


    def populate_avtagbox(self):
        for x in self.avtags:
            x.destroy()
        self.avtags = []
        for tag in cat.tags:
            x = gtk.Button(tag)
            self.avtags += [x]
            x.show()
            x.connect("clicked", lambda w: self.select_tag(w))
            self.avtagbox.pack_start(x, expand=False, fill=False)
        self.avtagbox.show()


    def populate_usetagbox(self):
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
        tag = button.get_label()
        if tag not in cat.current['tags']:
            cat.current['tags'] = sorted(cat.current['tags'] + [tag])
        self.populate_usetagbox()


    def unselect_tag(self, button):
        tag = button.get_label()
        cat.current['tags'] = [i for i in cat.current['tags'] if i != tag]
        self.populate_usetagbox()


    def add_tag(self, _, entry):
        tag = entry.get_text()
        if tag == DEFAULT_ADDTAG:
            return
        if tag not in cat.current['tags']:
            cat.current['tags'] = sorted(cat.current['tags'] + [tag])
        if tag not in cat.tags:
            cat.tags = sorted(cat.tags + [tag])
        entry.set_text("")
        self.populate_usetagbox()
        self.populate_avtagbox()


    def rem_tag(self, _, entry):
        tag = entry.get_text()
        cat.current['tags'] = [i for i in cat.current['tags'] if i != tag]
        cat.tags = [i for i in cat.tags if i != tag]
        entry.set_text("")
        self.populate_usetagbox()
        self.populate_avtagbox()


    def get_path(self, _, entry):
        path = entry.get_text()
        if path == DEFAULT_PATHENTRY:
            return
        print path


    def get_next(self):
        checknow = list(self.unchecked)
        found = False
        for i in checknow:
            name = i
            self.unchecked.remove(i)
            if cat.get_img(name, IMG_DIR):
                continue
            else:
                found = True
                break
        if not found:
            name = self.imglist[random.randint(0,len(self.imglist)-1)]
            cat.get_img(name, IMG_DIR)
        self.populate_usetagbox()
        self.populate_avtagbox()
        if cat.current['name'] == "":
            cat.current['name'] = name
        self.nameentry.set_text(cat.current['name'])
        self.filename.set_text("#%d: %s" % (self.session_count, name))
        self.display_img(name)


    def submit(self, entry):
        if cat.current:
            self.session_count += 1
            name = entry.get_text()
            if name == DEFAULT_NAMEENTRY:
                name = ""
            cat.current['name'] = name
            cat.current['tags'] = [x.get_label() for x in self.usetags]
            cat.add_current()
            cat.save()
            entry.set_text(DEFAULT_NAMEENTRY)
            self.get_next()


    def display_img(self, name):
        self.imgname = name
        scalebuf = gtk.gdk.pixbuf_new_from_file("%s/%s" % (IMG_DIR, self.imgname))
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
        IMG_DIR = sys.argv[1]
    base = Base()
    base.main()
