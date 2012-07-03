#!/usr/bin/python

"""
Folder tree is done using tabs, each name is followed by rule for sorting.

root: (No rule because any item can be placed in root)
    first_in_root: FIRST_RULE
        first_in_first: FIRST_FIRST_RULE
        second_in_first: FIRST_SECOND_RULE
    second_in_root: SECOND_RULE
    etc.
"""

img_path    = ""
cfg_path    = ""
# recursive: to be placed in a folder, image must satisfy conditions to be in parent
recursive   = True
# redundant: place image in all parents where it qualifies, not just the deepest node
redundant   = False

"""
rules for each node use or-and format
    ex1: cat | dog & !bird -- YES if (cat OR dog) AND (NOT bird)
    ex2: bird | !cat & bird | !dog -- YES if (bird OR NOT cat) AND (bird OR NOT dog)
"""

class Node:
    def __init__(self, init_str = None):
        if self.init_str == None:
            self.parent = None
            self.path = ""
            self.tags = []
            self.children = []
            self.rule = None

if __name__ == "__main__":
    pass
