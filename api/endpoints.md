# Websports API Documentation

> [!WARNING]
> This documentation is unofficial and is not affiliated with, endorsed by, or maintained by Websports.
>
> I do not claim ownership of the Websports API. This documentation is the result of my own research into how the Websports front-end communicates with its back-end through the API.
>
> The purpose of this project is purely educational: to understand the API endpoints, the data they provide, and how that data can be accessed and interpreted.

## Game example
This game will be used as an example throughout the document.
```text
https://www.websports.co.za/livecricket.html?gid=263316&sportid=1
```

The `gid` query parameter identifies the game. The `sportid` query parameter identifies the sport; for cricket, this is `1`.

## 1. Common identifiers

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. It can be retrieved from the `gid` query parameter in the fixture URL. |
| `sportID` | `integer` | The sport identifier. Websports supports multiple sports; for cricket, this is always `1`. |
| `teamID` | `integer` | The Websports server ID of a team. It can be obtained from the fixture details response. |
| `commBatTeamIDInn1` | `integer` | The team ID of the team batting in the first innings. |
| `commBatTeamIDInn2` | `integer` | The team ID of the team batting in the second innings. |
| `battingTeamID` | `integer` | The ID of the team currently batting. |
| `inningsID` | `integer` | The innings identifier used by live-match endpoints. |
| `selInningsIDScorecard` | `integer` | The selected innings identifier used by the scorecard endpoints. It is `1` for the limited-overs scorecards covered here. |
| `selWagonWheelInningsID` | `integer` | The selected innings identifier used by the wagon-wheel endpoints. |
| `playerID` | `integer` | The Websports server ID of a player. |
| `selWagonWheelStatsType` | `integer` or `string` | The selected wagon-wheel statistics type. The valid values have not yet been confirmed. |

## 2. Fixture details

Returns the basic details of a fixture, including team identifiers and innings scores.

### Endpoint

