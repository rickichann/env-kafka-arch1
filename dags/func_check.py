import time
import logging

curr_time = time.time()
curr_time2 = time.time()


print(curr_time)
print(curr_time2)

while True:
    if time.time() > curr_time + 60:
        break
    try:
        print("Always run") 

    except Exception as e:
        logging.error(f'An error occured: {e}')
        continue



