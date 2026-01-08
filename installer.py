import subprocess
from strings import service, timer, greeting
from functions import say, write, terminal, bash
from pathlib import Path
from time import sleep
import random

say(greeting)

say("Alright. Let’s set this up properly before you hurt yourself.")
# creating the aurora.service file
with open("./aurora.service", "w") as f:
    terminal("creating aurora.service...")
    sleep(random.uniform(0.5, 5))
    f.write(service)
    terminal("aurora.service created.")
# Creating the aurora.timer file
with open("./aurora.timer", "w") as f:
    terminal("creating aurora.timer...")
    sleep(random.uniform(0.5, 5))
    f.write(timer)
    terminal("aurora.timer created.")

say("Service and timer files are ready. Try to keep up.")

service = Path("/etc/systemd/system/aurora.service")
timer = Path("/etc/systemd/system/aurora.timer")


# Checking for existing service and timer files and removing them if they exist
if service.exists():
    say("Existing service detected. I’ll clean that up.")
    write("sudo rm /etc/systemd/system/aurora.service")
    try:
        terminal("removing existing aurora.service...")
        subprocess.run(["sudo", "rm", "/etc/systemd/system/aurora.service"])
        sleep(random.uniform(0.5, 5))
        terminal("aurora.service removed.")
    except Exception as err:
        terminal("Task failed.")
        terminal(f"Error: {err}")

if timer.exists():
    say("Existing timer detected. Same fate.")
    write("sudo rm /etc/systemd/system/aurora.timer")
    try:
        terminal("removing existing aurora.timer...")
        subprocess.run(["sudo", "rm", "/etc/systemd/system/aurora.timer"])
        sleep(random.uniform(0.5, 5))
        terminal("aurora.timer removed.")
    except Exception as err:
        terminal("Task failed.")
        terminal(f"Error: {err}")

say("Old files cleared. As expected.")

base_dir = Path(__file__).resolve().parent

say("Now we put the new pieces where they belong.")

if not service.exists() or not timer.exists():
    say("Installing systemd service.")
    write(f"sudo ln -s {base_dir}/aurora.service /etc/systemd/system/")
    terminal("installing aurora.service...")
    sleep(random.uniform(0.5, 5))
    try:
        subprocess.run(["sudo", "ln", "-s", f"{base_dir}/aurora.service", "/etc/systemd/system/"])
        terminal("aurora.service installed.")
    except Exception as err:
        terminal("Installation failed.")
        terminal(f"Error: {err}")

    say("Installing systemd timer.")
    write(f"sudo ln -s {base_dir}/aurora.timer /etc/systemd/system/")
    terminal("installing aurora.timer...")
    sleep(random.uniform(0.5, 5))
    try:
        subprocess.run(["sudo", "ln", "-s", f"{base_dir}/aurora.timer", "/etc/systemd/system/"])
        terminal("aurora.timer installed.")
    except Exception as err:
        terminal("Installation failed.")
        terminal(f"Error: {err}")

    say("Refreshing systemd. It likes to be told when things change.")
    say("I’ll need your password for this part. Don’t worry, I’m not interested in it.")
    write("systemctl daemon-reload")
    if subprocess.run(["systemctl", "daemon-reload"]).returncode != 0:
        say("systemd did not cooperate.")

    say("Activating Aurora.")
    say("This part needs your password. Blame permissions, not me.")
    write("systemctl enable --now aurora.timer")
    if subprocess.run(["systemctl", "enable", "--now", "aurora.timer"]).returncode != 0:
        say("Activation failed.")

say("Good. Everything is running.")

say("One last thing. Want Aurora available automatically in your terminal? (y/n)")

valid_responses = ["y", "n"]
while True:
    inpt = input("> ").strip().lower()
    if inpt in valid_responses:
        if inpt == "y":
            bash()
        break
    else:
        say("Focus. It’s a yes or a no.")
say("That’s it. I’m in place now. I’ll take it from here—try not to make my job harder.")