```http
GET /api/live/getfixturebysport/{gameID}/sport/{sportID}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game being scored. |
| `sportID` | `integer` | The sport identifier. For cricket, this is always `1`. |

### Example request

```http
GET https://www.websports.co.za/api/live/getfixturebysport/263316/sport/1
```

### Example response

```json
{
  "fixtures": [
    {
      "InningsID": "1",
      "aTeamID": 24,
      "aRuns": 337,
      "aWickets": 7,
      "bTeamID": 25,
      "bRuns": 306,
      "bWickets": 5,
      "isHighlightsVideo": 0,
      "isLiveStreamVL": 0
    }
  ]
}
```

### Relevant fields

| Field | Description |
| :--- | :--- |
| `InningsID` | Innings identifier returned by the fixture. |
| `aTeamID` | Server ID of team A. |
| `aRuns` | Runs scored by team A. |
| `aWickets` | Wickets lost by team A. |
| `bTeamID` | Server ID of team B. |
| `bRuns` | Runs scored by team B. |
| `bWickets` | Wickets lost by team B. |
| `isHighlightsVideo` | Indicates whether a highlights video is available. |
| `isLiveStreamVL` | Indicates whether a live stream is available. |

Use the team IDs from this response when requesting team-specific scorecard data. The fixture response may contain additional fields not shown in this example.

## 3. Innings scorecard

The scorecard endpoints return the batting, extras, bowling, and fall-of-wickets information for a selected team and innings.

For limited-overs cricket, the scorecard innings identifier used in the observed requests is `1`. Other formats may use different innings identifiers.

### 3.1 Batting scorecard

Returns the batting scorecard for a team in the selected fixture innings.

**Endpoint**

```http
GET /api/live/fixture/scorecard/batting/{gameID}/{teamID}/{innings}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `teamID` | `integer` | The server ID of the team. This can be retrieved from the fixture details endpoint. |
| `innings` | `integer` | The innings identifier. For the limited-overs scorecards documented here, this is `1`. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/scorecard/batting/263316/24/1
```

**Example response**

```json
{
  "scorecard": [
    {
      "ServerPlayerID": 114202,
      "PlayerName": "Jason",
      "PlayerSurname": "Roy",
      "BattingNr": 1,
      "WicketTaker": "Kuldeep Yadav",
      "BatRuns": 66,
      "BatBalls": 57,
      "Fielder": "Ravindra Jadeja",
      "BatFours": 7,
      "BatSixes": 2,
      "JerseyNumber": 0,
      "PlayerNameInitial": "J",
      "HowOutFull": "ct Ravindra Jadeja b Kuldeep Yadav",
      "HowOut": "Caught"
    },
    {
      "ServerPlayerID": 114195,
      "PlayerName": "Jonny",
      "PlayerSurname": "Bairstow",
      "BattingNr": 2,
      "WicketTaker": "Mohammad Shami",
      "BatRuns": 111,
      "BatBalls": 109,
      "Fielder": "Rishabh Pant",
      "BatFours": 10,
      "BatSixes": 6,
      "JerseyNumber": 0,
      "PlayerNameInitial": "J",
      "HowOutFull": "ct Rishabh Pant b Mohammad Shami",
      "HowOut": "Caught"
    }
  ]
}
```

### 3.2 Extras

Returns the extras recorded for a team's innings.

**Endpoint**

```http
GET /api/live/fixture/scorecard/extras/{gameID}/{teamID}/{innings}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `teamID` | `integer` | The server ID of the batting team. |
| `innings` | `integer` | The selected scorecard innings identifier. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/scorecard/extras/263316/24/1
```

**Example response**
```json
{
  "extras": [
    {
      "Extras": 8,
      "NoBalls": 0,
      "WideBalls": 4,
      "Byes": 2,
      "LegByes": 2
    }
  ]
}
```

### 3.3 Bowling scorecard

Returns the bowling figures for the selected innings.

**Endpoint**

```http
GET /api/live/fixture/scorecard/bowling/{gameID}/{teamID}/{innings}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `teamID` | `integer` | The server team ID used for the bowling scorecard request. |
| `innings` | `integer` | The selected scorecard innings identifier. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/scorecard/bowling/263316/24/1
```

**Example response**
```json
{
  "scorecard": [
    {
      "ServerPlayerID": 114205,
      "PlayerName": "Chris",
      "PlayerSurname": "Woakes",
      "BowlNr": 1,
      "OversBowled": 10,
      "MaidensBowled": 3,
      "RunsAgainst": 58,
      "Wickets": 2,
      "NoBalls": 0,
      "Wides": 0,
      "TotalBowlerBalls": 60,
      "JerseyNumber": 0
    },
    {
      "ServerPlayerID": 114194,
      "PlayerName": "Jofra",
      "PlayerSurname": "Archer",
      "BowlNr": 2,
      "OversBowled": 10,
      "MaidensBowled": 0,
      "RunsAgainst": 45,
      "Wickets": 0,
      "NoBalls": 0,
      "Wides": 0,
      "TotalBowlerBalls": 60,
      "JerseyNumber": 0
    }
  ]
}
```

### 3.4 Fall of wickets (FOW)

Returns the fall-of-wickets information for the selected innings.

**Endpoint**

```http
GET /api/live/fixture/scorecard/fownew/{gameID}/{teamID}/{innings}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `teamID` | `integer` | The server ID of the batting team. |
| `innings` | `integer` | The selected scorecard innings identifier. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/scorecard/fownew/263316/24/1
```

**Example response**
```json
{
  "fow": [
    {
      "GameID": "263316",
      "EventID": 135,
      "PlayerName": "Jason",
      "PlayerSurname": "Roy",
      "TeamTotalRuns": 160,
      "TeamTotalWickets": 1
    },
    {
      "GameID": "263316",
      "EventID": 193,
      "PlayerName": "Jonny",
      "PlayerSurname": "Bairstow",
      "TeamTotalRuns": 205,
      "TeamTotalWickets": 2
    }
  ]
}
```

## 4. Live innings data

These endpoints provide information about the current state of a match. They are particularly useful when building a live score display.

### 4.1 Current bowlers

Returns the bowler information for the selected innings.

**Endpoint**

```http
GET /api/live/fixture/bowlers/{gameID}/{inningsID}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `inningsID` | `integer` | The innings identifier. This is normally `1` in the observed requests, but may differ in time cricket. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/bowlers/263316/1
```

**Example response**
```json
{
  "fow": [
    {
      "GameID": "263316",
      "EventID": 135,
      "PlayerName": "Jason",
      "PlayerSurname": "Roy",
      "TeamTotalRuns": 160,
      "TeamTotalWickets": 1
    },
    {
      "GameID": "263316",
      "EventID": 193,
      "PlayerName": "Jonny",
      "PlayerSurname": "Bairstow",
      "TeamTotalRuns": 205,
      "TeamTotalWickets": 2
    }
  ]
}
```

### 4.2 Current batsmen

Returns the batsmen for the team currently batting in the selected innings.

**Endpoint**

```http
GET /api/live/fixture/batsmen/{gameID}/{battingTeamID}/{inningsID}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `battingTeamID` | `integer` | The server ID of the team currently batting. |
| `inningsID` | `integer` | The innings identifier. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/batsmen/263316/24/1
```

**Example response**
```json
{
  "batsmen": [
    {
      "GameID": "263316",
      "InningsID": 1,
      "TeamID": 25,
      "Team": "India",
      "BattingNr": 7,
      "PlayerID": 605,
      "ServerPlayerID": 114213,
      "PlayerName": "Kedar",
      "PlayerSurname": "Jadhav",
      "BatRuns": 12,
      "BatBalls": 13,
      "BatMins": 23,
      "BatFours": 1,
      "BatSixes": 0,
      "HowOut": "Not Out",
      "WicketTaker": "",
      "BowlNr": 0,
      "OversBowled": 0,
      "TotalBowlerBalls": 0,
      "MaidensBowled": 0,
      "RunsAgainst": 0,
      "Wickets": 0,
      "NoBalls": 0,
      "Wides": 0,
      "PlayerIndicator": "Batsman1",
      "CurrentPlayer": "OnStrike",
      "BattingHandID": 1,
      "BowlingHandID": 1,
      "BowlingActionID": 5,
      "PSServerTeamID": 0,
      "JerseyNumber": 0
    }
  ]
}
```

### 4.3 Ball countdown

Returns the ball-countdown information for the selected team and innings.

**Endpoint**

```http
GET /api/live/fixture/ballcountdown/{gameID}/{teamID}/{inningsID}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `gameID` | `integer` | The ID of the game. |
| `teamID` | `integer` | The relevant team identifier. Confirm whether this is the batting or fielding team for each request. |
| `inningsID` | `integer` | The innings identifier. |

