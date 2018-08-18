#!/usr/bin/env python
#
# abs2obj.py: convert a *.abs file from the Face Recognition Grand Challenge
# database (FRGC) to an *.obj file (wavefront).
# The output mesh is made of triangles defined counterclockwise when seen from
# the camera position.
#
#
# Copyright (C) 2010  Clement Creusot
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import string
import os.path
import getopt
import tempfile
from subprocess import *


def print_help():
    print
    "Usage: " + os.path.basename(sys.argv[0]) + " [OPTIONS] filein.abs[.gz]"
    print
    "   Options: -o OUTPUT_FILE"
    print
    "               Write the output mesh in OUTPUT_FILE"
    print
    "            -d FACTOR"
    print
    "               Downsample(average) the size of the 2D range image by FACTOR"
    print
    "            -r (dx)x(dy)"
    print
    "               Fix the size of output pixels (not compatible with -d)"
    print
    "            -c produce cross connection (8 instead of 6)"
    print
    "            -t D "
    print
    "               convert only the upper D millimeters of the mesh"
    print
    "            -p PERCENT minimum % of defined flags for the first line (when using -t)"
    print
    "            -T produce vt (texture) vertex "
    print
    "            -s '5x5,10' spike removal (mean) window and threshold (before reduction)"
    print
    "            -S '5x5,10' spike removal (erase) window and threshold (after reduction)"
    sys.exit()


def print_error(*str):
    print
    "ERROR: ",
    for i in str:
        print
        i,
    print
    sys.exit()


# Reading the parameters
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'ho:d:ct:p:s:S:r:T')
except getopt.GetoptError, err:
    print
    str(err)
    print_help()

if len(args) < 1:
    print_help()

absfilename = args[0]
# By default the output is the abs filename followed by '.obj'
objfilename = absfilename.replace(".gz", "") + ".obj"

# By default we reduce the size image per 4
# There will be one vertex for every 16 pixels.
reductionFactor = 4
resolution = []
crossConnection = False
spikeRemoval = []
spikeRemoval2 = []
tmp = ""
topcrop = ""
minFlagRatio = ""
useTexture = False

# Uncompress if compressed
if absfilename.rfind(".gz") != -1:
    code, tmp = tempfile.mkstemp(suffix=".abs")
    call("gunzip -c " + absfilename + " > " + tmp, shell=True);
    absfilename = tmp

if cmp(string.split(absfilename, ".")[-1].lower(), "abs") != 0:
    print_error(absfilename, ": The file is not an .abs file.")
if not os.path.exists(absfilename):
    print_error(absfilename, ": The file doesn't exist.")

# use options
for opt, value in optlist:
    if opt in ("-h", "--help"):
        print_help()
    elif opt == '-o':
        objfilename = value
    elif opt == '-t':
        topcrop = float(value)
    elif opt == '-T':
        useTexture = True
    elif opt == '-p':
        minFlagRatio = float(value)
    elif opt == '-c':
        crossConnection = True
    elif opt == '-s':
        try:
            aux = string.split(value, ",")
            spikeRemoval = map(int, string.split(aux[0], "x"))
            spikeRemoval.append(float(aux[1]))
            if len(spikeRemoval) != 3:
                raise NameError('missing parameter')
        except:
            print_error("spike removal parameter should be 'PxQ,distance'")
    elif opt == '-S':
        try:
            aux = string.split(value, ",")
            spikeRemoval2 = map(int, string.split(aux[0], "x"))
            spikeRemoval2.append(float(aux[1]))
            if len(spikeRemoval2) != 3:
                raise NameError('missing parameter')
        except:
            print_error("spike removal parameter should be 'PxQ,distance'")
    elif opt == '-d':
        try:
            reductionFactor = int(value)
        except ValueError:
            print_error(value, " is not an integer")
    elif opt == '-r':
        try:
            resolution = map(float, string.split(value, "x"))
            if len(resolution) != 2:
                raise NameError('missing parameter')
        except:
            print_error(value, " resolution should be 'axb'")
    else:
        print
        "Unhandled option"
        print_help()

