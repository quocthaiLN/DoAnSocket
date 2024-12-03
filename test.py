import time

# Lấy thời gian thực dưới dạng timestamp
timestamp = time.time()
print("Timestamp:", timestamp)

# Chuyển thành thời gian định dạng
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
print("Thời gian định dạng:", formatted_time)
