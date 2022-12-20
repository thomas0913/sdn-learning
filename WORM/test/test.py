import os

list_dir = os.listdir("/Users/USER/Desktop/weak_point")
fd = os.open("/Users/USER/Desktop/weak_point/worm.py", os.O_RDONLY)

result = os.read(fd, 100)

print(result)

os.close(fd)