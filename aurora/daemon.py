from aurora.functions import get_distro
from aurora.config.paths import state_path

def check_updates():
    distro = get_distro()
    updateable_packages = distro.check_updates()
    with open(state_path, "w") as f:
        f.write(updateable_packages)
    
    
def create_list():
    distro = get_distro()
    updates_list = distro.get_pkg_list()
    with open("/tmp/update-list.txt", "w") as f:
        for item in updates_list:
            f.write(item)
            f.write("\n")

if __name__ == "__main__":
    check_updates()
    create_list()
