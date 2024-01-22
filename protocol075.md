This page documents Ace of Spades 0.75, the last fully released version of Ace of Spades classic, and 0.76, the last publically available version of Ace of Spades Classic.

Except where otherwise noted, this document applies to .75, the only
commonly played version.

# Connection

When you connect, you must send a version number as the initial data.

Following that a client needs to send an Existing Player data packet to send
its own name, team etc.

If the client does not send an Existing Player packet first, but any other
packet, then the server closes the connection and seems to temporarily ban the
player.

| Number | AoS version |
|--------|-------------|
| 3      | 0.75        |
| 4      | 0.76        |

Send this magic number as part of the `enet_host_connect(ENetHost, ENetAddress,
channels, int)` function

## Disconnect Reasons

Whenever the connection is closed by the server, there is a reason supplied to
the client in the event's data (event.data).

| Number | Reason                       |
|--------|------------------------------|
| 1      | Banned                       |
| 2      | IP connection limit exceded? |
| 3      | Wrong protocol version       |
| 4      | Server full                  |
| 10     | Kicked                       |

## About Coordinates

In Ace of Spades the up-down axis is Z and it is inverted. This means 63 is
water level and 0 is the highest point on a map.

# Packets

All packets start with an unsigned byte to specify their type, followed by the
data for that type of packet. The size given for each packet below includes
this byte.

## Table of Contents

