# Websports API

A Python-based cricket match viewer that retrieves match data from [Websports](https://www.websports.co.za).

The project interacts with undocumented Websports endpoints to retrieve and process match data, making the retrieved data accessible to other applications.

## Overview
Since the Websports API isn't publicly documented, I wanted to satisfy my curiosity by exploring whether I could access the endpoints the platform communicates with.

This project is the result of that exploration, with the aim of making the retrieved data accessible on other places.

## Features
The entire Websports' API is simplified in the `/api` folder, which can be used independently to build other applications that utilise Websports match data.

This repository currently only includes a desktop match viewer as an example of what can be built using the API. However, there are many other possibilities, such as a PDF match summary exporter that could provide an alternative to Websports' existing summary, which lacks visual design and can sometimes be broken.

## How it works
1. The game ID is pulled from the link you provide
2. A background thread requests all the details from the API
3. The API response data are turned into usable match information
4. Result is handed back to the UI thread through a queue and the UI updates

All the network operations happens off the main thread, so the window stays responsive even when the connection is slow.

## Tech Stack
- **Python 3.9+**
- **CustomTkinter** - for the modern interface using tkinter
- **Requests** - for communication to Websports endpoints
- **Pillow** - for loading and resizing team logos
- **threading**, **queue**, and **concurrent.futures** - for background fetching without freezing the UI

## Project Structure
The project is split into two parts. `/api` talks to `websports.co.za`, it is entirely independent and works on its own. `/src` contains the code for the desktop app built on top of it.

> [!NOTE]
> You can view the unofficial documentation for the [Websports](https://www.websports.co.za) API [here](api/endpoints.md).

```
Websports Match Viewer/
├── main.py              # entry point
├── requirements.txt
├── api/
│   ├── __init__.py
│   ├── client.py        # session, base URL, get_json
│   ├── fixture.py       # get_fixture, game ID extraction, live innings detection
│   ├── scorecard.py     # get_batting_scorecard, get_bowling_scorecard, get_extras
│   ├── players.py       # get_current_batsmen, get_current_bowlers
│   └── logos.py         # get_logo
└── src/
    ├── app.py           # app controller: screen switching, polling, threading
    ├── screens.py       # landing screen and match screen
    ├── widgets.py       # reusable widgets (team panel, live card, data table)
    ├── config.py        # refresh interval and theme colours
    └── presenter.py     # turns api data into table rows, scores and status text
```

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
