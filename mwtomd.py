"""
horrible, terrible hacky quick script to convert the mediawiki
dump to markdown
"""

import sys
import csv
from pprint import pprint

f = open(sys.argv[1])

tablemode = False

table = []
row = []

for i in f:
    i = i.strip()
    i = i.replace("<code>", "`")
    i = i.replace("</code>", "`")
    i = i.replace("\\'", "'")
    i = i.replace('\\"', '"')
    if tablemode:
        items = i.split("|")
        lastitem = items[-1].strip()
        if i.endswith("}"):
            # pprint(table)
            print()
            for j in table:
                if len(j) == 0:
                    continue
                print("|{}|".format("|".join(j)))
                if "otal Size" in j[0]:
                    print("\n#### Fields\n")
            tablemode = False
            continue

        if lastitem.startswith('-'):
            table.append(row)
            row = []
        else:
            # print(items)
            if "acket ID" in lastitem:
                table.insert(0, [lastitem])
            elif "rowspan" in items[1]:
                table[0].append(lastitem)
            else:
                row.append(lastitem)
    else:
        if i.startswith("{"):
            table = []
            tablemode = True
            continue

        if i.startswith("===="):
            print("### " + i[4:-4])
        elif i.startswith("==="):
            print("## " + i[3:-3])
        elif i.startswith("=="):
            print("# " + i[2:-2])
        elif i.startswith("''"):
            print("#### " + i[2:-2])
        else:
            print(i)
