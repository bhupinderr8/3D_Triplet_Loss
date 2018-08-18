import random
import re

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
            print('Found')
            temp.append(random_choice_positive)
            temp.append(random_choice_negative)

        if len(temp) != 3:
            i -= 1
        else:
            address.append(temp)
            # print(temp)
    i+=1

print(address[0][2])