* [Position Data](#position-data)
* [Orientation Data](#orientation-data)
* [World Update (0.75)](#world-update-075)
* [World Update (0.76)](#world-update-076)
* [Input Data](#input-data)
* [Weapon Input](#weapon-input)
* [Hit Packet](#hit-packet)
* [Set HP](#set-hp)
* [Grenade Packet](#grenade-packet)
* [Set Tool](#set-tool)
* [Set Colour](#set-colour)
* [Existing Player](#existing-player)
* [Short Player Data](#short-player-data)
* [Move Object](#move-object)
* [Create Player](#create-player)
* [Block Action](#block-action)
* [Block Line](#block-line)
* [CTF State](#ctf-state)
* [TC State](#tc-state)
* [State Data](#state-data)
* [Kill Action](#kill-action)
* [Chat Message](#chat-message)
* [Map Start (0.75)](#map-start-075)
* [Map Start (0.76)](#map-start-076)
* [Map Chunk](#map-chunk)
* [Player Left](#player-left)
* [Territory Capture](#territory-capture)
* [Progress Bar](#progress-bar)
* [Intel Capture](#intel-capture)
* [Intel Pickup](#intel-pickup)
* [Intel Drop](#intel-drop)
* [Restock](#restock)
* [Fog Colour](#fog-colour)
* [Weapon Reload](#weapon-reload)
* [Change Team](#change-team)
* [Change Weapon](#change-weapon)
* [Map Cached (0.76)](#map-cached-076)
* [Extra Packets](#extra-packets)
* [Version Handshake Init (EP)](#version-handshake-init-ep)
* [Version Handshake Response (EP)](#version-handshake-response-ep)
* [Version Get (EP)](#version-get-ep)
* [Version Response (EP)](#version-response-ep)
* [Powerthirst Edition](#powerthirst-edition)
* [Map Start (PT)](#map-start-pt)
* [Map Chunk (PT)](#map-chunk-pt)
* [Script Begin (PT)](#script-begin-pt)
* [Script Chunk (PT)](#script-chunk-pt)
* [Script End (PT)](#script-end-pt)
* [Script Call (PT)](#script-call-pt)
* [Script Parameters](#script-parameters)

## Data types

Generally, all fields in the Protocol are Low Endian if not specified.

The following shorthands are used in this document:

| Shorthand    | details                                                 |
| -----------: | ----------                                              |
| Byte         | 8 bits of arbitrary data. Usually accompanied by a note |
| UByte        | Unisgned 8 bit number                                   |
| LE Float     | 32bit IEEE float                                        |
| LE Uint      | 32bit unsigned integer                                  |
| CP437 String | String encoded with CP437. Usually fixed-length.        |

## Position Data
`Client <-> Server`

This packet is used to set the players position.

| ------------: | ---------- |
| Packet ID:    | 0          |
| Total Size:   | 13 bytes   |

|Field Name|Field Type|Example|Notes|
|---------:|----------|-------|-----|
|        X | LE Float |  `0`  |     |
|        Y | LE Float |  `0`  |     |
|        Z | LE Float |  `0`  |     |

## Orientation Data
This packet is used to set the players orientation.

| -----------: |----------|
| Packet ID    | 1        |
| Total Size:  | 13 bytes |

#### Fields

|Field Name|Field Type|Example|Notes|
|---------:|----------|-------|-----|
|        X | LE Float |  `0`  |     |
|        Y | LE Float |  `0`  |     |
|        Z | LE Float |  `0`  |     |

## World Update (0.75)
Updates position and orientation of all players.
Depending on the server implementation, the size may be fixed at 32 players or dynamic based on the greatest player
ID, or even based on which players have moved since last update (although this may not work well with Voxlap).
"Slots" which are not occupied by a connected player should be zeroed-out (position: [0,0,0], orientation:
[0,0,0]).

| ----------: | ------------------ |
| Packet ID   | 2                  |
| Total Size: | 1+24*players bytes |

#### Fields

| Field Name                         | Field Type                        | Example | Notes                    |
|------------------------------------|-----------------------------------|---------|--------------------------|
| players positions and orientations | Array[32] of Player Position Data |         | See below table for data |

#### 'Player Position Data'

| ----------: | -------- |
| Total Size: | 24 bytes |

#### Fields

| Field Name    | Field Type | Example | Notes             |
|---------------|------------|---------|-------------------|
| X position    | LE Float   | `0`     | 0 for non-players |
| Y position    | LE Float   | `0`     | 0 for non-players |
| Z position    | LE Float   | `0`     | 0 for non-players |
| X orientation | LE Float   | `0`     | 0 for non-players |
| Y orientation | LE Float   | `0`     | 0 for non-players |
| Z orientation | LE Float   | `0`     | 0 for non-players |

## World Update (0.76)
Updates position and orientation of all players. Unlike 0.75, this only sends
information for the necessary players.

| -----------: | ------------------ |
| Packet ID    | 2                  |
| Total Size:  | 1+25*players bytes |

#### Fields

| Field Name                        | Field Type                                     | Example | Notes                    |
|-----------------------------------|------------------------------------------------|---------|--------------------------|
| Player positions and orientations | Array[] of Player Position Data, variable size |         | See below table for data |

#### 'Player Position Data'

|------------:|----------|
| Total Size: | 25 bytes |

#### Fields

| Field Name    | Field Type | Example | Notes |
|---------------|------------|---------|-------|
| Player ID     | UByte      | `0`     |       |
| X position    | LE Float   | `0`     |       |
| Y position    | LE Float   | `0`     |       |
| Z position    | LE Float   | `0`     |       |
| X orientation | LE Float   | `0`     |       |
| Y orientation | LE Float   | `0`     |       |
| Z orientation | LE Float   | `0`     |       |

## Input Data
Contains the key-states of a player, packed into a byte.

| ----------- | -------- |
| Packet ID   | 3        |
| Total Size: | 3 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                                                                 |
|------------|------------|---------|-----------------------------------------------------------------------|
| Player ID  | UByte      | `0`     |                                                                       |
| Key states | UByte      | `0`     | Each bit in the byte represents a key, as defined in the table below. |

#### Key States:

| Placement | Key    |
| --------- | ------ |
| 1         | Up     |
| 2         | Down   |
| 3         | Left   |
| 4         | Right  |
| 5         | Jump   |
| 6         | Crouch |
| 7         | Sneak  |
| 8         | Sprint |

## Weapon Input
Contains the weapon input state.

|------------:|---------|
| Packet ID   | 4       |
| Total Size: | 3 bytes |

| Field Name   | Field Type | Example | Notes                                                                                        |
|--------------|------------|---------|----------------------------------------------------------------------------------------------|
| Player ID    | UByte      | `0`     |                                                                                              |
| Weapon input | UByte      | `0`     | The lowest bit represents the primary fire, the second lowest represents the secondary fire. |

## Hit Packet
#### Client-to-Server

Sent by the client when a hit is registered. The server should verify that this
is possible to prevent abuse (such as hitting without shooting, facing the
wrong way, etc).


| -----------:| ------- |
| Packet ID   | 5       |
| Total Size: | 3 bytes |

#### Fields

| Field Name    | Field Type | Example | Notes                     |
|---------------|------------|---------|---------------------------|
| Player ID hit | UByte      | `0`     |                           |
| Hit type      | UByte      | `0`     | See values in table below |

#### Hit Types

| Value | Type  |
| ----- | ----- |
| 0     | Torso |
| 1     | Head  |
| 2     | Arms  |
| 3     | Legs  |
| 4     | Melee |

## Set HP
#### Server-to-Client

Sent to the client when hurt.


| -----------:| -------- |
| Packet ID   | 5        |
| Total Size: | 15 bytes |

| Field Name        | Field Type | Example | Notes                |
|-------------------|------------|---------|----------------------|
| HP                | UByte      | `0`     |                      |
| Type              | UByte      | `0`     | 0 = fall, 1 = weapon |
| Source X position | LE Float   | `0`     |                      |
| Source Y position | LE Float   | `0`     |                      |
| Source Z position | LE Float   | `0`     |                      |

## Grenade Packet
Spawns a grenade with the given information.

| ------------:| --------- |
| Packet ID    | 6         |
| Total Size:  | 30 bytes  |

#### Fields

| Field Name  | Field Type | Example | Notes |
|-------------|------------|---------|-------|
| Player ID   | UByte      | `0`     |       |
| Fuse length | LE Float   | `0`     |       |
| X position  | LE Float   | `0`     |       |
| Y position  | LE Float   | `0`     |       |
| Z position  | LE Float   | `0`     |       |
| X velocity  | LE Float   | `0`     |       |
| Y velocity  | LE Float   | `0`     |       |
| Z velocity  | LE Float   | `0`     |       |

## Set Tool
Sets a player's currently equipped tool/weapon.


|------------:|---------|
| Packet ID   | 7       |
| Total Size: | 3 bytes |

#### Fields

| Field Name | Field Type | Example | Notes                        |
|------------|------------|---------|------------------------------|
| Player ID  | UByte      | `0`     |                              |
| Tool       | UByte      | `0`     | Tool values are listed below |

#### Tools

| Value | Type    |
| ----- | -----   |
| 0     | Spade   |
| 1     | Block   |
| 2     | Gun     |
| 3     | Grenade |

## Set Colour
Set the colour of a player's held block.

|------------:|---------|
| Packet ID   | 8       |
| Total Size: | 5 bytes |

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| Player ID  | UByte      | `0`     |       |
| Blue       | UByte      | `0`     |       |
| Green      | UByte      | `0`     |       |
| Red        | UByte      | `0`     |       |

## Existing Player
Set player's team, weapon, etc.

|------------:|---------|
| Packet ID   | 9       |
| Total Size: | depends |

#### Fields

| Field Name | Field Type                                                  | Example | Notes |
|------------|-------------------------------------------------------------|---------|-------|
| Player ID  | UByte                                                       | `0`     |       |
| Team       | UByte                                                       | `0`     |       |
| Weapon     | UByte                                                       | `0`     |       |
| Held item  | UByte                                                       | `0`     |       |
| Kills      | LE UInt                                                     | `0`     |       |
| Blue       | UByte                                                       | `0`     |       |
| Green      | UByte                                                       | `0`     |       |
| Red        | UByte                                                       | `0`     |       |
| Name       | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String? | `Deuce` |       |

## Short Player Data
Like Existing Player, but with less information.

|------------:|---------|
| Packet ID   | 10      |
| Total Size: | 4 bytes |

#### Fields

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| Player ID  | UByte      | `0`     |       |
| Team       | UByte      | `0`     |       |
| Weapon     | UByte      | `0`     |       |

## Move Object
This packet is used to move various game objects like tents, intels and even grenades. When moving grenades in TC mode the voxlap client has a bug that changes grenades' models to small tents.

| ----------: | -------- |
| Packet ID   | 11       |
| Total Size: | 15 bytes |

#### Fields

| Field Name | Field Type | Example | Notes       |
|------------|------------|---------|-------------|
| Object ID  | UByte      | `0`     |             |
| Team       | UByte      | `0`     | 2 = neutral |
| X position | LE Float   | `0`     |             |
| Y position | LE Float   | `0`     |             |
| Z position | LE Float   | `0`     |             |

## Create Player
Send on respawn of a player.

| ----------: | ------- |
| Packet ID   | 12      |
| Total Size: | depends |

#### Fields

| Field Name | Field Type                                                  | Example | Notes |
|------------|-------------------------------------------------------------|---------|-------|
| Player ID  | UByte                                                       | `0`     |       |
| Weapon     | UByte                                                       | `0`     |       |
| Team       | UByte                                                       | `0`     |       |
| X position | LE Float                                                    | `0`     |       |
| Y position | LE Float                                                    | `0`     |       |
| Z position | LE Float                                                    | `0`     |       |
| Name       | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String? | `Deuce` |       |

## Block Action
Sent when a block is placed/destroyed.

| ----------: | -------- |
| Packet ID   | 13       |
| Total Size: | 15 bytes |

#### Fields

| Field Name  | Field Type | Example | Notes           |
|-------------|------------|---------|-----------------|
| Player ID   | UByte      | `0`     |                 |
| Action type | UByte      | `0`     | See table below |
| X position  | LE Int     | `0`     |                 |
| Y position  | LE Int     | `0`     |                 |
| Z position  | LE Int     | `0`     |                 |


#### Fields

| Value | Type                                   | Notes                                               |
| ----- | -------------------------------------- | --------------------------------------------------- |
| 0     | Build                                  | places a block with the player's selected color     |
| 1     | Bullet and spade (left button) destroy |                                                     |
| 2     | Spade (right button) destroy           | destroys 3 blocks, one above and below additionally |
| 3     | Grenade destroy                        | destroys all blocks within an 3x3x3 area            |

## Block Line
Create a line of blocks between 2 points. The block color is defined by the `Set Color` packet. 

| ----------: | -------- |
| Packet ID   | 14       |
| Total Size: | 26 bytes |

| Field Name       | Field Type      | Example | Notes |
| ---------------- | --------------- | ------- | ----- |
| Player ID        | UByte           | `0`     |       |
| Start X position | LE Int          | `0`     |       |
| Start Y position | LE Int          | `0`     |       |
| Start Z position | LE Int          | `0`     |       |
| End X position   | LE Int          | `0`     |       |
| End Y position   | LE Int          | `0`     |       |
| End Z position   | LE Int          | `0`     |       |

## CTF State
Brief description.

| ----------: | -------- |
| Packet ID   | none     |
| Total Size: | 52 bytes |

#### Fields

| Field Name             | Field Type    | Example | Notes                                                                |
| ---------------------- | ------------- | ------- | -------------------------------------------------------------------- |
| Team 1 score           | UByte         | `0`     |                                                                      |
| Team 2 score           | UByte         | `0`     |                                                                      |
| Capture limit          | UByte         | `0`     |                                                                      |
| Intel flags            | UByte         | `0`     | bits signal if teams have intel - bit 1 for team 1, bit 2 for team 2 |
| Team 1 intel location  | Location Data | `0`     | see below                                                            |
| Team 2 intel location  | Location Data | `0`     | see below                                                            |
| Team 1 base X position | LE Float      | `0`     |                                                                      |
| Team 1 base Y position | LE Float      | `0`     |                                                                      |
| Team 1 base Z position | LE Float      | `0`     |                                                                      |
| Team 2 base X position | LE Float      | `0`     |                                                                      |
| Team 2 base Y position | LE Float      | `0`     |                                                                      |
| Team 2 base Z position | LE Float      | `0`     |                                                                      |

The intel location data is 12 bytes long. If the intel is being held, the first
byte is a UByte with the ID of the holding player, then the rest are padding.
If the intel is on the ground (not being held), the data will hold three LE
Floats with its x, y and z position.

#### Fields

| Intel State         | Field Name        | Field Type   |
| ------------------- | ----------------- | ------------ |
| Held                | Holding player ID | UByte        |
|                     | N/A (padding)     | 11 bytes     |
| Dropped             | Intel X position  | LE Float     |
|                     | Intel Y position  | LE Float     |
|                     | Intel Z position  | LE Float     |

This packet is not a complete packet, as it is only sent after the initial
data, where the gamemode is sent. It could be considered as part of that
initial data packet, but as what's sent varies greatly depending on the
gamemode, it is documented separately.

## TC State

| Field Name                | Field Type                          | Example | Notes                                                                      |
| ------------------------- | ----------------------------------- | ------- | -------------------------------------------------------------------------- |
| territory count           | UByte                               | 16      | Maximum is 16 otherwise the client will crash with 'Invalid memory access' |
| Array[] of territory data | LE Float, LE Float, LE Float, UByte |         | See table below                                                            |

This packet is not a complete packet, as it is only sent after the initial
data, where the gamemode is sent. It could be considered as part of that
initial data packet, but as what's sent varies greatly depending on the
gamemode, it is documented separately.

## State Data
`Server-->Client`

Indicates that the map transfer is complete. Also informs the client of
numerous game parameters. Be aware that CTFState or TCState may be appended to
the packet after the gamemode ID portion.

| ----------: | -------- |
| Packet ID   | 15       |
| Total Size: | 52 bytes |

#### Fields

| Field Name               | Field Type     | Example   | Notes                     |
| ------------------------ | -------------- | --------- | ------------------------- |
| Player ID                | UByte          | 0         |                           |
| Fog blue color value     | UByte          | 0         |                           |
| Fog green color value    | UByte          | 0         |                           |
| Fog red color value      | UByte          | 0         |                           |
| Team 1 blue color value  | UByte          | 0         |                           |
| Team 1 green color value | UByte          | 0         |                           |
| Team 1 red color value   | UByte          | 0         |                           |
| Team 2 blue color value  | UByte          | 0         |                           |
| Team 2 green color value | UByte          | 0         |                           |
| Team 2 red color value   | UByte          | 0         |                           |
| Team 1 name              | CP437 String   | Blue      | Always 10 characters long |
| Team 2 name              | CP437 String   | Green     | Always 10 characters long |
| Gamemode ID              | UByte          | 0         | 0 for CTF, 1 for TC       |


## Kill Action
#### Server->Client

Notify the client of a player's death.

| ----------: | -------- |
| Packet ID   | 16       |
| Total Size: | 5 bytes  |

| Field Name       | Field Type | Example | Notes                 |
|------------------|------------|---------|-----------------------|
| Player ID        | UByte      | 12      | Player that died      |
| Killer ID        | UByte      | 8       |                       |
| Kill type        | UByte      | 0       | See table below       |
| Respawn time     | UByte      | 1       | Seconds until respawn |

#### Fields

If any value greater than 6 is received in the classic/Voxlap client,
it will display the kill message as "Derpy Kill Message".

| Value | Type                 |
|-------|----------------------|
| 0     | WEAPON (body, limbs) |
| 1     | HEADSHOT             |
| 2     | MELEE (spade)        |
| 3     | GRENADE              |
| 4     | FALL                 |
| 5     | TEAM\_CHANGE         |
| 6     | CLASS\_CHANGE        |

## Chat Message
#### Two-way

Reasonable limits should be placed on length and frequency of chat messages.

| ----------: | -------- |
| Packet ID   | 17       |
| Total Size: | . bytes  |

| Field Name   | Field Type                                                 | Example           | Notes           |
|--------------|------------------------------------------------------------|-------------------|-----------------|
| Player ID    | UByte                                                      | `0`               |                 |
| Chat Type    | UByte                                                      | `0`               | See table below |
| Chat Message | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `"join /squad 1"` |                 |

#### Fields

| Value | Type         | voxlap default color            |
| ----- | ------------ | ------------------------------- |
| 0     | CHAT\_ALL    | white                           |
| 1     | CHAT\_TEAM   | team color, black for spectator |
| 2     | CHAT\_SYSTEM | red                             |

## Map Start (0.75)
#### Server->Client

Sent when a client connects, or a map is advanced for already existing connections.

Should be the first packet received when a client connects.

| ----------: | -------- |
| Packet ID   | 18       |
| Total Size: | 5 bytes  |

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| Map size   | LE Uint    | `4567`  |       |

## Map Start (0.76)
#### Server->Client

Sent when a client connects, or a map is advanced for already existing connections.

Should be the first packet received when a client connects.

| ----------: | -------- |
| Packet ID   | 18       |
| Total Size: | 9+ bytes |

#### Fields

| Field Name | Field Type                                                 | Example       | Notes |
|------------|------------------------------------------------------------|---------------|-------|
| Map size   | Uint32                                                     | `283839`      |       |
| CRC32      | Uint32                                                     | `0x4c7ebe43`  |       |
| Map name   | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `"pinpoint2"` |       |

## Map Chunk
#### Server->Client

Sent just after **Map Start**, repeatedly until the entire map is sent.

Should always be the next sequence of packets after a **Map Start** packet.

| ----------: | -------- |
| Packet ID   | 19       |
| Total Size: | depends  |

#### Fields

| Field Name | Field Type | Example | Notes                                                                                                                              |
|------------|------------|---------|------------------------------------------------------------------------------------------------------------------------------------|
| Map Data   | UByte      | `0`     | [DEFLATE/zlib](http://en.wikipedia.org/wiki/DEFLATE) encoded [AOS map data](http://silverspaceship.com/aosmap/aos_file_format.html)|

## Player Left
#### Server->Protocol

Sent when a player disconnects.


| ----------: | -------- |
| Packet ID   | 20       |
| Total Size: | 2 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| player ID  | UByte      | `0`     |       |

## Territory Capture
#### Server->Protocol

Sent when a player captures a Command Post in Territory Control mode.

Captures have affects on the client.

| ----------: | -------- |
| Packet ID   | 21       |
| Total Size: | 5 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                           |
|------------|------------|---------|---------------------------------|
| Player ID  | UByte      | `0`     |                                 |
| Entity ID  | UByte      | `0`     | The ID of the CP being captured |
| Winning    | UByte      | `0`     | (or losing)                     |
| State      | UByte      | `0`     | Team ID                         |

## Progress Bar
#### Server->Client

Display the TC progress bar.

| ----------: | -------- |
| Packet ID   | 22       |
| Total Size: | 8 bytes  |

#### Fields

| Field Name        | Field Type | Example | Notes                                                                                            |
|-------------------|------------|---------|--------------------------------------------------------------------------------------------------|
| Entity ID         | UByte      | `0`     | The ID of the tent entity                                                                        |
| Capturing team ID | UByte      | `1`     |                                                                                                  |
| Rate              | Byte       | `2`     | Used by the client for interpolation, one per team member capturing (minus enemy team members). One rate unit is 5% of progress per second. |
| Progress          | LE Float   | `0.5`   | In range [0,1]                                                                                   |

## Intel Capture
#### Server->Protocol

Sent when a player captures the intel, which is determined by the server.

Winning captures have affects on the client.

| ----------: | -------- |
| Packet ID   | 23       |
| Total Size: | 3 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                   |
|------------|------------|---------|-------------------------|
| Player ID  | UByte      | `0`     |                         |
| Winning    | UByte      | `0`     | Was the winning capture |

## Intel Pickup
#### Server->Protocol

Sent when a player collects the intel, which is determined by the server.

| ----------: | -------- |
| Packet ID   | 24       |
| Total Size: | 2 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| Player ID  | UByte      | `0`     |       |

## Intel Drop
#### Server->Protocol

Sent when a player dropped the intel. This will update the intel position on the client.


| ----------: | -------- |
| Packet ID   | 25       |
| Total Size: | 14 bytes |

#### Fields

| Field Name | Field Type | Example | Notes                              |
| Player ID  | UByte      | `0`     | ID of the player who dropped intel |
| X position | LE Float   | `32.0`  |                                    |
| Y position | LE Float   | `32.0`  |                                    |
| Z position | LE Float   | `32.0`  |                                    |

## Restock
#### Server->Protocol

Id of the player who has been restocked.

| ----------: | -------- |
| Packet ID   | 26       |
| Total Size: | 2 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                          |
|------------|------------|---------|--------------------------------|
| Player ID  | UByte      | `0`     | ID of the player who restocked |

## Fog Colour
#### Server->Client

Set the colour of a player's fog.

| ----------: | -------- |
| Packet ID   | 27       |
| Total Size: | 5 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes  |
| ---------- | ---------- | ------- | ------ |
| Alpha      | UByte      | `0`     | Unused |
| Blue       | UByte      | `255`   |        |
| Green      | UByte      | `232`   |        |
| Red        | UByte      | `128`   |        |

## Weapon Reload
#### Client-->Server->Protocol

Sent by the client when the player reloads their weapon, and relayed to other
clients after protocol logic applied.

This has no affect on animation, but is used to trigger sound effects on the
other clients.

| ----------: | -------- |
| Packet ID   | 28       |
| Total Size: | 4 bytes  |

#### Fields

| Field Name   | Field Type | Example | Notes               |
|--------------|------------|---------|---------------------|
| Player ID    | UByte      | `0`     | Player who reloaded |
| Clip ammo    | UByte      | `0`     |                     |
| Reserve ammo | UByte      | `0`     |                     |

## Change Team
#### Client-->Server-->Protocol-->Kill Action & Create Player

Sent by the client when the player changes team. It is not relayed to clients
directly, but instead uses **Kill Action** (optionally)
then **Create Player** to inform other
clients of the team change.

| ----------: | -------- |
| Packet ID   | 29       |
| Total Size: | 3 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                       |
|------------|------------|---------|-----------------------------|
| Player ID  | UByte      | `0`     | Player who has changed team |
| Team ID    | UByte      | `0`     | See values in table below   |

#### Team IDs

| Value    | Type                |
|---------:|---------------------|
| 255      | Spectator           |
| 0        | First team (Blue)   |
| 1        | Second team (Green) |

## Change Weapon
#### Client-->Server-->Protocol-->Kill Action & Create Player

Sent by the client when the player changes weapon. It SHOULD NOT be sent to clients,
but pyspades and all known derivatives send the packet with invalid parameters
immediately before the kill action is sent (if any). All packets of this type sent from
the server SHOULD be ignored.
Otherwise, the server sends **Kill Action** (optionally)
then **Create Player** to inform other
clients of the weapon change.

| ----------: | -------- |
| Packet ID   | 30       |
| Total Size: | 3 bytes  |

| Field Name | Field Type | Example | Notes                         |
|------------|------------|---------|-------------------------------|
| Player ID  | UByte      | `0`     | Player who has changed weapon |
| Weapon ID  | UByte      | `0`     | See values in table below     |

#### Weapon ID

| Value | Type    |
|-------|---------|
| 0     | Rifle   |
| 1     | SMG     |
| 2     | Shotgun |

## Map Cached (0.76)
`Client->Server`

| ----------: | -------- |
| Packet ID   | 31       |
| Total Size: | 2 bytes  |

| Field Name | Field Type | Example | Notes                        |
|------------|------------|---------|------------------------------|
| Cached     | UByte      | `1`     | `1` if cached, `0` otherwise |

# Extra Packets

Extra packets are new packets added by the community, usually requiring a script.

## Version Handshake Init (EP)
#### Server->Client

Sent to the client for checking if client is compatible with version info (this isnt
required to get version info).

When sent, server waits for a [Handshake Response](#version-handshake-response-ep) with the
challenge.


| ----------: | -------- |
| Packet ID   | 31       |
| Total Size: | 5 bytes  |

| Field Name | Field Type | Example | Notes                                                   |
|------------|------------|---------|---------------------------------------------------------|
| Challenge  | LE Int     | `42`    | A number that should be sent back in handshake response |

## Version Handshake Response (EP)
#### Client->Server

Send back the challenge number to the server, for validating the client (this isnt
required to get version info).


| ----------: | -------- |
| Packet ID   | 32       |
| Total Size: | 5 bytes  |

| Field Name | Field Type | Example | Notes                                       |
|------------|------------|---------|---------------------------------------------|
| Challenge  | LE Int     | `42`    | Number sent to the client in Handshake Init |


## Version Get (EP)
#### Server->Client

Ask the client to send the client and operational system infos.


| ----------: | -------- |
| Packet ID   | 33       |
| Total Size: | 1 byte   |

## Version Response (EP)
#### Client->Server

Send the client and operational system infos.


| ----------: | -------------- |
| Packet ID   | 34             |
| Total Size: | (varies) bytes |

| Field Name         | Field Type   | Example      | Notes                                  |
|--------------------|--------------|--------------|----------------------------------------|
| client_identifier  | Byte         | `o`          | Number representing an ASCII character |
| version_major      | Byte         | `-1`         | Current client major version           |
| version_minor      | Byte         | `-1`         | Current client minor version           |
| version_revision   | Byte         | `-1`         | Current client revision version        |
| version_revision   | Byte         | `-1`         | Current client revision version        |
| os_info            | CP437 String | `Windows 10` | Operational System informations        |

# Powerthirst Edition

This version adds 4 new packets, extends 2 packets, and duplicately maps 1 packet over another.

The World Update packet has up to 64 fields now instead of 32.

## Map Start (PT)
#### Server->Client

Sent when a client connects, or a map is advanced for already existing connections.

Should be the first packet received when a client connects.

The version must exist and be >= 1 (and &lt;= the client's Powerthirst proto
version or otherwise the client will refuse to connect) to enable certain
Powerthirst features such as long-name support.


| ----------: | -------- |
| Packet ID   | 18       |

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| Map size   | Uint32     | `4567`  |       |
| PT version | UInt32     | `4`     |       |

## Map Chunk (PT)
#### Server->Client

This is just a remapping of the [Map Chunk](#map-chunk) packet to 2 packets back to stop vanilla clients from connecting.

| ----------: | -------- |
| Packet ID   | 17       |
| Total Size: | 9 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                                                                                                                               |
|------------|------------|---------|-------------------------------------------------------------------------------------------------------------------------------------|
| Map Data   | UByte      | `0`     | [DEFLATE/zlib](http://en.wikipedia.org/wiki/DEFLATE) encoded [AOS map data](http://silverspaceship.com/aosmap/aos_file_format.html) |

## Script Begin (PT)
#### Server->Client


| ----------: | --------       |
| Packet ID   | 31             |
| Total Size: | (varies) bytes |

#### Fields

| Field Name  | Field Type                                                 | Example | Notes |
|-------------|------------------------------------------------------------|---------|-------|
| Script size | Uint32                                                     | `4567`  |       |
| Module name | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String |         |       |

## Script Chunk (PT)
#### Server->Client

This is just a remapping of the [Map_Chunk](#map-chunk) packet to 2 packets back to stop vanilla clients from connecting.


| ----------: | --------       |
| Packet ID   | 32             |
| Total Size: | (varies) bytes |

#### Fields

| Field Name  | Field Type | Example | Notes                                                                                                                         |
|-------------|------------|---------|-------------------------------------------------------------------------------------------------------------------------------|
| Script Data | UByte      | `0`     | [DEFLATE/zlib](http://en.wikipedia.org/wiki/DEFLATE) encoded [AngelScript source code](http://www.angelcode.com/angelscript/) |


## Script End (PT)
#### Server->Client

Once this is sent, the script is loaded.

| ----------: | --------       |
| Packet ID   | 33             |
| Total Size: | (varies) bytes |

#### Fields

| Field Name  | Field Type                                                 | Example | Notes |
|-------------|------------------------------------------------------------|---------|-------|
| Module name | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String |         |       |

## Script Call (PT)
#### Server->Client


| ----------: | --------       |
| Packet ID   | 34             |
| Total Size: | (varies) bytes |

#### Fields

| Field Name    | Field Type                                                              | Example       | Notes                                                      |
|---------------|-------------------------------------------------------------------------|---------------|------------------------------------------------------------|
| Function name | 0-terminated [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `void main()` | Must be an AngelScript prototype, not just the name itself |
| Parameters    | See below                                                               |               |                                                            |

### Script Parameters
Start from after the 0-byte in the Function name string. Then, loop through these IDs:

* 0: `ASP_TERM`: End of parameter list.
* 1: `ASP_INT`: Read a 32-bit little-endian int. AngelScript type: "int"
* 2: `ASP_FLOAT`: Read a 32-bit little-endian single-precision float. AngelScript type: "float"
* 3: `ASP_PSTRING`: Read an 8-bit uint, then read that many bytes as a string (do NOT add in a terminating NUL). AngelScript type: "const string &in"