# start reading the ABS file
absfile = open(absfilename, "r")
try:
    tab = string.split(absfile.readline())
    rows = int(tab[0])
    tab = string.split(absfile.readline())
    columns = int(tab[0])
    tab = string.split(absfile.readline())  # comment pixel
except ValueError:
    print_error("Bad ABS header")

# Read all the flags 0 or 1
flags = map(int, string.split(absfile.readline()))
# Read all the x,y and z coordinates
X = map(float, string.split(absfile.readline()))
Y = map(float, string.split(absfile.readline()))
Z = map(float, string.split(absfile.readline()))
absfile.close()

if spikeRemoval != []:
    removedNb = 0
    p = (spikeRemoval[0] - 1) / 2
    q = (spikeRemoval[1] - 1) / 2
    for ii in range(rows - 2 * q):
        i = ii + q
        for jj in range(columns - 2 * p):
            j = jj + p
            validNb = 0
            awayNb = 0
            sumZ = 0.0
            center = (ii + q) * columns + jj + p
            if flags[center] != 1:
                continue
            for a in range(q * 2 + 1):  # local matrix
                for b in range(p * 2 + 1):
                    if a == q and b == p:  # dont count center point
                        continue
                    offset = (ii + a) * columns + jj + b
                    if flags[offset] != 1:
                        continue
                    validNb += 1
                    sumZ += Z[offset]
                    if abs(Z[offset] - Z[center]) > spikeRemoval[2]:
                        awayNb += 1
            if awayNb > validNb / 2.0:
                Z[center] = sumZ / float(validNb)
                removedNb += 1
    # print removedNb

if topcrop != "":
    # only keep the topcrop first mm on top of the mesh
    threshold = - topcrop
    if minFlagRatio == "":
        for i, f in enumerate(flags):
            if f == 1:
                threshold += Y[i]
                break
    else:
        for i in range(rows):
            trueFlagNb = 0
            ycurr = 0.0
            for j in range(columns):
                if flags[i * columns + j] == 1:
                    trueFlagNb += 1
                    ycurr = Y[i * columns + j]
            if trueFlagNb / float(columns) * 100 > minFlagRatio:
                threshold += ycurr
                break
            else:  # set flags to 0
                for j in range(columns):
                    flags[i * columns + j] = 0

    for i, y in enumerate(Y):
        if y < threshold:
            flags[i] = 0

    # print threshold, topcrop

