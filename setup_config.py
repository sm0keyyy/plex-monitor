#!/usr/bin/env python3
"""
Setup script for Plex Monitor.
This script creates a config.json file from the template and guides the user through the configuration process.
"""

import json
import os
import sys
import shutil

def setup_config():
    """Create a config.json file from the template and guide the user through the configuration process."""
    # Check if config.json already exists
    if os.path.exists('config.json'):
        overwrite = input("config.json already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup cancelled.")
            return 1
    
    # Check if config.template.json exists
    if not os.path.exists('config.template.json'):
        print("Error: config.template.json not found.")
        return 1
    
    # Load the template
    try:
        with open('config.template.json', 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("Error: config.template.json is not valid JSON.")
        return 1
    except Exception as e:
        print(f"Error loading config.template.json: {e}")
        return 1
    
    # Guide the user through the configuration process
    print("\n=== Plex Monitor Configuration Setup ===\n")
    
    # Discord webhook URL
    webhook_url = input("Enter your Discord webhook URL: ")
    if webhook_url:
        config['discord_webhook_url'] = webhook_url
    
    # Update interval
    update_interval = input("Enter update interval in seconds (default: 60): ")
    if update_interval and update_interval.isdigit():
        config['update_interval_seconds'] = int(update_interval)
    
    # Services
    print("\n=== Service Configuration ===")
    print("For each service, enter the required information or leave blank to skip.")
    
    # Plex
    print("\n--- Plex ---")
    plex_url = input("Plex URL (e.g., http://localhost:32400): ")
    plex_token = input("Plex token: ")
    if plex_url and plex_token:
        config['services']['plex'] = {
            'url': plex_url,
            'token': plex_token
        }
    
    # Radarr
    print("\n--- Radarr ---")
    radarr_url = input("Radarr URL (e.g., http://localhost:7878): ")
    radarr_api_key = input("Radarr API key: ")
    if radarr_url and radarr_api_key:
        config['services']['radarr'] = {
            'url': radarr_url,
            'api_key': radarr_api_key
        }
    
    # Sonarr
    print("\n--- Sonarr ---")
    sonarr_url = input("Sonarr URL (e.g., http://localhost:8989): ")
    sonarr_api_key = input("Sonarr API key: ")
    if sonarr_url and sonarr_api_key:
        config['services']['sonarr'] = {
            'url': sonarr_url,
            'api_key': sonarr_api_key
        }
    
    # Sabnzbd
    print("\n--- Sabnzbd ---")
    sabnzbd_url = input("Sabnzbd URL (e.g., http://localhost:8080): ")
    sabnzbd_api_key = input("Sabnzbd API key: ")
    if sabnzbd_url and sabnzbd_api_key:
        config['services']['sabnzbd'] = {
            'url': sabnzbd_url,
            'api_key': sabnzbd_api_key
        }
    
    # qBittorrent
    print("\n--- qBittorrent ---")
    qbittorrent_url = input("qBittorrent URL (e.g., http://localhost:8080): ")
    qbittorrent_username = input("qBittorrent username: ")
    qbittorrent_password = input("qBittorrent password: ")
    if qbittorrent_url:
        config['services']['qbittorrent'] = {
            'url': qbittorrent_url,
            'username': qbittorrent_username,
            'password': qbittorrent_password
        }
    
    # Tautulli
    print("\n--- Tautulli ---")
    tautulli_url = input("Tautulli URL (e.g., http://localhost:8181): ")
    tautulli_api_key = input("Tautulli API key: ")
    if tautulli_url and tautulli_api_key:
        config['services']['tautulli'] = {
            'url': tautulli_url,
            'api_key': tautulli_api_key
        }
    
    # Overseerr
    print("\n--- Overseerr ---")
    overseerr_url = input("Overseerr URL (e.g., http://localhost:5055): ")
    overseerr_api_key = input("Overseerr API key: ")
    if overseerr_url and overseerr_api_key:
        config['services']['overseerr'] = {
            'url': overseerr_url,
            'api_key': overseerr_api_key
        }
    
    # Save the config
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("\nConfiguration saved to config.json")
        return 0
    except Exception as e:
        print(f"Error saving config.json: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(setup_config())
