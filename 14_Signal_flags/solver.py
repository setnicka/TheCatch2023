#!/usr/bin/python3

from multiprocessing import Pool

import os
import cv2
import numpy as np

processes = 8
threshold = 0.99
match_method = cv2.TM_CCOEFF_NORMED
flags_dir = "flags"
images_dir = "images"

# Options - grayscale for quicker matching, colors are distinguishable even in grayscale
# imread_options = None
imread_options = cv2.IMREAD_GRAYSCALE

# Load all flags named as 0.png, a.png, b.png, ...
print("Reading flags...")
flags = {}
for file in sorted(os.listdir(flags_dir)):
    parts = file.split(".", 2)
    if len(parts) == 2 and parts[1] == "png" and len(parts[0]) == 1:
        flags[parts[0]] = cv2.imread(os.path.join(flags_dir, file), imread_options)


def parseImage(filename):
    pid = os.getpid()
    # print(f"[{pid}] Processing {filename}")

    img = cv2.imread(filename, imread_options)

    # Quick test for hex image
    isHex = False
    if np.max(cv2.matchTemplate(img, flags['0'], match_method)) > threshold:
        isHex = True

    matches = []
    for (c, flag) in flags.items():
        if isHex and c > 'f' and c != 'x':
            continue  # skip non-hex flags

        h, w = flag.shape[0], flag.shape[1]

        res = cv2.matchTemplate(img, flag, match_method)
        locations = np.where(res >= threshold)

        for (y, x) in zip(locations[0], locations[1]):
            # Add match with coordinates of the center of the flag (flags could
            # have different heights and top of a tall flag could be higher than
            # top of the previous short flag)
            matches.append((c, x + w/2, y + h/2))
            # For debug:
            # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)

    # For debug:
    # cv2.imshow('Detected', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Sort matches by y top to down
    matches.sort(key=lambda tup: tup[2])

    msg = "".join(c for (c, _, _) in matches)
    if msg.startswith('0x'):
        msg = bytes.fromhex(msg[2:]).decode() + f" (orig: {msg})"
    print(f"[{pid}] {filename}: {msg}")
    return msg


print("Processing files...")
with Pool(processes=processes) as pool:
    filenames = [
        os.path.join(images_dir, f)
        for f in sorted(os.listdir(images_dir))
        if f.endswith(".png")
    ]
    results = pool.map(parseImage, filenames)

    for (f, r) in zip(filenames, results):
        print(f"{f}: {r}")
