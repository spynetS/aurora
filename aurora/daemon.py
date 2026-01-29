import subprocess
from functions import get_distro
from config.paths import *

def check_updates():
    distro = get_distro()
    updateable_packages = distro.check_updates()
    with open(log_path, "w") as f:
        f.write(updateable_packages)

if __name__ == "__main__":
    check_updates()