if resolution != []:
    # compute the window of interest
    ymin = 9999999.0
    ymax = -9999999.0
    xmin = 9999999.0
    xmax = -9999999.0
    yargmin = -1
    yargmax = -1
    xargmin = -1
    xargmax = -1
    for i in range(rows):  # ymax
        for j in range(columns):
            offset = i * columns + j
            if flags[offset] == 1:
                if Y[offset] > ymax:
                    yargmax = i
                    ymax = Y[offset]
                    # if yargmax !=-1:
        #    break
    for i in range(rows):  # ymin
        for j in range(columns):
            offset = (rows - 1 - i) * columns + j
            if flags[offset] == 1:
                if Y[offset] < ymin:
                    yargmin = (rows - 1 - i)
                    ymin = Y[offset]
    for i in range(rows):
        for j in range(columns):  # xmin
            offset = i * columns + j
            if flags[offset] == 1:
                if X[offset] < xmin:
                    xargmin = j
                    xmin = X[offset]
                    # break
        for j in range(columns):  # xmax
            offset = (i + 1) * columns - 1 - j
            if flags[offset] == 1:
                if X[offset] > xmax:
                    xargmax = columns - 1 - j
                    xmax = X[offset]
                    # break

    newRowNb = int((ymax - ymin) / resolution[0]) + 2
    newColNb = int((xmax - xmin) / resolution[1]) + 2

    # pre allocate for conveniance
    pointsCoord = []
    flagSum = []
    pointId = []
    for i in range(newRowNb):
        row = []
        pointsCoord.append(row)
        flagRow = []
        flagSum.append(flagRow)
        pointIdRow = []
        pointId.append(pointIdRow)
        for j in range(newColNb):
            pts = [0.0, 0.0, 0.0, 0.0, 0.0]
            row.append(pts)
            flagRow.append(0)
            pointIdRow.append(-1)
    if crossConnection:  # an other grid (n-1)x(n-1) with an offset of 0.5,0.5
        pointsCoordCross = []
        flagSumCross = []
        pointIdCross = []
        for i in range(newRowNb - 1):
            row = []
            pointsCoordCross.append(row)
            flagRow = []
            flagSumCross.append(flagRow)
            pointIdRow = []
            pointIdCross.append(pointIdRow)
            for j in range(newColNb - 1):
                pts = [0.0, 0.0, 0.0, 0.0, 0.0]
                row.append(pts)
                flagRow.append(0)
                pointIdRow.append(-1)

                # Sum the values for each new pixel
    for i in range(rows):
        for j in range(columns):
            offset = i * columns + j
            if flags[offset] != 0:
                newI = int((Y[offset] - ymin) / resolution[0])
                newJ = int((X[offset] - xmin) / resolution[1])
                pointsCoord[newI][newJ][0] += X[offset]
                pointsCoord[newI][newJ][1] += Y[offset]
                pointsCoord[newI][newJ][2] += Z[offset]
                pointsCoord[newI][newJ][3] += j / float(columns)
                pointsCoord[newI][newJ][4] += (rows - 1 - i) / float(rows)

                # how many active pixels of the source belong to the new pixel
                flagSum[newI][newJ] += 1
                if crossConnection:
                    if ((Y[offset] - ymin) > resolution[0] / 2.0
                            and (X[offset] - xmin) > resolution[1] / 2.0
                            and (ymax - Y[offset]) > resolution[0] / 2.0
                            and (xmax - X[offset]) > resolution[1] / 2.0):
                        newI = int((Y[offset] - ymin - resolution[0] / 2.0) / resolution[0])
                        newJ = int((X[offset] - xmin - resolution[1] / 2.0) / resolution[1])

                        pointsCoordCross[newI][newJ][0] += X[offset]
                        pointsCoordCross[newI][newJ][1] += Y[offset]
                        pointsCoordCross[newI][newJ][2] += Z[offset]
                        pointsCoordCross[newI][newJ][3] += j / float(columns)
                        pointsCoordCross[newI][newJ][4] += (rows - 1 - i) / float(rows)

                        # how many active pixels of the source belong to the new pixel
                        flagSumCross[newI][newJ] += 1

else:

    # Compute the reduction
    newRowNb = (rows - 1) / reductionFactor + 1
    newColNb = (columns - 1) / reductionFactor + 1

    # pre allocate for conveniance
    pointsCoord = []
    flagSum = []
    pointId = []
    for i in range(newRowNb):
        row = []
        pointsCoord.append(row)
        flagRow = []
        flagSum.append(flagRow)
        pointIdRow = []
        pointId.append(pointIdRow)
        for j in range(newColNb):
            pts = [0.0, 0.0, 0.0, 0.0, 0.0]  # x,y,z,u,v
            row.append(pts)
            flagRow.append(0)
            pointIdRow.append(-1)
    if crossConnection:  # an other grid (n-1)x(n-1) with an offset of 0.5,0.5
        pointsCoordCross = []
        flagSumCross = []
        pointIdCross = []
        for i in range(newRowNb - 1):
            row = []
            pointsCoordCross.append(row)
            flagRow = []
            flagSumCross.append(flagRow)
            pointIdRow = []
            pointIdCross.append(pointIdRow)
            for j in range(newColNb - 1):
                pts = [0.0, 0.0, 0.0, 0.0, 0.0]
                row.append(pts)
                flagRow.append(0)
                pointIdRow.append(-1)

                # Sum the values for each new pixel
    for i in range(rows):
        newI = i / reductionFactor
        for j in range(columns):
            if flags[i * columns + j] != 0:
                newJ = j / reductionFactor
                pointsCoord[newI][newJ][0] += X[i * columns + j]
                pointsCoord[newI][newJ][1] += Y[i * columns + j]
                pointsCoord[newI][newJ][2] += Z[i * columns + j]
                pointsCoord[newI][newJ][3] += j / float(columns)
                pointsCoord[newI][newJ][4] += (rows - 1 - i) / float(rows)

                # how many active pixels of the source belong to the new pixel
                flagSum[newI][newJ] += 1

    if crossConnection:
        offset = int(reductionFactor / 2)
        for i in range(rows - reductionFactor):
            newI = i / reductionFactor
            for j in range(columns - reductionFactor):
                id = (i + offset) * columns + j + offset
                if flags[id] != 0:
                    newJ = j / reductionFactor
                    pointsCoordCross[newI][newJ][0] += X[id]
                    pointsCoordCross[newI][newJ][1] += Y[id]
                    pointsCoordCross[newI][newJ][2] += Z[id]
                    pointsCoordCross[newI][newJ][3] += (j + offset) / float(columns)
                    pointsCoordCross[newI][newJ][4] += (rows - 1 - i - offset) / float(rows)

                    # how many active pixels of the source belong to the new pixel
                    flagSumCross[newI][newJ] += 1

