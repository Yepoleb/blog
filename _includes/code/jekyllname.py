#!/usr/bin/env python3

import os.path
import sys

if len(sys.argv) != 2:
    print("Usage: {} post.md".format(sys.argv[0]))
    exit()
path = sys.argv[1]

f = open(path)
title = None
date = None
# Find the title and date header values
for line in f:
    line = line.strip()
    if ": " not in line:
        continue
    k, v = line.split(": ", 1)
    if k == "title":
        title = v
    elif k == "date":
        date = v.split()[0]

if not title:
    print("Could not find title")
    exit()
if not date:
    print("Could not find date")
    exit()

title = title.lower().replace(" ", "-")
filename = date + "-" + title + ".md"
dirname = os.path.dirname(path)
new_path = os.path.join(dirname, filename)
os.rename(path, new_path)
