import getpass
from config import daemon_timer


user = getpass.getuser()

service = f"""[Unit]
Description=Aurora daemon service

[Service]
Type=oneshot
ExecStart=/usr/bin/python /home/{user}/Aurora/daemon.py """

timer = f"""[Unit]
Description=Run Aurora package counter every 10 minutes

[Timer]
OnBootSec=0s
OnUnitActiveSec={str(daemon_timer)}s

[Install]
WantedBy=timers.target

 """


greeting = f"""Hello {user}! I’m Aurora your personal system assistant. Let’s get things running."""


