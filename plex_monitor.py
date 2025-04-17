import json
import requests
import time
import logging
import os
from plexapi.server import PlexServer
from plexapi.exceptions import NotFound, Unauthorized
from pyarr import RadarrAPI, SonarrAPI
from requests.exceptions import ConnectionError as ReqConnectionError, HTTPError
import qbittorrentapi
from qbittorrentapi.exceptions import APIConnectionError, LoginFailed, APIError

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
    """Fetches status from Plex using plexapi."""
    if not config:
        logging.warning("Plex configuration missing in config.json")
        return {"status": "Offline", "sessions": "N/A", "error": "Config missing"}

    baseurl = config.get('url')
    token = config.get('token')

    if not baseurl or not token or 'YOUR_PLEX_' in baseurl or 'YOUR_PLEX_' in token:
        logging.warning("Plex URL or Token is missing or not configured in config.json")
        return {"status": "Offline", "sessions": "N/A", "error": "URL/Token missing"}

    logging.info(f"Attempting to connect to Plex: {baseurl}")
    try:
        # Set a timeout for the connection attempt
        session = requests.Session()
        session.verify = False # Consider security implications if not using HTTPS or valid certs
        plex = PlexServer(baseurl, token, session=session, timeout=10)
        sessions = plex.sessions()
        session_count = len(sessions)
        logging.info(f"Plex connection successful. Active sessions: {session_count}")
        return {"status": "Online", "sessions": session_count, "error": None}
    except Unauthorized:
        logging.error("Plex connection failed: Unauthorized (Invalid Token?).")
        return {"status": "Error", "sessions": "N/A", "error": "Unauthorized"}
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        logging.error(f"Plex connection failed: Could not connect to {baseurl}.")
        return {"status": "Offline", "sessions": "N/A", "error": "Connection failed"}
    except NotFound:
         logging.error(f"Plex connection failed: Server not found at {baseurl} (404).")
         return {"status": "Offline", "sessions": "N/A", "error": "Not Found (404)"}
    except Exception as e:
        logging.exception(f"An unexpected error occurred connecting to Plex: {e}")
        return {"status": "Error", "sessions": "N/A", "error": f"Unexpected: {type(e).__name__}"}

