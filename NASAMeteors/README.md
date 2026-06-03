
# NASA Meteorite Proximity Finder 🛰️☄️

A lightweight, high-performance Python utility that connects to a live data stream mirror containing historical NASA meteorite landing profiles. The application calculates the great-circle distance between a reference coordinate (configured by default for the San Antonio, TX region) and thousands of documented global meteorite impacts using the Haversine formula, displaying a clean, real-time proximity dashboard in the terminal.

## Features
* **Live Stream Ingestion:** Dynamically fetches up-to-date coordinate maps using a robust connection interface.
* **Offline Resiliency:** Features an automated fallback data layer to keep the system functional during network interruptions or API downtime.
* **Geospatial Computations:** Employs pure mathematical coordinate unpacking and the Haversine formula to compute geodesic curves across the Earth's radius without heavy external GIS overhead.
* **Clean Terminal Report:** Automatically filters, parses, and sorts the collection to output the top 10 closest landing vectors in a highly readable ASCII matrix.

## Requirements

To run this project locally, you need:
* **Python 3.11** (See installation instructions below)
* **pip** (Python package installer)

The project relies on the following third-party package:
* `requests` — For managing secure HTTP stream connections and processing JSON payloads.

---

## How to Install Python 3.11

If you do not have Python 3.11 installed, choose the method below that matches your operating system:

### 🍏 macOS
The cleanest way to manage Python versions on macOS is via [Homebrew](https://brew.sh/):
```zsh
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"

# Install Python 3.11
brew install python@3.11

# Verify the installation
python3.11 --version
Alternatively, you can download the macOS 64-bit universal2 installer directly from the official Python Downloads Page.

🪟 Windows
Download the installer from the official Python 3.11 Downloads Page.

Run the executable.

CRITICAL: Check the box that says "Add python.exe to PATH" before clicking Install Now.

Verify in PowerShell/Command Prompt: python --version

🐧 Linux (Ubuntu/Debian)
Bash
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
How to Download
Clone the repository directly from GitHub into your local directory space:

Bash
# Clone the repository via HTTPS
git clone [https://github.com/MAOFILHO/NASAMeteors.git](https://github.com/MAOFILHO/NASAMeteors.git)

# Navigate directly into the project workspace
cd NASAMeteors
Local Installation & Execution
Follow these step-by-step instructions to set up your isolated virtual workspace and execute the tracker locally:

1. Initialize a Virtual Environment
Isolate your project dependencies by spinning up a clean virtual environment explicitly targeted to Python 3.11:

Bash
python3.11 -m venv .venv
2. Activate the Environment
Activate the environment context to direct your Python interpreter path correctly:

Bash
# On macOS and Linux (Zsh/Bash):
source .venv/bin/activate

# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1
(Once active, you will see (.venv) prepend your terminal prompt).

3. Install Dependencies
Update your local tracking environment with the required operational binaries:

Bash
pip install requests

4. Execute the Application
Launch the proximity processor to pull live telemetry and display the table:

Bash
python find_meteors.py
Expected Output Structure
Plaintext
🛰️  Connecting to Meteorite Data Stream...
✅ Live data successfully retrieved from mirror!

☄️  Top 10 Closest Meteorites Found:
=======================================================
Index  | Meteorite Name       | Proximity (KM)  
-------------------------------------------------------
1      | Example Meteor A     | 1,245.32 km     
2      | Example Meteor B     | 2,110.87 km     
...
=======================================================
