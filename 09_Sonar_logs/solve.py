#!/usr/bin/python3

from sys import stdin
from dateutil.parser import parse
import pytz


records = {}
for line in stdin:
    if line.find("detected") == -1:
        continue
    tokens = line.split()

    d = parse(tokens[0] + " " + tokens[1])
    t = pytz.timezone(tokens[2])
    char = chr(int(tokens[8]))

    timestamp = int(t.localize(d).timestamp())
    records[timestamp] = char

for timestamp in sorted(records.keys()):
    print(records[timestamp], end="")

print()
