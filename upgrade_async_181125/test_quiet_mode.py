quiet_mode_counter_dict = {"client":0}
client = "楊老闆"
client2 = "華納"
print(quiet_mode_counter_dict)
if client not in quiet_mode_counter_dict:
    quiet_mode_counter_dict[client] = 0
print(quiet_mode_counter_dict)
if client in quiet_mode_counter_dict:
    quiet_count = quiet_mode_counter_dict[client]
print(quiet_count)

