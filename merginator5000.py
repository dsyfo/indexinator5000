#!/usr/bin/python
from sys import argv
import indexinator5000 as i5k

cat = i5k.cat

MERGE_COMBMINE  = 1
MERGE_COMBYOURS = 2
MERGE_MINE      = 3
MERGE_YOURS     = 4

if __name__ == "__main__":
    if len(argv) < 2:
        foreign = raw_input("Name of foreign archive to merge: ")
    else:
        foreign = argv[1]
    foreign = i5k.Catalogue(foreign)
    foreign.load()
    print "How would you like to handle merge conflicts?"
    print "1 - Combine the tags from both archives, keep my filenames."
    print "2 - Combine the tags from both archives, keep foreign filenames."
    print "3 - Keep my tags and filenames only."
    print "4 - Keep the foreign tags and filenames only."
    conflicts = int(raw_input("Please enter a number (1-4): "))
    if conflicts not in range(1,5):
        exit(1)

    print "Merging archives now."
    running_tags = set(cat.tags)
    for fimage in foreign.images:
        if fimage in cat.images:
            if conflicts == MERGE_COMBMINE:
                cat.images[fimage]['tags'] += foreign.images[fimage]['tags']
            elif conflicts == MERGE_COMBYOURS:
                cat.images[fimage]['tags'] += foreign.images[fimage]['tags']
                cat.images[fimage]['name'] = foreign.images[fimage]['name']
            elif conflicts == MERGE_MINE:
                pass
            elif conflicts == MERGE_YOURS:
                cat.images[fimage]['tags'] = list(foreign.images[fimage]['tags'])
                cat.images[fimage]['name'] = foreign.images[fimage]['name']

            cat.images[fimage]['tags'] = list(set(cat.images[fimage]['tags']))
        else:
            cat.images[fimage] = dict(foreign.images[fimage])
        running_tags = running_tags | set(cat.images[fimage]['tags'])
    cat.tags = list(running_tags)
    cat.save()
    print "Finished merging."
