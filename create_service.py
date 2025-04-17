#!/usr/bin/env python3
"""
Script to create a systemd service file for Plex Monitor.
This script creates a systemd service file that can be used to run Plex Monitor as a service on Linux systems.
"""

import os
import sys
import getpass

def create_service_file():
    """Create a systemd service file for Plex Monitor."""
    # Get the current user
    user = getpass.getuser()
    
    # Get the current working directory
    cwd = os.path.abspath(os.path.dirname(__file__))
    
    # Get the path to the Python executable
    python_path = sys.executable
    
    # Create the service file content
    service_content = f"""[Unit]
Description=Plex Monitor Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={cwd}
ExecStart={python_path} {os.path.join(cwd, 'plex_monitor.py')}
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=plex-monitor

[Install]
WantedBy=multi-user.target
"""
    
    # Write the service file
    service_file_path = os.path.join(cwd, 'plex-monitor.service')
    try:
        with open(service_file_path, 'w') as f:
            f.write(service_content)
        print(f"Service file created at: {service_file_path}")
        
        # Print instructions
        print("\nTo install the service:")
        print(f"1. Copy the service file to /etc/systemd/system/:")
        print(f"   sudo cp {service_file_path} /etc/systemd/system/")
        print("2. Reload systemd:")
        print("   sudo systemctl daemon-reload")
        print("3. Enable the service to start at boot:")
        print("   sudo systemctl enable plex-monitor.service")
        print("4. Start the service:")
        print("   sudo systemctl start plex-monitor.service")
        print("5. Check the status:")
        print("   sudo systemctl status plex-monitor.service")
        
        return 0
    except Exception as e:
        print(f"Error creating service file: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(create_service_file())
