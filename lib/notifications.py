import json

def new_notification(path: str = "", title: str = None, message: str = None, author: str = "homeHub"):
    """
    Créer une nouvelle notification
    """
    with open(f"{path}/config/notifications.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        f.close()

    if not title in data:
        data[title] = {
            "message": message,
            "author": author
        }

        with open(f"{path}/config/notifications.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            f.close()