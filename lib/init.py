import os
import json
from colorama import init, Fore
from threading import Thread

init(autoreset=True)

def load_assets(path: str = ""):
    """
    Charger toutes les assets présentes dans le dossier assets/
    """
    assets = []

    for element in os.listdir(f"{path}/assets/"):
        for element2 in os.listdir(f"{path}/assets/{element}"):
            assets.append(f"""
@app.route('/assets/{element}/{element2}')
def file{len(assets)}():
    return send_file(r'{path}\\assets\\{element}\\{element2}')
    """)
            

    for element in os.listdir(f"{path}/apps/"):
        with open(f"{path}/apps/{element}/app.json", "r", encoding="utf-8") as f:
            app_name = json.loads(f.read())["name"]
            f.close()
        assets.append(f"""
@app.route('/apps/{app_name}/images/logo.png')
def file{len(assets)}():
    return send_file(r'{path}\\apps\\{element}\\images\\logo.png')
    """)
        if os.path.exists(f"{path}/apps/{element}/images/background.png"):
            assets.append(f"""
@app.route('/apps/{app_name}/images/background.png')
def file{len(assets)}():
    return send_file(r'{path}\\apps\\{element}\\images\\background.png')
""")

    with open("flask_assets", "a", encoding="utf-8") as f:
        for element in assets:
            f.write(element)
        f.close()

    with open("flask_assets", "r", encoding="utf-8") as f:
        data = f.read()
        f.close()
    os.remove("flask_assets")
    del assets

    return data

def load_settings(path: str =""):
    """
    Charger les paramètres de homeHub
    """
    with open(f"{path}/config/settings.json") as f:
        settings = json.loads(f.read())
        f.close()

    return settings