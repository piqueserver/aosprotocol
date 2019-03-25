## Connection

This protocol is used to measure the connection delay (latency/ping) between your local computer and a server.

You will need to measure the actual time difference yourself:

```
ping = dt/2
```

Open up a raw UDP connection to the server's port, and send a packet.

## Packets

There are only two groups of packets, no packet id precedes the actual data.

## Table of Contents
* [Ping start](#ping-start)
* [Ping acknowledge](#ping-acknowledge)
* [Ping LAN](#ping-lan)
* [LAN Info](#lan-info)

## Ping start
*Client->Server*

After server recieved this packet, a ping acknowledge is sent back immediately.

| Length  | Value   | Field Type   | Notes                                  |
| ------- | ------- | ------------ | -------------------------------------- |
| 5 bytes | `HELLO` | CP437 String | fixed length, never send anything more |

## Ping acknowledge
*Server->Client*

| Length  | Value | Field Type   | Notes        |
| ------- | ----- | ------------ | ------------ |
| 2 bytes | `HI`  | CP437 String | fixed length |

## Ping LAN

*Client->Server*

Server replies with a LAN Info Packet

| Length  | Value      | Field Type   | Notes                                  |
| ------- | ---------- | ------------ | -------------------------------------- |
| 8 bytes | `HELLOLAN` | CP437 String | fixed length, never send anything more |

## LAN Info

*Server->Client*

| Length   | Example    | Field Type   | Notes               |
| -------- | ---------- | ------------ | ------------------- |
| variable | See below  | CP437 String | JSON formatted data |

| Param              | Notes                  |
| ------------------ | ---------------------- |
| `name`             | server name            |
| `players_current`  | player count           |
| `players_max`      | server slots           |
| `map`              | map name               |
| `game_mode`        | game mode abbreviation |
| `game_version`     | voxlap version         |


This is what piqueserver sends as of writing (an example):
```JSON
{
	"name": "piqueserver instance",
	"players_current": 5,
	"players_max": 32,
	"map": "classicgen",
	"game_mode": "ctf",
	"game_version": "0.75"
}
```
