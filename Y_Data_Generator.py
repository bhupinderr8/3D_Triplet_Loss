import re
import numpy as np


with open('voxel_file_list.txt') as f:
    list = f.read().splitlines()

address = []

for l in list:
    current=re.search(r'[0-9][0-9][0-9]', l)
    if current != None:
        address.append(current.group())
        print(current.group())


# for saving output values
Y_Data = np.asanyarray(address)
np.save('Y_Data', Y_Data)
print(Y_Data.shape)