**Example request**

```http
GET https://www.websports.co.za/api/live/fixture/ballcountdown/263316/24/1
```

**Example response**
```json
{
  "ballcountdown": [
    {
      "EventID": 304,
      "Over": "49.6",
      "BallDescription": "1"
    },
    {
      "EventID": 303,
      "Over": "49.5",
      "BallDescription": "0"
    },
    {
      "EventID": 302,
      "Over": "49.4",
      "BallDescription": "W"
    }
  ]
}
```

## 5. Endpoint reference

| Feature | Endpoint |
| :--- | :--- |
| Fixture details | `/api/live/getfixturebysport/{gameID}/sport/{sportID}` |
| Batting scorecard | `/api/live/fixture/scorecard/batting/{gameID}/{teamID}/{innings}` |
| Extras | `/api/live/fixture/scorecard/extras/{gameID}/{teamID}/{innings}` |
| Bowling scorecard | `/api/live/fixture/scorecard/bowling/{gameID}/{teamID}/{innings}` |
| Fall of wickets | `/api/live/fixture/scorecard/fownew/{gameID}/{teamID}/{innings}` |
| Current bowlers | `/api/live/fixture/bowlers/{gameID}/{inningsID}` |
| Current batsmen | `/api/live/fixture/batsmen/{gameID}/{battingTeamID}/{inningsID}` |
| Ball countdown | `/api/live/fixture/ballcountdown/{gameID}/{teamID}/{inningsID}` |

## 6. Suggested request flow
The data flow used in **websports-match-viewer**.
1. Extract `gameID` from the `gid` parameter in the fixture URL.
2. Request fixture details using `getfixturebysport`.
3. Read the team IDs from the fixture response and identify the batting team for the innings being requested.
4. Request the batting, extras, bowling, and fall-of-wickets scorecard endpoints.
5. For live match information, request the current batsmen, current bowlers, and ball-countdown endpoints.

**The exact sequence may vary depending on the match state and which identifiers are already available in the front-end.**

## 7. Further investigation
The following details still need to be confirmed by inspecting additional requests and responses:

- Exact fields and coordinate system used by the wagon-wheel endpoints.