if spikeRemoval2 != []:
    removedNb = 0
    p = (spikeRemoval2[0] - 1) / 2
    q = (spikeRemoval2[1] - 1) / 2
    for ii in range(newRowNb - 2 * q):
        i = ii + q
        for jj in range(newColNb - 2 * p):
            j = jj + p
            validNb = 0
            awayNb = 0
            sumZ = 0.0
            if flagSum[i + q][j + p] == 0:
                continue
            for a in range(q * 2 + 1):  # local matrix
                for b in range(p * 2 + 1):
                    if a == q and b == p:  # dont count center point
                        continue
                    if flagSum[ii + a][jj + b] == 0:
                        continue
                    validNb += 1
                    # sumZ += pointsCoord[ii+a][jj+b][2]/float(flagSum[ii+a][jj+b]
                    if abs(pointsCoord[ii + a][jj + b][2] / float(flagSum[ii + a][jj + b]) - pointsCoord[i + q][j + p][
                        2] / float(flagSum[i + q][j + p])) > spikeRemoval2[2]:
                        awayNb += 1
            if float(awayNb) > 3 * validNb / 4.0:
                # pointsCoord[i+q][j+p][2] = sumZ/float(validNb)
                flagSum[i + q][j + p] = 0
                removedNb += 1

    # print removedNb

# Divide by the number of values summed for each superpixel
# List the points to keep
points = []
pointsTextureRatio = []
cnt = 1  # OBJ index starts at 1
for i in range(newRowNb):
    for j in range(newColNb):
        if flagSum[i][j] != 0:
            pointsCoord[i][j][0] /= float(flagSum[i][j])
            pointsCoord[i][j][1] /= float(flagSum[i][j])
            pointsCoord[i][j][2] /= float(flagSum[i][j])
            pointsCoord[i][j][3] /= float(flagSum[i][j])
            pointsCoord[i][j][4] /= float(flagSum[i][j])
            points.append(pointsCoord[i][j][0:3])
            pointsTextureRatio.append(pointsCoord[i][j][3:])
            pointId[i][j] = cnt
            cnt = cnt + 1
        if crossConnection:
            if i < newRowNb - 1 and j < newColNb - 1:
                if flagSumCross[i][j] != 0:
                    pointsCoordCross[i][j][0] /= float(flagSumCross[i][j])
                    pointsCoordCross[i][j][1] /= float(flagSumCross[i][j])
                    pointsCoordCross[i][j][2] /= float(flagSumCross[i][j])
                    pointsCoordCross[i][j][3] /= float(flagSumCross[i][j])
                    pointsCoordCross[i][j][4] /= float(flagSumCross[i][j])
                    points.append(pointsCoordCross[i][j][0:3])
                    pointsTextureRatio.append(pointsCoordCross[i][j][3:])
                    pointIdCross[i][j] = cnt
                    cnt = cnt + 1

faces = []

