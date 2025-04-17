# Plex Monitor

A Python script to monitor the status of your Plex ecosystem services and report the consolidated status to a Discord webhook. The Discord message is updated periodically instead of posting new messages repeatedly.

## Features

*   Monitors status for:
    *   Plex Media Server - Shows active sessions
    *   Radarr - Shows queue count
    *   Sonarr - Shows queue count
    *   Sabnzbd - Shows download speed and queue size
    *   qBittorrent - Shows download/upload speeds and active torrents
    *   Tautulli - Shows stream count and bandwidth usage
    *   Overseerr - Shows pending request count
*   Sends status updates to a Discord webhook using embeds
*   Updates a single Discord message instead of spamming the channel
*   Configurable update interval
*   Logs activity to `plex_monitor.log`
*   Docker support for easy deployment (including Unraid)

## Prerequisites

*   Python 3.x and `pip` (Python package installer)
*   OR Docker (for containerized deployment)

## Setup

### Option 1: Standard Python Setup

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
    *   Service URLs, API keys, and credentials for each service you want to monitor.

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

5.  **Run the script:**
    ```bash
    python plex_monitor.py # Or use 'py plex_monitor.py' on Windows
    ```

### Option 2: Docker Setup

1.  **Create a directory structure:**
    ```bash
    mkdir -p plex-monitor/config plex-monitor/logs
    cd plex-monitor
    ```

2.  **Create your configuration file:**
    ```bash
    # Download the template
    curl -o config/config.json https://raw.githubusercontent.com/your-username/plex-monitor/main/config.template.json
    # Or manually create it in the config directory
    ```
    Edit `config/config.json` with your service details.

3.  **Run with Docker Compose:**
    ```bash
    # Download the docker-compose.yml file
    curl -o docker-compose.yml https://raw.githubusercontent.com/your-username/plex-monitor/main/docker-compose.yml
    
    # Start the container
    docker-compose up -d
    ```

4.  **Or run with Docker directly:**
    ```bash
    docker run -d \
      --name plex-monitor \
      -v $(pwd)/config:/app/config \
      -v $(pwd)/logs:/app/logs \
      -e TZ=America/New_York \
      --restart unless-stopped \
      ghcr.io/your-username/plex-monitor:latest
    ```

### Unraid Setup

1. Go to the "Docker" tab in your Unraid web UI
2. Click "Add Container"
3. Set the following parameters:
   - Repository: `ghcr.io/your-username/plex-monitor:latest`
   - Name: `plex-monitor`
   - Add Path: `/app/config` mapped to `/mnt/user/appdata/plex-monitor/config`
   - Add Path: `/app/logs` mapped to `/mnt/user/appdata/plex-monitor/logs`
   - Add Variable: `TZ` = `Your/Timezone`

## Configuration (`config.json`)

The `config.json` file holds all the necessary settings:

*   `discord_webhook_url`: **Required**. The URL for your Discord webhook.
*   `update_interval_seconds`: Optional (defaults to 60). The time between status checks.
*   `services`: Contains nested objects for each service with its specific connection details:
    * `plex`: URL and token for your Plex Media Server
    * `radarr`: URL and API key for Radarr
    * `sonarr`: URL and API key for Sonarr
    * `sabnzbd`: URL and API key for SABnzbd
    * `qbittorrent`: URL, username, and password for qBittorrent
    * `tautulli`: URL and API key for Tautulli
    * `overseerr`: URL and API key for Overseerr

**Important:** Keep your `config.json` file secure and do not commit it to version control, as it contains sensitive information. The `.gitignore` file is already configured to prevent this.

## Helper Scripts

Several helper scripts are included to make it easier to work with Plex Monitor:

### setup_config.py

This script helps you create a `config.json` file by guiding you through the configuration process:

```bash
python setup_config.py
```

### update_config.py

This script updates an existing `config.json` file with new options from the template:

```bash
python update_config.py
```

Use this script after updating to a new version of Plex Monitor to ensure your configuration includes any new options or services.

### create_service.py

This script creates a systemd service file for running Plex Monitor as a service on Linux systems:

```bash
python create_service.py
```

Follow the instructions printed by the script to install and start the service.

### run_tests.py

This script runs the unit tests for Plex Monitor:

```bash
python run_tests.py
```

## Testing

Unit tests are provided in the `tests` directory. You can run them using the `run_tests.py` script:

```bash
python run_tests.py
```

Or using pytest directly:

```bash
pytest tests/
```

To run tests with coverage reporting:

```bash
pytest tests/ --cov=plex_monitor
```

## Future Work

*   Add more detailed status information for each service (e.g., specific download names, Plex stream details)
*   Add options for customizing the Discord embed appearance
*   Add support for additional services like Bazarr, Lidarr, Readarr, etc.
*   Implement retry mechanisms for temporary failures
*   Add notification for persistent service failures
