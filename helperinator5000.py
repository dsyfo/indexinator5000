#!/usr/bin/python
import os
import re
from sys import argv
from platform import system

operating_system = system().lower()
pywin_found = False
if 'windows' in operating_system:
    try:
        from win32com.client import Dispatch
        print "PyWin32 found."
        i = raw_input("Should I use .lnk files instead of .url? y/n: ").lower()[0]
        pywin_found = (i == 'y')
    except ImportError:
        print "PyWin32 not detected on this machine."
        print "Should I continue by using .url files instead of .lnk shortcuts?"
        print "You won't be able to see thumbnails for the images in your browser."
        i = raw_input("y/n: ").lower()[0]
        if i != 'y':
            exit()

import indexinator5000 as i5k
cat = i5k.cat

"""
Folder tree is done using tabs, each name is followed by rule for sorting.

root: (No rule because any item can be placed in root)
    first_in_root: FIRST_RULE
        first_in_first: FIRST_FIRST_RULE
        second_in_first: FIRST_SECOND_RULE
    second_in_root: SECOND_RULE
    etc.
"""

WORKING     = os.getcwd()
# RECURSIVE: to be placed in a folder, image must satisfy conditions to be in parent
RECURSIVE   = True
# REDUNDANT: place image in all parents where it qualifies, not just the deepest node
REDUNDANT   = False

img_path = ""
sorted_path = ""
cfg_path = ""

"""
rules for each node use and-or format
    ex1: cat | dog & !bird -- YES if cat OR (dog AND NOT bird)
    ex2: bird | !cat & dog | fish -- YES if bird OR (NOT cat AND dog) OR fish
"""

class Node:
    def __init__(self, init_str = None, parent = None):
        self.init_str = str(init_str).strip()
        self.rule = []
        if init_str == None:
            self.parent = None
            self.path = sorted_path
        else:
            self.parent = parent
            (name, rule) = tuple(self.init_str.split(':'))
            self.path = os.path.join(self.parent.path, name)

            clauses = rule.strip().split('|')
            clauses = filter(lambda x: x != "", clauses)
            for clause in clauses:
                clause = clause.strip().split('&')
                self.rule += [[i.strip() for i in clause]]

        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        self.children = []


    def check_rule(self, tags):
        ''' Given tags for an image, checks whether the image belongs in this node. '''
        if self.rule == []:
            return True
        if RECURSIVE and not self.parent.check_rule(tags):
            return False

        for clause in self.rule:
            good = set(filter(lambda x: x[0] != "!", clause))
            bad = set(map(lambda x: x[1:], set(clause) - good))
            if set(tags) & bad:
                continue
            if set(tags) & good == good:
                return True

        return False


    def add_image(self, filename, img):
        ''' Recursively finds appropriate node for image and adds it. '''
        child_success = sum([i.add_image(filename, img) for i in self.children])
        self_success = self.check_rule(img['tags'])

        if REDUNDANT or not child_success:
            if (not RECURSIVE) or self.parent and self.parent.check_rule(img['tags']):
                if self_success and self.rule:
                    source = os.path.join(img_path, filename)
                    destination = os.path.join(self.path, img['name'])
                    self.create_link(source, destination)

        return child_success or self_success


    def create_link(self, source, destination):
        ''' Creates a soft link/shortcut to the image file in the source directory. '''
        if 'windows' in operating_system:
            if pywin_found:
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(destination + '.lnk')
                shortcut.Targetpath = source
                shortcut.WorkingDirectory = os.path.split(source)[0]
                shortcut.IconLocation = source
                shortcut.save()
            else:
                shortcut = file(destination + '.url', 'w')
                shortcut.write('[InternetShortcut]\n')
                shortcut.write('URL="%s"' % source)
                shortcut.close()
        else:
            source = source.replace(' ', '\ ')
            destination = destination.replace(' ', '\ ')
            cmd = "ln -s %s %s" % (source, destination)
            os.system(cmd)


    def __str__(self):
        return str(self.init_str)


if __name__ == "__main__":
    if len(argv) < 4:
        print "Operating system: " + operating_system
        img_path = raw_input("Name of folder containing unsorted images: ")
        sorted_path = raw_input("Name of folder to contain sorted images: ")
        cfg_path = raw_input("Name of sorting configuration file: ")
    else:
        img_path = argv[1]
        sorted_path = argv[2]
        cfg_path = argv[3]
    img_path = os.path.join(WORKING, img_path)
    sorted_path = os.path.join(WORKING, sorted_path)
    cfg_path = os.path.join(WORKING, cfg_path)

    # Build the directory tree, including rules for sorting images
    root = Node()
    current = root
    stack = []
    f = open(cfg_path)
    prevdepths = [-1]
    for line in f:
        if line.strip() == "":
            continue

        depth = len(line) - len(line.lstrip())
        lastdepth = prevdepths[len(prevdepths)-1]
        while lastdepth != depth:
            if depth < lastdepth and len(stack) > 1:
                stack.pop()
                prevdepths.pop()
            elif depth > lastdepth:
                stack += [current]
                prevdepths += [depth]
            else:
                break
            lastdepth = prevdepths[len(prevdepths)-1]

        top = stack[len(stack)-1]
        current = Node(line, top)
        top.children += [current]

    f.close()

    re_pic = re.compile("^.*\.(gif|jpg|jpeg|png|bmp)$")
    images = filter(lambda name: re_pic.match(name), os.listdir(img_path))

    print "Sorting images now."
    for filename in images:
        cat.get_img(filename, path=img_path)
        if 'tags' in cat.current and cat.current['tags']:
            root.add_image(filename, cat.current)
    print "Finished sorting."
