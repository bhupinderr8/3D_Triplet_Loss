import random
import re
import numpy as np


with open('voxel_file_list.txt') as f:
    list = f.read().splitlines()

address = []
i=0
while i < len(list):
    temp = []
    current = re.search(r'[0-9][0-9][0-9]', list[i])
    if current is not None:
        temp.append(list[i])
        current_id = current.group()
        random_choice_positive = random.choice(list)
        random_choice_negative = random.choice(list)
        if re.search(current_id, random_choice_positive) is not None and re.search(current_id, random_choice_negative) is None:
            # print('Found')
            temp.append(random_choice_positive)
            temp.append(random_choice_negative)

        if len(temp) != 3:
            i -= 1
        else:
            address.append(temp)
            # print(temp)
    i+=1


def getBinaryVoxel(file, size=32):
    print(file)
    x_voxel = np.loadtxt(file).astype(np.int64)
    print('shape of voxel:  ', x_voxel.shape)
    [x_min, y_min, z_min] = np.amin(x_voxel, axis=0)
    [x_max, y_max, z_max] = np.amax(x_voxel, axis=0)

    for i in range(x_voxel.shape[0]):
        x_voxel[i][0] = (size-1) * (x_voxel[i][0] - x_min) / (x_max - x_min)
        x_voxel[i][1] = (size-1) * (x_voxel[i][1] - y_min) / (y_max - y_min)
        x_voxel[i][2] = (size-1) * (x_voxel[i][2] - z_min) / (z_max - z_min)

    voxel_binary = np.zeros(shape=(size, size, size))

    [x_min, y_min, z_min] = np.amin(x_voxel, axis=0)
    [x_max, y_max, z_max] = np.amax(x_voxel, axis=0)

    for i in range(x_voxel.shape[0]):
        voxel_binary[int(x_voxel[i][0]) + abs(x_min)][int(x_voxel[i][1]) + abs(y_min)][int(x_voxel[i][2]) + abs(z_min)] = 1

    return voxel_binary

X_Data=[]

for l in address:
    temp = np.asanyarray([getBinaryVoxel(l[0]), getBinaryVoxel(l[1]), getBinaryVoxel(l[2])])
    X_Data.append(temp)
    print(len(X_Data))

np.save('X_Data',np.asanyarray(X_Data))
print(np.asanyarray(X_Data).shape)