# Construct faces from 4 points (i,j), (i,j+1), (i+1,j) and (i+1,j+1):
#
#  *-*      *-*        *      *        *-*
#  |/|  or  |/   or   /|  or  |\   or   \|
#  *-*      *        *-*      *-*        *
#   4        3        3        3        3   # Number of defined pixel
#
for i in range(newRowNb - 1):
    for j in range(newColNb - 1):
        if not crossConnection or flagSumCross[i][j] == 0:
            # up left triangle
            if (flagSum[i][j] != 0 and
                    flagSum[i + 1][j] != 0 and
                    flagSum[i][j + 1] != 0):
                triangle = [pointId[i][j],
                            pointId[i + 1][j],
                            pointId[i][j + 1]]
                faces.append(triangle)

            # bottom right triangle
            if (flagSum[i + 1][j] != 0 and
                    flagSum[i + 1][j + 1] != 0 and
                    flagSum[i][j + 1] != 0):
                triangle = [pointId[i + 1][j],
                            pointId[i + 1][j + 1],
                            pointId[i][j + 1]]
                faces.append(triangle)

            # up right triangle
            # (only if the lower left pixel is not defined)
            if (flagSum[i + 1][j] == 0 and
                    flagSum[i][j] != 0 and
                    flagSum[i + 1][j] != 0 and
                    flagSum[i + 1][j + 1] != 0):
                triangle = [pointId[i][j],
                            pointId[i + 1][j],
                            pointId[i + 1][j + 1]]
                faces.append(triangle)

                # bottom left triangle
            # (only if the upper right pixel is not defined)
            if (flagSum[i][j + 1] == 0 and
                    flagSum[i][j] != 0 and
                    flagSum[i + 1][j + 1] != 0 and
                    flagSum[i][j + 1] != 0):
                triangle = [pointId[i][j],
                            pointId[i + 1][j + 1],
                            pointId[i][j + 1]]
                faces.append(triangle)

        else:
            # the middle point is defined
            # Construct faces from 4 points (i,j), (i,j+1), (i+1,j) and (i+1,j+1):
            #
            #  *---*      *---*      *                  *
            #  |\ /|  =    \ /   +   |\   +        +   /|
            #  |/*\|        *        |/*      /*\     *\|
            #  *---*                 *       *---*      *
            #
            # left triangle
            if (flagSum[i][j] != 0 and
                    flagSum[i + 1][j] != 0):
                triangle = [pointIdCross[i][j],
                            pointId[i][j],
                            pointId[i + 1][j]]
                faces.append(triangle)

            # right triangle
            if (flagSum[i][j + 1] != 0 and
                    flagSum[i + 1][j + 1] != 0):
                triangle = [pointIdCross[i][j],
                            pointId[i + 1][j + 1],
                            pointId[i][j + 1]]
                faces.append(triangle)

            # bottom triangle
            if (flagSum[i + 1][j] != 0 and
                    flagSum[i + 1][j + 1] != 0):
                triangle = [pointIdCross[i][j],
                            pointId[i + 1][j],
                            pointId[i + 1][j + 1]]
                faces.append(triangle)

                # up triangle
            if (flagSum[i][j] != 0 and
                    flagSum[i][j + 1] != 0):
                triangle = [pointIdCross[i][j],
                            pointId[i][j + 1],
                            pointId[i][j]]
                faces.append(triangle)

# Write the target file
objfile = open(objfilename, "w")
objfile.write("# File type: ASCII OBJ\n")
objfile.write("# Generated from " + os.path.basename(args[0]))
if resolution != []:
    objfile.write(" with a resolution " + string.join(map(str, resolution), "x") + "\n")
else:
    objfile.write(" with a reduction factor of " + str(reductionFactor) + "\n")

for pts in points:
    objfile.write("v " + string.join(map(str, pts), " ") + "\n")

if useTexture:
    for pts in pointsTextureRatio:
        objfile.write("vt " + string.join(map(str, pts), " ") + "\n")
    for f in faces:
        objfile.write("f " + string.join(map(lambda x: str(x) + "/" + str(x), f), " ") + "\n")
else:
    for f in faces:
        objfile.write("f " + string.join(map(str, f), " ") + "\n")

objfile.close()

if tmp != "":
    os.remove(tmp)



