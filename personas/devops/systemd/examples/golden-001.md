# Systemd Response
## Example Output
```
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=appuser
Group=appgroup
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/.venv/bin/python app.py
Restart=on-failure
RestartSec=5
StartLimitBurst=3
StartLimitIntervalSec=60

# Environment
EnvironmentFile=/opt/myapp/.env
Environment=PYTHONUNBUFFERED=1

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

[Install]
WantedBy=multi-user.target
```
