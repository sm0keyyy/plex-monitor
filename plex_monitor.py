import json
import requests
import time
import logging
import os

# --- Configuration ---
CONFIG_FILE = 'config.json'
LOG_FILE = 'plex_monitor.log'

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# --- Global Variables ---
discord_message_id = None

# --- Helper Functions ---
def load_config():
    """Loads configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"Configuration file '{CONFIG_FILE}' not found.")
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Basic validation (can be expanded)
        if not config.get('discord_webhook_url') or 'YOUR_DISCORD_WEBHOOK_URL_HERE' in config.get('discord_webhook_url'):
             logging.warning("Discord webhook URL is missing or not configured in config.json.")
             # Allow script to run but Discord functionality will fail
        return config
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from '{CONFIG_FILE}'.")
        return None
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return None

def get_plex_status(config):
    """Fetches status from Plex (Placeholder)."""
    # TODO: Implement actual Plex API call
    logging.info("Fetching Plex status (Placeholder)...")
    # Example data structure
    return {"status": "Online", "sessions": 0, "error": None}

def get_radarr_status(config):
    """Fetches status from Radarr (Placeholder)."""
    # TODO: Implement actual Radarr API call
    logging.info("Fetching Radarr status (Placeholder)...")
    # Example data structure
    return {"status": "Online", "queue_count": 0, "error": None}

def get_sonarr_status(config):
    """Fetches status from Sonarr (Placeholder)."""
    # TODO: Implement actual Sonarr API call
    logging.info("Fetching Sonarr status (Placeholder)...")
    # Example data structure
    return {"status": "Online", "queue_count": 0, "error": None}

def get_sabnzbd_status(config):
    """Fetches status from Sabnzbd (Placeholder)."""
    # TODO: Implement actual Sabnzbd API call
    logging.info("Fetching Sabnzbd status (Placeholder)...")
    # Example data structure
    return {"status": "Online", "speed": "0 KB/s", "queue_size": "0 B", "error": None}

def get_qbittorrent_status(config):
    """Fetches status from qBittorrent (Placeholder)."""
    # TODO: Implement actual qBittorrent API call
    logging.info("Fetching qBittorrent status (Placeholder)...")
    # Example data structure
    return {"status": "Online", "download_speed": "0 KiB/s", "upload_speed": "0 KiB/s", "active_torrents": 0, "error": None}

def format_discord_message(statuses):
    """Formats the collected statuses into a Discord embed message."""
    logging.info("Formatting Discord message...")
    embed = {
        "title": "Plex Ecosystem Monitor Status",
        "description": f"Last updated: <t:{int(time.time())}:R>", # Relative timestamp
        "color": 0x0099ff, # Blue color
        "fields": [],
        "footer": {
            "text": "Plex Monitor by Roo"
        },
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    }

    service_emojis = {
        "plex": "🎬",
        "radarr": "🎥",
        "sonarr": "📺",
        "sabnzbd": "💾",
        "qbittorrent": "🔄"
    }

    for service, data in statuses.items():
        emoji = service_emojis.get(service, "❓")
        if data.get("error"):
            status_text = f"🔴 Error: {data['error']}"
            value = f"Status: {status_text}"
        elif data.get("status") == "Offline":
            status_text = "Offline"
            value = f"Status: {status_text}"
        else:
            status_text = "Online"
            details = []
            # Add specific details based on service
            if service == "plex":
                details.append(f"Sessions: {data.get('sessions', 'N/A')}")
            elif service == "radarr":
                details.append(f"Queue: {data.get('queue_count', 'N/A')}")
            elif service == "sonarr":
                details.append(f"Queue: {data.get('queue_count', 'N/A')}")
            elif service == "sabnzbd":
                details.append(f"Speed: {data.get('speed', 'N/A')}")
                details.append(f"Queue: {data.get('queue_size', 'N/A')}")
            elif service == "qbittorrent":
                details.append(f"DL: {data.get('download_speed', 'N/A')}")
                details.append(f"UL: {data.get('upload_speed', 'N/A')}")
                details.append(f"Active: {data.get('active_torrents', 'N/A')}")

            value = f"Status:🟢 {status_text}\n" + "\n".join(details)

        embed["fields"].append({
            "name": f"{emoji} {service.capitalize()}",
            "value": value,
            "inline": True # Display fields side-by-side where possible
        })

     # Ensure an even number of fields for better inline display if needed
    if len(embed["fields"]) % 2 != 0 and len(embed["fields"]) > 1 :
         embed["fields"].append({"name": "\u200b", "value": "\u200b", "inline": True}) # Add blank field


    return {"embeds": [embed]}

def send_discord_message(webhook_url, message_data):
    """Sends a new message to the Discord webhook."""
    global discord_message_id
    if not webhook_url or 'YOUR_DISCORD_WEBHOOK_URL_HERE' in webhook_url:
        logging.warning("Discord webhook URL not configured. Skipping message send.")
        return False
    try:
        # Add wait=True to get the message ID back from Discord
        response = requests.post(f"{webhook_url}?wait=true", json=message_data, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        discord_message_id = response_data.get('id')
        if discord_message_id:
            logging.info(f"Initial Discord message sent. Message ID: {discord_message_id}")
            return True
        else:
            logging.error("Failed to get message ID from Discord response.")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending Discord message: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred sending Discord message: {e}")
        return False


def update_discord_message(webhook_url, message_id, message_data):
    """Updates an existing Discord message using its ID."""
    if not webhook_url or 'YOUR_DISCORD_WEBHOOK_URL_HERE' in webhook_url:
        logging.warning("Discord webhook URL not configured. Skipping message update.")
        return False
    if not message_id:
        logging.error("No message ID available to update.")
        return False

    update_url = f"{webhook_url}/messages/{message_id}"
    try:
        response = requests.patch(update_url, json=message_data, timeout=10)
        response.raise_for_status()
        logging.info(f"Discord message {message_id} updated successfully.")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404: # Not Found - Message might have been deleted
             logging.warning(f"Discord message {message_id} not found (404). It might have been deleted. Will attempt to send a new one.")
             return "send_new" # Signal to send a new message
        else:
             logging.error(f"HTTP error updating Discord message {message_id}: {e.response.status_code} - {e.response.text}")
             return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error updating Discord message {message_id}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred updating Discord message {message_id}: {e}")
        return False


# --- Main Loop ---
def main():
    """Main execution function."""
    global discord_message_id
    config = load_config()
    if not config:
        return # Stop if config failed to load

    webhook_url = config.get('discord_webhook_url')
    update_interval = config.get('update_interval_seconds', 60) # Default to 60 seconds

    while True:
        logging.info("--- Starting status check cycle ---")
        statuses = {
            "plex": get_plex_status(config.get('services', {}).get('plex')),
            "radarr": get_radarr_status(config.get('services', {}).get('radarr')),
            "sonarr": get_sonarr_status(config.get('services', {}).get('sonarr')),
            "sabnzbd": get_sabnzbd_status(config.get('services', {}).get('sabnzbd')),
            "qbittorrent": get_qbittorrent_status(config.get('services', {}).get('qbittorrent')),
        }

        message_data = format_discord_message(statuses)

        if discord_message_id:
            logging.info(f"Attempting to update message ID: {discord_message_id}")
            update_status = update_discord_message(webhook_url, discord_message_id, message_data)
            if update_status == "send_new":
                discord_message_id = None # Reset message ID as it's invalid
                logging.info("Previous message not found, attempting to send a new one.")
                send_discord_message(webhook_url, message_data)
            elif not update_status:
                 logging.warning("Failed to update Discord message. Will retry next cycle.")
                 # Optionally: Implement logic to retry sending a new message after several failed updates
        else:
            logging.info("No existing message ID found, sending initial message.")
            send_discord_message(webhook_url, message_data)

        logging.info(f"--- Cycle complete. Waiting for {update_interval} seconds. ---")
        time.sleep(update_interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script interrupted by user. Exiting.")
    except Exception as e:
        logging.exception(f"An unhandled exception occurred: {e}")