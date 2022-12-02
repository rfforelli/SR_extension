import cv2
import csv
import sys
import numpy as np

DATA_FILE = sys.argv[1]
IMG_FILE = sys.argv[2]


with open(DATA_FILE, "r") as file:
    reader = csv.reader(file, delimiter=" ")
    row = next(reader)
    row = np.array(row, dtype=np.int32)
    N = row.shape[0]
    W = 2040
    C = 3
    H = int(N / (W * C))
    print("INFO: Image size {}x{}x{}".format(H, W, C))
    if H*W*C != N:
        print("ERROR: Unexpected size")
        exit(1)
    img = row.reshape(H, W, C)
    cv2.imwrite(IMG_FILE, img)
    print("INFO: Save:", IMG_FILE)
