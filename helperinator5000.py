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

#test_tags   = ["vriska", "persona 4", "homestuck", "reaction image", "!not homestuck"]
img_path    = "Pictures"
cfg_path    = "dir.cfg"
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
    def __init__(self, init_str = None, parent = None):
        self.init_str = str(init_str).strip()
        self.rule = []
        if init_str == None:
            self.parent = None
            self.path = img_path
        else:
            self.parent = parent
            (name, rule) = tuple(self.init_str.split(':'))
            self.path = self.parent.path + '/' + name
            clauses = rule.strip().split('&')
            clauses = filter(lambda x: x != "", clauses)
            for clause in clauses:
                clause = clause.strip().split('|')
                self.rule += [[i.strip() for i in clause]]
        self.children = []


    def check_rule(self, tags):
        if self.rule == []:
            return True
        if recursive and not self.parent.check_rule(tags):
            return False
        for clause in self.rule:
            good = set(filter(lambda x: x[0] != "!", clause))
            bad = set(map(lambda x: x[1:], set(clause) - good))
            if set(tags) & bad:
                return False
            if not set(tags) & good:
                return False
        return True


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
