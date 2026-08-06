import json

FILE = 'user_info.json'

def load_user_info():
    """Load user_info from json file. Return {} if file not find."""
    try:
        with open(FILE) as file: # 'with' closes the file without the need of file.close() command
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_info(user_info):
    """Save user_info on json file."""
    with open(FILE, 'w') as file: # open FILE
        json.dump(user_info, file) # Dumps the new info in it