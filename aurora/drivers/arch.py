from .driver import Driver
import subprocess
from aurora.strings import pacman_hook
from aurora.config.paths import pacman_hook_path

class Archlinux(Driver):

    FLAGGED_PACKAGES: dict[str, dict[str, str]] = {
    # ===== Kernel / boot chain =====
    "linux": {"risk": "high", "category": "kernel"},
    "linux-lts": {"risk": "high", "category": "kernel"},
    "linux-zen": {"risk": "high", "category": "kernel"},
    "linux-hardened": {"risk": "high", "category": "kernel"},

    "linux-firmware": {"risk": "high", "category": "boot"},
    "mkinitcpio": {"risk": "high", "category": "boot"},
    "dracut": {"risk": "high", "category": "boot"},  # if used instead of mkinitcpio
    "intel-ucode": {"risk": "high", "category": "boot"},
    "amd-ucode": {"risk": "high", "category": "boot"},

    # Bootloaders / boot management
    "grub": {"risk": "high", "category": "bootloader"},
    "efibootmgr": {"risk": "low", "category": "bootloader"},
    "refind": {"risk": "medium", "category": "bootloader"},   # optional but common
    "limine": {"risk": "medium", "category": "bootloader"},   # optional but common

    # ===== Core userspace / init / system plumbing =====
    "systemd": {"risk": "high", "category": "core"},
    "systemd-libs": {"risk": "high", "category": "core"},
    "systemd-sysvcompat": {"risk": "medium", "category": "core"},  # compatibility layer

    "dbus": {"risk": "high", "category": "core"},
    "util-linux": {"risk": "high", "category": "core"},
    "coreutils": {"risk": "medium", "category": "core"},
    "bash": {"risk": "medium", "category": "core"},
    "filesystem": {"risk": "high", "category": "core"},
    "procps-ng": {"risk": "medium", "category": "core"},
    "shadow": {"risk": "medium", "category": "core"},
    "sudo": {"risk": "medium", "category": "core"},

    # ===== Core C/C++ runtime =====
    "glibc": {"risk": "critical", "category": "core-lib"},
    "gcc-libs": {"risk": "high", "category": "core-lib"},
    "llvm-libs": {"risk": "medium", "category": "core-lib"},  # important if you depend on LLVM stacks

    # ===== Crypto / trust store =====
    "openssl": {"risk": "medium", "category": "crypto"},
    "gnutls": {"risk": "medium", "category": "crypto"},
    "ca-certificates": {"risk": "medium", "category": "trust"},
    "ca-certificates-utils": {"risk": "medium", "category": "trust"},

    # ===== Package manager / keys / signature trust =====
    "pacman": {"risk": "high", "category": "package-manager"},
    "archlinux-keyring": {"risk": "high", "category": "package-manager"},
    "gnupg": {"risk": "high", "category": "package-manager"},  # signature verification chain
    "curl": {"risk": "medium", "category": "package-manager"}, # pacman downloads

    # ===== Desktop / graphics stack =====
    "mesa": {"risk": "high", "category": "graphics"},
    "libdrm": {"risk": "high", "category": "graphics"},
    "xorg-server": {"risk": "high", "category": "graphics"},

    "wayland": {"risk": "medium", "category": "graphics"},
    "wlroots": {"risk": "high", "category": "graphics"},

    # GPU drivers (user-impacting; can cause black screen / no GUI)
    "nvidia": {"risk": "high", "category": "graphics"},
    "nvidia-lts": {"risk": "high", "category": "graphics"},
    "nvidia-utils": {"risk": "high", "category": "graphics"},
    "nvidia-settings": {"risk": "medium", "category": "graphics"},

    "xf86-video-amdgpu": {"risk": "medium", "category": "graphics"},
    "xf86-video-intel": {"risk": "medium", "category": "graphics"},

    # ===== Networking baseline =====
    "iproute2": {"risk": "medium", "category": "network"},
    "networkmanager": {"risk": "medium", "category": "network"},
    "wpa_supplicant": {"risk": "medium", "category": "network"},
    "openssh": {"risk": "medium", "category": "network"},

    # ===== Language runtimes =====
    "python": {"risk": "low", "category": "runtime"},
}

    def __init__(self):
        self.dependencies = [
            "python",
            "pacman",
            "systemd",
        ]
    
    def update(self):
        return subprocess.run(["sudo", "pacman", "-Syu", "--noconfirm"])
        

    def check_updates(self):
        result = subprocess.run(["checkupdates"], capture_output=True, text=True)
        if result.returncode == 0 or result.returncode == 2:
            return str(len(result.stdout.splitlines()))
        raise Archlinux.Error()

    def check_dependencies(self, say=lambda x: None , terminal=lambda x:None):
        missing = []

        say("Since you are using arch, my favorite distro btw, I will have to check that you have the right dependencies")
        for item in self.dependencies:
            check = subprocess.run(["pacman", "-Q", item], capture_output=True, text=True)
            if check.returncode == 0:
                terminal(f"[ OK ] {item}")
            else:
                terminal(f"[ FAIL ] {item}")   
                missing.append(item)
                
        if len(missing) > 0:
            for item in missing:
                subprocess.run(["sudo", "pacman", "-S", item], capture_output=True, text=True)

    def install_hook(self, write, MAX_TRIES,say=lambda x: None , terminal=lambda x:None):
        say("One more thing. I’m wiring myself directly into pacman.")
        say("Any time pacman updates itself, I’ll know. Instantly.")
        
        for attempt in range(1, MAX_TRIES + 1):
            terminal("Installing pacman hook...")
            try:
                # Creating pacman hook folder if it doesn't exist
                if not pacman_hook_path.exists():
                    say("Pacman doesn’t have a hook directory yet. That’s fine. I’ll make one.")
                    write("sudo mkdir /etc/pacman.d/hooks")
                    terminal("/etc/pacman.d/hooks path not found")
                    terminal("creating path /etc/pacman.d/hooks")
                    subprocess.run(["sudo", "mkdir", "/etc/pacman.d/hooks"])
                    
                    say("Dropping the hook in place.")
                    write("sudo tee /etc/pacman.d/hooks/aurora-pacman-update.hook")
                    subprocess.run(
                        ["sudo", "tee", "/etc/pacman.d/hooks/aurora-pacman-update.hook"],
                        input=pacman_hook,
                        text=True,
                        stdout=subprocess.DEVNULL,
                        check=True,
                    )
                    
                    terminal("pacman update hook successfully installed")
                    say("Done. Pacman moves — I respond.")
                    break
            except Exception as e:
                terminal(f"Installation failed: {e}")
                say("That didn’t work. I’ll try again.")
                if attempt == MAX_TRIES:
                    raise
    def get_pkg_name(self, update_entry):
        split = update_entry.split(" ")
        return split[0]
    
    def get_pkg_list(self):
        result = subprocess.run(["checkupdates"], capture_output=True, text=True)

        if result.returncode == 0 or result.returncode == 2:
            lines = result.stdout.splitlines()
            names = []
            for entry in lines:
                entry = entry.strip()
                if not entry or entry.startswith("Listing"):
                    continue
                names.append(self.get_pkg_name(entry))
            return names
        raise Archlinux.Error()

