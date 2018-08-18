import sys
import os.path
import string
import struct
import numpy as np

def create(bntfilename):
    absfilename = bntfilename + '.txt'
    f = open(bntfilename, "rb")
    nrows = struct.unpack("H", f.read(2))[0]
    ncols = struct.unpack("H", f.read(2))[0]
    zmin = struct.unpack("d", f.read(8))[0]
    print
    nrows, ncols, zmin
    len = struct.unpack("H", f.read(2))[0]
    imfile = []
    for i in range(len):
        imfile.append(struct.unpack("c", f.read(1))[0])
    print
    imfile

    # % normally, size of data must be nrows*ncols*5
    size = struct.unpack("I", f.read(4))[0] / 5
    if (size != nrows * ncols):
        print_error("Uncoherent header: The size of the matrix is incorrect");

    data = {"x": [], "y": [], "z": [], "a": [], "b": [], "flag": []}
    for key in ["x", "y", "z", "a", "b"]:
        for i in range(nrows):
            # the range image is stored upsidedown in the .bnt file
            # |LL LR|              |UL UR|
            # |UL UR|  instead of  |LL LR|
            # As we dont want to use the insert function or compute
            # the destination of each value, we reverse the lines
            # |LR LL|
            # |UR UL|
            # and then reverse the whole list
            # |UL UR|
            # |LL LR|
            row = []
            for i in range(ncols):
                row.append(struct.unpack("d", f.read(8))[0])
            row.reverse()
            data[key].extend(row)
    f.close()
    # reverse list
    data["x"].reverse()
    data["y"].reverse()
    data["z"].reverse()
    data["a"].reverse()
    data["b"].reverse()

    # we determine the flag for each pixel
    for i in range(int(size)):
        if data["z"][i] == zmin:
            data["x"][i] = -999999.000000
            data["y"][i] = -999999.000000
            data["z"][i] = -999999.000000
            data["flag"].append(0)
        else:
            data["flag"].append(1)

    # Write the abs file
    # absfile = open(absfilename, "w")
    # absfile.write(string.join(map(str, data["flag"]), " ") + "\n")
    # absfile.write(string.join(map(str, data["x"]), " ") + "\n")
    # absfile.write(string.join(map(str, data["y"]), " ") + "\n")
    # absfile.write(string.join(map(str, data["z"]), " ") + "\n")
    # absfile.close()

    file=[]
    file.append(data["flag"])
    file.append(data["x"])
    file.append(data["y"])
    file.append(data["z"])
    return np.asanyarray(file, np.float64)