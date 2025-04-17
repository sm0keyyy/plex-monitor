#!/usr/bin/env python3
"""
Update script for Plex Monitor.
This script updates an existing config.json file with new options from the template.
"""

import json
import os
import sys
import shutil
from datetime import datetime

def update_config():
    """Update an existing config.json file with new options from the template."""
    # Check if config.json exists
    if not os.path.exists('config.json'):
        print("Error: config.json not found. Please run setup_config.py to create a new config file.")
        return 1
    
    # Check if config.template.json exists
    if not os.path.exists('config.template.json'):
        print("Error: config.template.json not found.")
        return 1
    
    # Load the existing config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON.")
        return 1
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return 1
    
    # Load the template
    try:
        with open('config.template.json', 'r') as f:
            template = json.load(f)
    except json.JSONDecodeError:
        print("Error: config.template.json is not valid JSON.")
        return 1
    except Exception as e:
        print(f"Error loading config.template.json: {e}")
        return 1
    
    # Create a backup of the existing config
    backup_file = f"config.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    try:
        shutil.copy('config.json', backup_file)
        print(f"Backup created: {backup_file}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Update the config with new options from the template
    updated = False
    
    # Check for new top-level options
    for key, value in template.items():
        if key not in config:
            config[key] = value
            print(f"Added new option: {key}")
            updated = True
    
    # Check for new services
    if 'services' in template and 'services' in config:
        for service, service_config in template['services'].items():
            if service not in config['services']:
                print(f"Added new service: {service}")
                config['services'][service] = service_config
                updated = True
            else:
                # Check for new options in existing services
                for option, option_value in service_config.items():
                    if option not in config['services'][service]:
                        print(f"Added new option to {service}: {option}")
                        config['services'][service][option] = option_value
                        updated = True
    
    # Save the updated config
    if updated:
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print("\nConfiguration updated successfully.")
            return 0
        except Exception as e:
            print(f"Error saving config.json: {e}")
            return 1
    else:
        print("\nNo updates needed. Your configuration is already up to date.")
        return 0

if __name__ == '__main__':
    sys.exit(update_config())
