# Websports Match Viewer

A Python-based cricket match viewer that retrieves match data from [Websports](https://www.websports.co.za).

The project interacts with undocumented Websports endpoints to retrieve and process match data, making it accessible for use in other applications.

## Overview
Since the Websports API isn't publicly documented, I wanted to satisfy my curiosity by exploring whether I could access the endpoints the platform communicates with.

This project is the result of that exploration, with the aim of making the retrieved data accessible on other places.

## Features
It's currently only limited to a match viewer by entering a game ID or match link, but many potential features are in the works.

Many existing websports features could be rewritten by a third party (like the PDF match summary, which is currently broken) to potentially improve it.

## How it works
1. The game ID is pulled from the link you provide
2. A background thread requests all the details from the API
3. The API response data are turned into valuable information
4. Result is handed back to the UI thread through a queue and screen updates

All the network processes happens off the main thread, so the window stays responsive even when the connection is slow.

## Tech Stack
- **Python 3.9+**
- **CustomTkinter** - for the modern interface using tkinter
- **Requests** - for communication to Websports endpoints
- **Pillow** - for loading and resizing team logos
- **threading**, **queue**, and **concurrent.futures** - for background fetching without freezing the UI

## Getting started
Install all the dependencies:
```
    pip install -r requirements.txt
```

Run the app
```
    python main.py
```

Paste any match link from Websports such as `https://www.websports.co.za/livecricket.html?gid=263316&sportid=1` or the game ID alone (such as `263316`).

> [!WARNING]
> **This is an independent, unofficial project and is not in any way affiliated with, endorsed by, or officially connected to Websports and Cobitech.**
> This project uses undocumented endpoints observed through the Websports website. These endpoints may change or become unavailable without notice. 
> The project does not claim ownership of Websports' data or content.