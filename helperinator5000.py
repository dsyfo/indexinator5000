#!/usr/bin/python
import os
import re

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
IMG_PATH    = "%s/Pictures" % WORKING
SORTED_PATH = "%s/Sorted" % WORKING
cfg_path    = "dir.cfg"
# RECURSIVE: to be placed in a folder, image must satisfy conditions to be in parent
RECURSIVE   = True
# REDUNDANT: place image in all parents where it qualifies, not just the deepest node
REDUNDANT   = False

"""
rules for each node use or-and format
    ex1: cat | dog & !bird -- YES if (cat OR dog) AND (NOT bird)
    ex2: bird | !cat & bird | !dog -- YES if (bird OR NOT cat) AND (bird OR NOT dog)
"""

class Node:
    def __init__(self, init_str = None, parent = None):
        self.init_str = str(init_str).strip()
        self.rule = []
        if init_str == None:
            self.parent = None
            self.path = SORTED_PATH
            if self.path[len(self.path)-1] == "/":
                self.path = self.path[:len(self.path)-1]
        else:
            self.parent = parent
            (name, rule) = tuple(self.init_str.split(':'))
            self.path = self.parent.path + '/' + name
            clauses = rule.strip().split('&')
            clauses = filter(lambda x: x != "", clauses)
            for clause in clauses:
                clause = clause.strip().split('|')
                self.rule += [[i.strip() for i in clause]]
        if not os.path.isdir(self.path):
            os.system("mkdir %s" % self.path)
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
                return False
            if not set(tags) & good:
                return False
        return True


    def add_image(self, filename, img):
        child_success = sum([i.add_image(filename, img) for i in self.children])
        self_success = self.check_rule(img['tags'])
        if REDUNDANT or not child_success:
            if (not RECURSIVE) or self.parent.check_rule(img['tags']):
                if self_success and self.rule:
                    os.system("ln -s %s/%s %s/%s" % \
                            (IMG_PATH, filename, self.path, img['name']))
                    print self.path
        return child_success or self_success


    def __str__(self):
        return str(self.init_str)


if __name__ == "__main__":
    root = Node()
    current = root
    stack = []
    f = open(cfg_path)
    lastdepth = -1
    for line in f:
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
    images = filter(lambda name: re_pic.match(name), os.listdir(IMG_PATH))
    for filename in images:
        cat.get_img(filename, path=IMG_PATH)
        if 'tags' in cat.current and cat.current['tags']:
            print filename
            root.add_image(filename, cat.current)