def get_radarr_status(config):
    """Fetches status from Radarr using pyarr."""
    if not config:
        logging.warning("Radarr configuration missing in config.json")
        return {"status": "Offline", "queue_count": "N/A", "error": "Config missing"}

    host_url = config.get('url')
    api_key = config.get('api_key')

    if not host_url or not api_key or 'YOUR_RADARR_' in host_url or 'YOUR_RADARR_' in api_key:
        logging.warning("Radarr URL or API Key is missing or not configured in config.json")
        return {"status": "Offline", "queue_count": "N/A", "error": "URL/API Key missing"}

    logging.info(f"Attempting to connect to Radarr: {host_url}")
    try:
        radarr = RadarrAPI(host_url, api_key, timeout=10)
        # Verify connection by getting system status (optional but good)
        radarr.get_system_status()
        # Get queue information
        queue = radarr.get_queue()
        queue_count = len(queue.get('records', [])) if isinstance(queue, dict) else 0 # pyarr v3+ returns dict
        # Alternative for older pyarr versions if needed:
        # queue = radarr.get_queue()
        # queue_count = len(queue) if isinstance(queue, list) else 0

        logging.info(f"Radarr connection successful. Queue count: {queue_count}")
        return {"status": "Online", "queue_count": queue_count, "error": None}
    except ReqConnectionError:
        logging.error(f"Radarr connection failed: Could not connect to {host_url}.")
        return {"status": "Offline", "queue_count": "N/A", "error": "Connection failed"}
    except HTTPError as e:
        if e.response.status_code == 401:
             logging.error("Radarr connection failed: Unauthorized (Invalid API Key?).")
             return {"status": "Error", "queue_count": "N/A", "error": "Unauthorized"}
        else:
             logging.error(f"Radarr connection failed: HTTP Error {e.response.status_code}")
             return {"status": "Error", "queue_count": "N/A", "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        logging.exception(f"An unexpected error occurred connecting to Radarr: {e}")
        return {"status": "Error", "queue_count": "N/A", "error": f"Unexpected: {type(e).__name__}"}

def get_sonarr_status(config):
    """Fetches status from Sonarr using pyarr."""
    if not config:
        logging.warning("Sonarr configuration missing in config.json")
        return {"status": "Offline", "queue_count": "N/A", "error": "Config missing"}

    host_url = config.get('url')
    api_key = config.get('api_key')

    if not host_url or not api_key or 'YOUR_SONARR_' in host_url or 'YOUR_SONARR_' in api_key:
        logging.warning("Sonarr URL or API Key is missing or not configured in config.json")
        return {"status": "Offline", "queue_count": "N/A", "error": "URL/API Key missing"}

    logging.info(f"Attempting to connect to Sonarr: {host_url}")
    try:
        sonarr = SonarrAPI(host_url, api_key, timeout=10)
        # Verify connection by getting system status (optional but good)
        sonarr.get_system_status()
        # Get queue information
        queue = sonarr.get_queue()
        queue_count = len(queue.get('records', [])) if isinstance(queue, dict) else 0 # pyarr v3+ returns dict
        # Alternative for older pyarr versions if needed:
        # queue = sonarr.get_queue()
        # queue_count = len(queue) if isinstance(queue, list) else 0

        logging.info(f"Sonarr connection successful. Queue count: {queue_count}")
        return {"status": "Online", "queue_count": queue_count, "error": None}
    except ReqConnectionError:
        logging.error(f"Sonarr connection failed: Could not connect to {host_url}.")
        return {"status": "Offline", "queue_count": "N/A", "error": "Connection failed"}
    except HTTPError as e:
        if e.response.status_code == 401:
             logging.error("Sonarr connection failed: Unauthorized (Invalid API Key?).")
             return {"status": "Error", "queue_count": "N/A", "error": "Unauthorized"}
        else:
             logging.error(f"Sonarr connection failed: HTTP Error {e.response.status_code}")
             return {"status": "Error", "queue_count": "N/A", "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        logging.exception(f"An unexpected error occurred connecting to Sonarr: {e}")
        return {"status": "Error", "queue_count": "N/A", "error": f"Unexpected: {type(e).__name__}"}

def get_sabnzbd_status(config):
    """Fetches status from Sabnzbd using its JSON API."""
    if not config:
        logging.warning("Sabnzbd configuration missing in config.json")
        return {"status": "Offline", "speed": "N/A", "queue_size": "N/A", "error": "Config missing"}

    base_url = config.get('url')
    api_key = config.get('api_key')

    if not base_url or not api_key or 'YOUR_SABNZBD_' in base_url or 'YOUR_SABNZBD_' in api_key:
        logging.warning("Sabnzbd URL or API Key is missing or not configured in config.json")
        return {"status": "Offline", "speed": "N/A", "queue_size": "N/A", "error": "URL/API Key missing"}

    # Ensure base_url doesn't end with a slash for proper joining
    if base_url.endswith('/'):
        base_url = base_url[:-1]

    api_url = f"{base_url}/sabnzbd/api"
    params = {
        "mode": "queue",
        "output": "json",
        "apikey": api_key
    }

    logging.info(f"Attempting to connect to Sabnzbd: {base_url}")
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        try:
            data = response.json()
        except json.JSONDecodeError:
             # Sabnzbd might return HTML on auth failure instead of a clean JSON error
             logging.error("Sabnzbd connection failed: Invalid response (Not JSON). Check URL and API Key.")
             return {"status": "Error", "speed": "N/A", "queue_size": "N/A", "error": "Invalid Response/API Key?"}


        if "error" in data: # Check for API-level errors (e.g., {'error': 'API Key Incorrect'})
             error_msg = data.get("error", "Unknown API Error")
             logging.error(f"Sabnzbd API error: {error_msg}")
             # Attempt to determine if it's an auth error
             if "api key" in error_msg.lower():
                 return {"status": "Error", "speed": "N/A", "queue_size": "N/A", "error": "Unauthorized"}
             else:
                 return {"status": "Error", "speed": "N/A", "queue_size": "N/A", "error": f"API Error: {error_msg[:30]}"} # Truncate long errors


        queue_data = data.get('queue', {})
        speed_kbps = float(queue_data.get('kbpersec', 0))
        size_mb = float(queue_data.get('mb', 0)) # Total size in MB

        # Format speed
        if speed_kbps < 1024:
            speed_str = f"{speed_kbps:.1f} KB/s"
        else:
            speed_str = f"{speed_kbps / 1024:.1f} MB/s"

        # Format size
        if size_mb < 1024:
             size_str = f"{size_mb:.1f} MB"
        else:
             size_str = f"{size_mb / 1024:.1f} GB"


        logging.info(f"Sabnzbd connection successful. Speed: {speed_str}, Queue Size: {size_str}")
        return {"status": "Online", "speed": speed_str, "queue_size": size_str, "error": None}

    except ReqConnectionError:
        logging.error(f"Sabnzbd connection failed: Could not connect to {base_url}.")
        return {"status": "Offline", "speed": "N/A", "queue_size": "N/A", "error": "Connection failed"}
    except requests.exceptions.Timeout:
         logging.error(f"Sabnzbd connection failed: Timeout connecting to {base_url}.")
         return {"status": "Offline", "speed": "N/A", "queue_size": "N/A", "error": "Timeout"}
    except requests.exceptions.HTTPError as e:
         # Handle potential auth errors that might return 403 Forbidden
         if e.response.status_code == 403:
              logging.error("Sabnzbd connection failed: Forbidden (403). Check API Key and permissions.")
              return {"status": "Error", "speed": "N/A", "queue_size": "N/A", "error": "Forbidden (403)"}
         else:
              logging.error(f"Sabnzbd connection failed: HTTP Error {e.response.status_code}")
              return {"status": "Error", "speed": "N/A", "queue_size": "N/A", "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        logging.exception(f"An unexpected error occurred connecting to Sabnzbd: {e}")
        return {"status": "Error", "speed": "N/A", "queue_size": "N/A", "error": f"Unexpected: {type(e).__name__}"}

def get_qbittorrent_status(config):
    """Fetches status from qBittorrent using qbittorrent-api."""
    if not config:
        logging.warning("qBittorrent configuration missing in config.json")
        return {"status": "Offline", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": "Config missing"}

    host_url = config.get('url')
    username = config.get('username')
    password = config.get('password')

    # Basic check if config seems default/missing
    if not host_url or 'YOUR_QBITTORRENT_' in host_url:
         logging.warning("qBittorrent URL is missing or not configured in config.json")
         return {"status": "Offline", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": "URL missing"}
    # Username/Password can be optional for some setups, but warn if default
    if 'YOUR_QBITTORRENT_' in username or 'YOUR_QBITTORRENT_' in password:
         logging.warning("qBittorrent username or password might not be configured (using defaults).")
         # Allow connection attempt, might work without auth depending on qBit setup

    logging.info(f"Attempting to connect to qBittorrent: {host_url}")
    client = qbittorrentapi.Client(
        host=host_url,
        username=username if 'YOUR_QBITTORRENT_' not in username else None, # Pass None if default
        password=password if 'YOUR_QBITTORRENT_' not in password else None, # Pass None if default
        REQUESTS_ARGS={'timeout': (10, 10)} # connect timeout, read timeout
    )

    try:
        client.auth_log_in()
        logging.info("qBittorrent login successful.")

        # Get global transfer info for speeds
        transfer_info = client.transfer_info()
        dl_speed_bytes = transfer_info.get('dl_info_speed', 0)
        ul_speed_bytes = transfer_info.get('up_info_speed', 0)

        # Get torrent list to count active ones (downloading or seeding)
        torrents = client.torrents_info(status_filter='active') # Filters: all, downloading, seeding, completed, paused, active, inactive, resumed
        active_count = len(torrents)

        # Format speeds (convert B/s to KiB/s or MiB/s)
        def format_speed(speed_bytes):
            if speed_bytes < 1024:
                return f"{speed_bytes} B/s"
            elif speed_bytes < 1024 * 1024:
                return f"{speed_bytes / 1024:.1f} KiB/s"
            else:
                return f"{speed_bytes / (1024 * 1024):.1f} MiB/s"

        dl_speed_str = format_speed(dl_speed_bytes)
        ul_speed_str = format_speed(ul_speed_bytes)

        logging.info(f"qBittorrent status fetched. DL: {dl_speed_str}, UL: {ul_speed_str}, Active: {active_count}")
        return {
            "status": "Online",
            "download_speed": dl_speed_str,
            "upload_speed": ul_speed_str,
            "active_torrents": active_count,
            "error": None
        }

    except LoginFailed:
        logging.error("qBittorrent connection failed: Login Failed (Incorrect username/password?).")
        return {"status": "Error", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": "Login Failed"}
    except APIConnectionError:
        logging.error(f"qBittorrent connection failed: Could not connect to {host_url}.")
        return {"status": "Offline", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": "Connection failed"}
    except APIError as e:
         logging.error(f"qBittorrent API error: {e.description} (Code: {e.code})")
         return {"status": "Error", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": f"API Error {e.code}"}
    except Exception as e:
        # Catch potential timeouts specifically if possible (depends on underlying requests exceptions)
        if isinstance(e, requests.exceptions.Timeout):
             logging.error(f"qBittorrent connection failed: Timeout connecting to {host_url}.")
             return {"status": "Offline", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": "Timeout"}
        logging.exception(f"An unexpected error occurred connecting to qBittorrent: {e}")
        return {"status": "Error", "download_speed": "N/A", "upload_speed": "N/A", "active_torrents": "N/A", "error": f"Unexpected: {type(e).__name__}"}
    finally:
        # Ensure logout happens even if errors occur after login
        try:
            if client.is_logged_in:
                client.auth_log_out()
                logging.debug("qBittorrent logout successful.")
        except Exception as logout_e:
            logging.warning(f"Error during qBittorrent logout: {logout_e}")

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