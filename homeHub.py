from flask import Flask, request, send_file, render_template
import json
import os
from lib.init import *
import socket
import threading
import wget
import requests
from lib.notifications import *
import zipfile
import shutil
import sys

path = os.getcwd()
version = 1.0
app = Flask(__name__)
ip = socket.gethostbyname(socket.gethostname())

if not os.path.exists(f"{path}/config"):
    os.mkdir(f"{path}/config")

if not os.path.exists(f"{path}/apps"):
    os.mkdir(f"{path}/apps")

@app.route('/')
def page_home():
    # Charger les paramètres
    settings = load_settings(path)

    with open(f"{path}/templates/home.html", "r", encoding="utf-8") as f:
        page = f.read()
        f.close()

    if settings["disable_weather_on_home"] == False:
        with requests.get("https://ipinfo.io/json") as r:
            ip_infos = json.loads(r.text)
            r.close()

        ip_infos["loc"] = ip_infos["loc"].split(",")

        wget.download(f"https://api.open-meteo.com/v1/forecast?latitude={ip_infos['loc'][0]}&longitude={ip_infos['loc'][1]}&current=temperature_2m,relative_humidity_2m,is_day,wind_speed_10m&timezone=Europe%2FBerlin&forecast_days=1", "weatherhome.json")
    
        with open("weatherhome.json", "r", encoding="utf-8") as f:
            weather = json.loads(f.read())
            f.close()
        
        os.remove("weatherhome.json")

        temp = str(weather["current"]["temperature_2m"])
        vvent = str(weather["current"]["wind_speed_10m"])
        humidite = str(weather["current"]["relative_humidity_2m"])

        if weather["current"]["is_day"] == 0:
            page = page.replace("Bonjour", "Bonsoir")
            page = page.replace("/271/waving-hand_1f44b.png", "/354/crescent-moon_1f319.png")
    else:
        page = page.replace('<input type="checkbox" class="form-check-input" id="disable_weather_on_home" name="disable_weather_on_home">', '<input type="checkbox" class="form-check-input" id="disable_weather_on_home" name="disable_weather_on_home" checked>')
        
        temp = "None"
        vvent = "None"
        humidite = "None"
    
    with open("config/notifications.json", "r", encoding="utf-8") as f:
        notifications = json.loads(f.read())
        f.close()
    
    if len(notifications) > 0:
        page = page.replace("$notifs", f'<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{len(notifications)} <ion-icon name="mail-unread"></ion-icon><span class="visually-hidden">unread messages</span></span>')
        notifs_total = ""
        for notification in notifications.keys():
            if len(notifications[notification]['message']) <= 157:
                notifs_total += f"""
<div class="notification">
    <a href="/notification?name={notification.replace(' ', '+')}"><h4 style="margin-left: 6px;">{notification}</h4></a>
    <p style="margin-left: 6px;"><i>Auteur : {notifications[notification]['author']}</i><br>{notifications[notification]['message']}</p>
</div>
"""
            else:
                notifs_total += f"""
<div class="notification">
    <a href="/notification?name={notification.replace(' ', '+')}"><h4 style="margin-left: 6px;">{notification}</h4></a>
    <p style="margin-left: 6px;"><i>Auteur : {notifications[notification]['author']}</i><br>{notifications[notification]['message'][0:157]} [...]</p>
</div>
"""
        page = page.replace("$notifications", notifs_total)
    else:
        page = page.replace("$notifs", "")
        page = page.replace("$notifications", '<p><ion-icon name="alert-circle"></ion-icon> Aucune notification.</p>')

    apps_total = ""
    rmapps_total = ""

    fd_apps = os.listdir(f"{path}/apps/")
    fd_apps.sort()

    for app in fd_apps:
        with open(f"{path}/apps/{app}/app.json", "r", encoding="utf-8") as f:
            app_info = json.loads(f.read())
            f.close()

        rmapps_total += f'<option value="{app}">{app_info["name"]}</option>\n'
        
        if app_info["colors"]["background_type"] == "color":
            apps_total += f"""
<div class="app" align="center" style="background-color: {app_info['colors']['background']}; color: {app_info['colors']['text']};" onclick="openApp('{ip}:{app_info['port']}', '{app_info['name']}')" title="Ouvrir {app_info['name']}">
    <img src="/apps/{app_info['name']}/images/logo.png" class="app-logo">
    <br/>
    <h4>{app_info['name']}</h4>
</div>
"""
        elif app_info["colors"]["background_type"] == "image":
            apps_total += f"""
<div class="app" align="center" style="background-color: grey; color: {app_info['colors']['text']}; background-image: url('/apps/{app_info['name']}/images/background.png');" onclick="openApp('{ip}:{app_info['port']}', '{app_info['name']}')" title="Ouvrir {app_info['name']}">
    <img src="/apps/{app_info['name']}/images/logo.png" class="app-logo">
    <br/>
    <h4>{app_info['name']}</h4>
</div>
"""

    if settings["theme"] == "dark":
        page = page.replace("color: black;", "color: white;").replace("background-color: white;", "background-color: #1E1E1F;")

    return render_template(
        f"home.html",
        version=str(version),
        temp=temp,
        vvent=vvent,
        humidite=humidite,
        osname=os.name,
        cpucount=str(os.cpu_count()),
        cwd=str(os.getcwd()),
        theme=settings["theme"],
        apps=apps_total,
        rmapps=rmapps_total
    )

@app.route('/settings')
def page_settings():
    return send_file(f"{path}/pages/settings.html")

