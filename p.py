import os
import json

def process_top_json(file_path):
    cache = set()
    
    with open(file_path, 'r') as f:
        top_data = json.load(f)
        

    usernames_to_remove = []
    
    for username, amount in top_data.items():
        if amount == 1:
            cache.add(username)
            user_json_path = os.path.join('data', 'users', f'{username}.json')
            if os.path.exists(user_json_path):
                os.remove(user_json_path)
                print(f"Deleted {user_json_path}")
            usernames_to_remove.append(username)

    for username in usernames_to_remove:
        del top_data[username]

    with open(file_path, 'w') as f:
        json.dump(top_data, f, indent=4)

    print("Cached usernames:", cache)

if __name__ == "__main__":
    top_json_path = 'data/top.json'
    process_top_json(top_json_path)