#!/usr/bin/python
import os
import re
from sys import argv
from platform import system

operating_system = system().lower()

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
        if 'linux' in operating_system:
            source = source.replace(' ', '\ ')
            destination = destination.replace(' ', '\ ')
            cmd = "ln -s %s %s" % (source, destination)
            os.system(cmd)
        elif 'windows' in operating_system:
            shortcut = file(destination + '.url', 'w')
            shortcut.write('[InternetShortcut]\n')
            shortcut.write('URL="%s"' % source)
            shortcut.close()


    def __str__(self):
        return str(self.init_str)


if __name__ == "__main__":
    if len(argv) < 4:
        print operating_system
        print "USAGE: python helperinator5000.py <SOURCE FOLDER> <DESTINATION> <CONFIG>"
        exit(1)
    img_path = os.path.join(WORKING, argv[1])
    sorted_path = os.path.join(WORKING, argv[2])
    cfg_path = os.path.join(WORKING, argv[3])

    root = Node()
    current = root
    stack = []
    f = open(cfg_path)
    lastdepth = -1
    for line in f:
        if line.strip() == "":
            continue

        depth = len(line) - len(line.lstrip())
        if depth < lastdepth and len(stack) > 1:
            stack.pop()
        elif depth > lastdepth:
            stack += [current]
        lastdepth = depth

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
