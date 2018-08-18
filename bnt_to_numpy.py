import numpy as np
import bnt_reader
import os

with open('bnt_list.txt') as f:
    list = f.read().splitlines()
min=999999
i=0
final_array=[]
print(len(list))
for file in list:
    if not file == '':
        current_file = bnt_reader.create(file)
        r=current_file.shape
        min = min if min < r[1] else r[1]
        i+=1
        print(min)
        print(i)
        final_array.append(current_file)
        np.save(file, np.asanyarray(np.asanyarray(current_file)))