@app.route('/notification', methods=["GET"])
def page_notification():
    with open(f"{path}/pages/notification.html", "r", encoding="utf-8") as f:
        page = f.read()
        f.close()
    with open(f"{path}/config/notifications.json", "r", encoding="utf-8") as f:
        notifications = json.loads(f.read())
        f.close()
    name = request.args.get("name").replace("+", " ")
    if name in notifications:
        page = page.replace("$title", name)
        page = page.replace("$message", notifications[name]["message"])
        page = page.replace("$author", notifications[name]["author"])
        page = page.replace("$version", str(version))
        return page
    
@app.route('/removeNotification', methods=["GET"])
def removeNotification():
    with open(f"{path}/config/notifications.json", "r", encoding="utf-8") as f:
        notifications = json.loads(f.read())
        f.close()
    name = request.args.get("name").replace("+", " ").replace("%20", " ")
    if name in notifications:
        del notifications[name]
        with open(f"{path}/config/notifications.json", "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=4)
            f.close()
    return 'Done'

@app.route('/removeAllNotification', methods=["GET"])
def removeAllNotification():
    with open(f"{path}/config/notifications.json", "r", encoding="utf-8") as f:
        notifications = json.loads(f.read())
        f.close()
    if len(notifications) > 0:
        with open(f"{path}/config/notifications.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
            f.close()
    return 'Done'

@app.route('/applySettings', methods=["GET"])
def applySettings():
    if os.path.exists(f"{path}/config/settings.json"):
        settings = {
            "theme": request.args.get("theme")
        }
        if request.args.get("disable_weather_on_home") == None:
            settings["disable_weather_on_home"] = False
        else:
            settings["disable_weather_on_home"] = True

        with open(f"{path}/config/settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
            f.close()

        return '<script>window.location.href = "/";</script>'
    else:
        return 'Error'
    
@app.route('/installApp', methods=["GET"])
def installApp():
    if request.args.get("link") != None:
        if request.args.get("link").startswith("https://github.com/"):
            repo = {}
            with requests.get(f"https://api.github.com/repos/{request.args.get('link').replace('https://github.com/', '')}/contents") as r:
                repo["content"] = json.loads(r.text)
                r.close()
            repo["content1"] = []
            for element in repo["content"]:
                repo["content1"].append(element["name"])
            if "app.json" in repo["content1"]:
                if not request.args.get('link').replace('https://github.com/', '').split("/")[1].replace("/", "") in os.listdir(f"{path}/apps/"):
                    a_apps = os.listdir(f"{path}/apps/")
                    wget.download(f"https://github.com/{request.args.get('link').replace('https://github.com/', '')}/archive/refs/heads/main.zip", "repo.zip")

                    with zipfile.ZipFile(f"{path}/repo.zip", 'r') as zip_ref:
                        zip_ref.extractall(f"{path}/apps/")

                    os.remove(f"{path}/repo.zip")

                    n_apps = os.listdir(f"{path}/apps/")
                    for e in a_apps:
                        if e in n_apps:
                            a_apps.remove(e)
                    del a_apps
                    n_apps = n_apps[0]
                    # os.rename(f"{path}/apps/{n_apps}", f"{path}/apps/{n_apps[0:len(n_apps[0])-6]}")

                    for fd in os.listdir(f"{path}/apps/"):
                        if fd.endswith("-main"):
                            os.rename(f"{path}/apps/{fd}", f"{path}/apps/{fd.replace("-main", "")}")

                    if os.name == "nt":
                        threading._start_new_thread(os.system, (f'python -u "{path}/apps/{n_apps[0:len(n_apps[0])-6]}/app.py"',))
                    else:
                        threading._start_new_thread(os.system, (f'python3 -u "{path}/apps/{n_apps[0:len(n_apps[0])-6]}/app.py"',))

                    return '<script>alert("L\'application a bien été installée. Pour finaliser l\'installation, veuillez redémarrer."); window.location.href = "/";</script>'
                else:
                    return '<script>alert("Cette application est déjà installée."); window.location.href = "/";</script>'
            else:
                return '<script>alert("Ce dépôt n\'est pas une application homeHub."); window.location.href = "/";</script>'
        else:
            return '<script>alert("Application invalide."); window.location.href = "/";</script>'
    else:
        return '<script>alert("Application invalide."); window.location.href = "/";</script>'
    
@app.route('/removeApp', methods=["GET"])
def removeApp():
    if request.args.get("app") != None:
        if request.args.get("app") in os.listdir(f"{path}/apps/"):
            shutil.rmtree(f"{path}/apps/{request.args.get("app")}")
            return '<script>alert("Application désinstallée."); window.location.href = "/";</script>'
        else:
            return '<script>alert("Application invalide."); window.location.href = "/";</script>'
    else:
        return '<script>alert("Application invalide."); window.location.href = "/";</script>'
    
# @app.route('/restart', methods=["GET"])
# def restart():
#     if os.name == "nt":
#         threading._start_new_thread(os.system, (f'python -u "{path}/scripts/restart.py"',))
#         threading._start_new_thread(os.system, (f'exit',))
#     else:
#         threading._start_new_thread(os.system, (f'python3 -u "{path}/scripts/restart.py"',))
#         threading._start_new_thread(os.system, (f'exit',))
#     return "Redémarrage"


# Charger les assets
exec(load_assets(path))

for app1 in os.listdir(f"{path}/apps/"):
    print(Fore.BLUE + f"[i] Lancement de l'application {app1}")
    if os.name == "nt":
        threading._start_new_thread(os.system, (f'python -u "{path}/apps/{app1}/app.py"',))
    else:
        threading._start_new_thread(os.system, (f'python3 -u "{path}/apps/{app1}/app.py"',))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, threaded=True)