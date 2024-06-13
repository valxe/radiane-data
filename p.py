import os
import json

def process_top_json(file_path):
    cache = set()
    
    with open(file_path, 'r') as f:
        top_data = json.load(f)
        
    # List to keep track of usernames to remove from top_data
    usernames_to_remove = []
    
    for username, amount in top_data.items():
        if amount == 1:
            # Save username in cache
            cache.add(username)
            # Delete username.json if exists
            user_json_path = os.path.join('data', 'users', f'{username}.json')
            if os.path.exists(user_json_path):
                os.remove(user_json_path)
                print(f"Deleted {user_json_path}")
            # Mark username for removal from top_data
            usernames_to_remove.append(username)
    
    # Remove usernames from top_data
    for username in usernames_to_remove:
        del top_data[username]
    
    # Save updated top_data back to top.json
    with open(file_path, 'w') as f:
        json.dump(top_data, f, indent=4)
    
    # Optionally, you might want to save the cache to a file or do something else with it
    # For simplicity, let's print the cached usernames
    print("Cached usernames:", cache)

if __name__ == "__main__":
    top_json_path = 'data/top.json'
    process_top_json(top_json_path)