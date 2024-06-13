import os
import json

users_dir = os.path.join('data', 'users')

def reformat_user_file(user_file_path):
    with open(user_file_path, 'r') as file:
        data = json.load(file)

    if not isinstance(data, list):
        return

    reformatted_data = {
        "user_pfp": None,
        "messages": []
    }

    for entry in data:
        if 'user_pfp' in entry:
            if not reformatted_data["user_pfp"]:
                reformatted_data["user_pfp"] = entry["user_pfp"]
        else:
            reformatted_data["messages"].append(entry)

    if not reformatted_data["user_pfp"]:
        reformatted_data["user_pfp"] = None

    with open(user_file_path, 'w') as file:
        json.dump(reformatted_data, file, indent=4)

def reformat_all_user_files():
    for filename in os.listdir(users_dir):
        if filename.endswith('.json'):
            user_file_path = os.path.join(users_dir, filename)
            reformat_user_file(user_file_path)
            print(f'Reformatted {user_file_path}')

if __name__ == '__main__':
    reformat_all_user_files()