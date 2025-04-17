# Plex Monitor

A Python script to monitor the status of your Plex ecosystem services (Plex, Radarr, Sonarr, Sabnzbd, qBittorrent) and report the consolidated status to a Discord webhook. The Discord message is updated periodically instead of posting new messages repeatedly.

## Features

*   Monitors status for:
    *   Plex Media Server
    *   Radarr
    *   Sonarr
    *   Sabnzbd
    *   qBittorrent
*   Sends status updates to a Discord webhook using embeds.
*   Updates a single Discord message instead of spamming the channel.
*   Configurable update interval.
*   Logs activity to `plex_monitor.log`.

## Prerequisites

*   Python 3.x
*   `pip` (Python package installer)

## Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd plex-monitor
    ```

2.  **Create your configuration file:**
    Copy the template file:
    ```bash
    # Windows
    copy config.template.json config.json
    # macOS / Linux
    cp config.template.json config.json
    ```
    Edit `config.json` and fill in your actual details:
    *   `discord_webhook_url`: Your Discord channel's webhook URL.
    *   `update_interval_seconds`: How often (in seconds) to check statuses and update Discord.
    *   Service URLs, API keys, and credentials for Plex, Radarr, Sonarr, Sabnzbd, and qBittorrent.

3.  **Set up a Python virtual environment (recommended):**
    ```bash
    # Create the environment
    python -m venv venv  # Or use 'py -m venv venv' on Windows

    # Activate the environment
    # Windows (cmd.exe)
    venv\Scripts\activate
    # Windows (PowerShell)
    venv\Scripts\Activate.ps1
    # macOS / Linux
    source venv/bin/activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt # Or use 'py -m pip install ...' on Windows
    ```

## Running the Script

Make sure your virtual environment is activated. Then run:

```bash
python plex_monitor.py # Or use 'py plex_monitor.py' on Windows
```

The script will start running in the foreground, logging output to the console and `plex_monitor.log`. You can stop it by pressing `Ctrl+C`.

## Configuration (`config.json`)

The `config.json` file holds all the necessary settings:

*   `discord_webhook_url`: **Required**. The URL for your Discord webhook.
*   `update_interval_seconds`: Optional (defaults to 60). The time between status checks.
*   `services`: Contains nested objects for each service with its specific connection details (URL, API keys/tokens, username/password). Fill in the details for the services you want to monitor.

**Important:** Keep your `config.json` file secure and do not commit it to version control, as it contains sensitive information. The `.gitignore` file is already configured to prevent this.

## Future Work

*   Add more detailed status information for each service (e.g., specific download names, Plex stream details).
*   Improve error handling and reporting granularity.
*   Add Dockerfile for containerization.
*   Consider adding support for other related services (e.g., Tautulli, Overseerr).
*   Add options for customizing the Discord embed appearance.