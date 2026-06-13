with open("final_game_database_with_managers.json", "rb") as f:
    data = f.read()

# Search for the string "1. FC K" in binary
idx = data.find(b"1. FC K")
if idx != -1:
    # Print 20 bytes after
    print("Bytes at 1. FC K:", data[idx:idx+20])

# Search for "Union Berlin" in binary
idx = data.find(b"Union Berlin")
if idx != -1:
    # Print 30 bytes before
    print("Bytes before Union Berlin:", data[max(0, idx-25):idx+15])
