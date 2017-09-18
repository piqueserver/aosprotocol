This page documents the Ace of Spades 1.0 alpha builds protocol.

# Connection

When you connect, you must send a version number as the initial data.

| Number | AoS version  |
|--------|--------------|
| 3      | 1.0a1        |

Send this magic number as part of the `enet_host_connect(ENetHost, ENetAddress, channels, int)` function

## Disconnect Reasons

Whenever the connection is closed by the server, there is a reason supplied to the client in the event's data (event.data).

| Number | Reason                       |
|--------|------------------------------|
| 0      | ERROR_UNDEFINED              |
| 1      | ERROR_BANNED                 |
| 2      | ERROR_KICKED                 |
| 3      | ERROR_WRONG_VERSION          |
| 4      | ERROR_FULL                   |


## About Coordinates

In Ace of Spades the up-down axis is Z and it is inverted. This means 63 is water level and 0 is the highest point on a map.

# Packets

## Table of Contents
- [Data types](#data-types)
- [Position Data](#position-data)
- [Orientation Data](#orientation-data)
- [World Update](#world-update)
- [Input Data](#input-data)
- [Weapon Input](#weapon-input)
- [Hit Packet](#hit-packet)
- [Set HP](#set-hp)
- [Use Oriented Item](#use-oriented-item)
- [Set Tool](#set-tool)
- [Set Color](#set-color)
- [Existing Player](#existing-player)
- [Short Player Data](#short-player-data)
- [Entity](#entity)
- [Change Entity](#change-entity)
- [Destroy Entity](#destroy-entity)
- [Create Entity](#create-entity)
- [Play Sound](#play-sound)
- [Stop Sound](#stop-sound)
- [Create Player](#create-player)
- [Block Action](#block-action)
- [Server Block Item](#server-block-item)
- [Server Block Action](#server-block-action)
- [Block Line](#block-line)
- [State Data](#state-data)
- [Kill Action](#kill-action)
- [Chat Message](#chat-message)
- [Map Start](#map-start)
- [Map Chunk](#map-chunk)
- [Pack Start](#pack-start)
- [Pack Response](#pack-response)
- [Pack Chunk](#pack-chunk)
- [Player Left](#player-left)
- [Progress Bar](#progress-bar)
- [Restock](#restock)
- [Fog Colour](#fog-colour)
- [Weapon Reload](#weapon-reload)
- [Change Team](#change-team)
- [Change Weapon](#change-weapon)
- [Set Score](#set-score)

All packets start with an unsigned byte to specify their type, followed by the data for that type of packet. The size given for each packet below includes this byte.

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

|-----------:|----------|
|Packet ID:  |  0       |
|Total Size: | 12 bytes |

|Field Name|Field Type|Example|Notes|
|---------:|----------|-------|-----|
|        x | LE Float |  `0`  |     |
|        y | LE Float |  `0`  |     |
|        z | LE Float |  `0`  |     |

## Orientation Data
This packet is used to set the players orientation.

|-----------:|----------|
|Packet ID   |  1       |
|Total Size: | 13 bytes |

#### Fields

|Field Name|Field Type|Example|Notes|
|---------:|----------|-------|-----|
|        x | LE Float |  `0`  |     |
|        y | LE Float |  `0`  |     |
|        z | LE Float |  `0`  |     |

## World Update
Updates position and orientation of all players. Unlike 0.75, this only sends information for the necessary players.

| -----------: | ----------    |
| Packet ID    | 2             |
| Total Size:  | 1 + 25n bytes |

#### Fields

| Field Name                         | Field Type                                     | Example | Notes                    |
|------------------------------------|------------------------------------------------|---------|--------------------------|
| players positions and orientations | Array[] of Player Position Data, variable size |         | See below table for data |

#### 'Player Position Data'

|------------:|----------|
| Total Size: | 25 bytes |

#### Fields

| Field Name    | Field Type | Example | Notes |
|---------------|------------|---------|-------|
| player ID     | UByte      | `0`     |       |
| x position    | LE Float   | `0`     |       |
| y position    | LE Float   | `0`     |       |
| z position    | LE Float   | `0`     |       |
| x orientation | LE Float   | `0`     |       |
| y orientation | LE Float   | `0`     |       |
| z orientation | LE Float   | `0`     |       |

## Input Data
Contains the key-states of a player, packed into a byte.

| ----------- | -------- |
| Packet ID   | 3        |
| Total Size: | 3 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                                                                 |
|------------|------------|---------|-----------------------------------------------------------------------|
| player ID  | UByte      | `0`     |                                                                       |
| key states | UByte      | `0`     | Each bit in the byte represents a key, as defined in the table below. |

#### Key States:

| Placement | Key    |
| --------- | ------ |
| 1         | up     |
| 2         | down   |
| 3         | left   |
| 4         | right  |
| 5         | jump   |
| 6         | crouch |
| 7         | sneak  |
| 8         | sprint |

## Weapon Input
Contains the weapon input state(?).

|------------:|---------|
| Packet ID   | 4       |
| Total Size: | 3 bytes |

| Field Name   | Field Type | Example | Notes                                                                                        |
|--------------|------------|---------|----------------------------------------------------------------------------------------------|
| player ID    | UByte      | `0`     |                                                                                              |
| weapon input | UByte      | `0`     | The lowest bit represents the primary fire, the second lowest represents the secondary fire. |

## Hit Packet
#### Client-to-Server

Sent by the client when a hit is registered. The server should verify that this is possible to prevent abuse (such as hitting without shooting, facing the wrong way, etc).


| -----------:| ------- |
| Packet ID   | 5       |
| Total Size: | 3 bytes |

#### Fields

| Field Name    | Field Type | Example | Notes                     |
|---------------|------------|---------|---------------------------|
| player ID hit | UByte      | `0`     |                           |
| hit type      | UByte      | `0`     | See values in table below |

#### Hit Types

| Value | Type  |
| ----- | ----- |
| 0     | TORSO |
| 1     | HEAD  |
| 2     | ARMS  |
| 3     | LEGS  |
| 4     | MELEE |

## Set HP
#### Server-to-Client

Sent to the client when hurt.


| -----------:| -------- |
| Packet ID   | 5        |
| Total Size: | 15 bytes |

| Field Name        | Field Type | Example | Notes                |
|-------------------|------------|---------|----------------------|
| HP                | UByte      | `0`     |                      |
| type              | UByte      | `0`     |                      |
| source x position | LE Float   | `0`     |                      |
| source y position | LE Float   | `0`     |                      |
| source z position | LE Float   | `0`     |                      |

#### Types

| Value | Type         |
| ----: | ------------ |
| 0     | DAMAGE_SELF  |
| 1     | DAMAGE_OTHER |
| 2     | HEAL         |

## Use Oriented Item
Spawns an oriented item (grenade or rocket) with the given information.

| ------------:| --------- |
| Packet ID    | 6         |
| Total Size:  | 31 bytes  |

#### Fields

| Field Name  | Field Type | Example | Notes |
|-------------|------------|---------|-------|
| player ID   | UByte      | `0`     |       |
| tool        | UByte      | `0`     |       |
| value       | LE Float   | `0`     |       |
| x position  | LE Float   | `0`     |       |
| y position  | LE Float   | `0`     |       |
| z position  | LE Float   | `0`     |       |
| x velocity  | LE Float   | `0`     |       |
| y velocity  | LE Float   | `0`     |       |
| z velocity  | LE Float   | `0`     |       |

#### Tools

| ID    | Tool         | Value |
| ----- | ------------ | ----- |
| 3     | GRENADE_TOOL | fuse  |
| 4     | RPG_TOOL     | n/a   |


## Set Tool
Sets a player's currently equipped tool/weapon.


|------------:|---------|
| Packet ID   | 7       |
| Total Size: | 3 bytes |

#### Fields

| Field Name | Field Type | Example | Notes                        |
|------------|------------|---------|------------------------------|
| player ID  | UByte      | `0`     |                              |
| tool       | UByte      | `0`     | Tool values are listed below |

#### Tools

| Value | Type    |
| ----- | -----   |
| 0     | spade   |
| 1     | block   |
| 2     | gun     |
| 3     | grenade |

## Set Color
Set the color of a player's held block.

|------------:|---------|
| Packet ID   | 8       |
| Total Size: | 5 bytes |

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| player ID  | UByte      | `0`     |       |
| blue       | UByte      | `0`     |       |
| green      | UByte      | `0`     |       |
| red        | UByte      | `0`     |       |

## Existing Player
Set player's team, weapon, etc.


|------------:|-----------|
| Packet ID   | 9         |
| Total Size: | 12 + name |

#### Fields

| Field Name | Field Type                                                 | Example | Notes |
|------------|------------------------------------------------------------|---------|-------|
| player ID  | UByte                                                      | `0`     |       |
| team       | Byte                                                       | `0`     |       |
| weapon     | UByte                                                      | `0`     |       |
| tool       | UByte                                                      | `0`     |       |
| kills      | LE UInt                                                    | `0`     |       |
| blue       | UByte                                                      | `0`     |       |
| green      | UByte                                                      | `0`     |       |
| red        | UByte                                                      | `0`     |       |
| name       | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | ``      |       |

## Short Player Data
Like Existing Player, but with less information.

|------------:|---------|
| Packet ID   | 10      |
| Total Size: | 4 bytes |

#### Fields

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| player ID  | UByte      | `0`     |       |
| team       | Byte       | `0`     |       |
| weapon     | UByte      | `0`     |       |

## Entity
This packet is not a complete packet. It is only sent in StateData and CreateEntity.

| ----------: | -------- |
| Packet ID   | none     |
| Total Size: | 16 bytes |

#### Fields

| Field Name  | Field Type    | Example | Notes      |
| ----------- | ------------- | ------- | -----      |
| id          | UByte         | `0`     | entity id  |
| type        | UByte         | `0`     |            |
| state       | UByte         | `0`     | team id    |
| carrier     | UByte         | `0`     | player id  |
| x           | LE Float      | `0`     |            |
| y           | LE Float      | `0`     |            |
| z           | LE Float      | `0`     |            |

#### Values

| Value | type         | state        |
| ----- | ------------ | ------------ |
| 0     | FLAG         | team 1       |
| 1     | BASE (CP)    | team 2       |
| 2     | HELICOPTER   | NEUTRAL_TEAM |
| 3     | AMMO_CRATE   |              |
| 4     | HEALTH_CRATE |              |



## Change Entity
Brief description.

| ----------: | ------- |
| Packet ID   | 11      |
| Total Size: | 17      |

#### Fields

| Field Name  | Field Type    | Example | Notes                               |
| ----------- | ------------- | ------- | ----------------------------------- |
| entity id   | UByte         | `0`     |                                     |
| type        | UByte         | `0`     |                                     |
| state       | UByte         | `0`     | present only if type = SET_STATE    |
| carrier     | UByte         | `0`     | present only if type = SET_CARRIER  |
| x           | LE Float      | `0`     | present only if type = SET_POSITION |
| y           | LE Float      | `0`     | present only if type = SET_POSITION |
| z           | LE Float      | `0`     | present only if type = SET_POSITION |

#### Types

| Value | Type         |
| ----- | ------------ |
| 0     | SET_STATE    |
| 1     | SET_POSITION |
| 2     | SET_CARRIER  |

## Destroy Entity
Destroys the entity with ID entity_id.

| ----------: | ------- |
| Packet ID   | 12      |
| Total Size: | 2       |

#### Fields

| Field Name  | Field Type    | Example | Notes                               |
| ----------- | ------------- | ------- | ----------------------------------- |
| entity id   | UByte         | `0`     |                                     |

## Create Entity
Destroys the entity with ID entity_id.

| ----------: | ------- |
| Packet ID   | 13      |
| Total Size: | 17      |

#### Fields

| Field Name  | Field Type    | Example | Notes                               |
| ----------- | ------------- | ------- | ----------------------------------- |
| entity      | Entity        | ``      |                                     |

## Play Sound
Play a .wav sound file.

| ----------: | --------- |
| Packet ID   | 14        |
| Total Size: | name + 15 |

#### Fields

| Field Name  | Field Type                                                 | Example     | Notes                                 |
|-------------|------------------------------------------------------------|------------ |---------------------------------------|
| name        | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `disco.wav` |                                       |
| sound flags | UByte                                                      | `0`         |                                       |
| loop_id     | UByte                                                      | `0`         | only present if looping bit set       |
| x position  | LE Float                                                   | `0`         | only present if positional bit is set |
| y position  | LE Float                                                   | `0`         | only present if positional bit is set |
| z position  | LE Float                                                   | `0`         | only present if positional bit is set |

#### Sound Flags:

| Bit | Flag       |
| --- | ---------- |
| 0   | looping    |
| 1   | positional |

## Stop Sound
Stop a looping .wav file.

| ----------: | ---- |
| Packet ID   | 15   |
| Total Size: | 2    |

#### Fields

| Field Name  | Field Type  | Example     | Notes |
|-------------|-------------|------------ | ----- |
| loop id     | UByte       | `0`         |       |

## Create Player
Brief description.

| ----------: | ------- |
| Packet ID   | 16      |
| Total Size: | depends |

#### Fields

| Field Name | Field Type                                                 | Example | Notes |
|------------|------------------------------------------------------------|---------|-------|
| player id  | UByte                                                      | `0`     |       |
| weapon     | UByte                                                      | `0`     |       |
| team       | Byte                                                       | `0`     |       |
| x position | LE Float                                                   | `0`     |       |
| y position | LE Float                                                   | `0`     |       |
| z position | LE Float                                                   | `0`     |       |
| name       | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | ``      |       |

## Block Action
Sent when a block is placed/destroyed.

| ----------: | -------- |
| Packet ID   | 17       |
| Total Size: | 15 bytes |

#### Fields

| Field Name  | Field Type | Example | Notes           |
|-------------|------------|---------|-----------------|
| player id   | UByte      | `0`     |                 |
| action type | UByte      | `0`     | See table below |
| x position  | LE Int     | `0`     |                 |
| y position  | LE Int     | `0`     |                 |
| z position  | LE Int     | `0`     |                 |


#### Fields

| Value | Type              |
| ----- | ----------------- |
| 0     | BUILD_BLOCK       |
| 1     | DESTROY_BLOCK     |
| 2     | SPADE_DESTROY     |
| 3     | GRENADE_DESTROY   |

## Server Block Item
This packet is not a complete packet. It is only sent in ServerBlockAction.

| ----------: | -------- |
| Packet ID   | none     |
| Total Size: | 16 bytes |

#### Fields

| Field Name  | Field Type    | Example | Notes      |
| ----------- | ------------- | ------- | -----      |
| x           | LE Float      | `0`     |            |
| y           | LE Float      | `0`     |            |
| z           | LE Float      | `0`     |            |
| blue        | UByte         | `0`     |            |
| green       | UByte         | `0`     | team id    |
| red         | UByte         | `0`     | player id  |

#### Values

| Value | type         | state        |
| ----- | ------------ | ------------ |
| 0     | FLAG         | team 1       |
| 1     | BASE (CP)    | team 2       |
| 2     | HELICOPTER   | NEUTRAL_TEAM |
| 3     | AMMO_CRATE   |              |
| 4     | HEALTH_CRATE |              |

This packet is not a complete packet. It is only sent in StateData and CreateEntity.

## Server Block Action
Sent when a block is directly added to or removed from the map
by the server.

| ----------: | ------------- |
| Packet ID   | 18            |
| Total Size: | 4 + 16n bytes |

#### Fields

| Field Name  | Field Type                            | Example | Notes           |
|-------------|-------------------------------------- |---------|-----------------|
| length      | LE UInt                               | `0`     |                 |
| items       | ServerBlockItem[length] array         | `0`     |                 |

## Block Line
Create a line of blocks between 2 points.

| ----------: | -------- |
| Packet ID   | 19       |
| Total Size: | 26 bytes |

| Field Name       | Field Type      | Example | Notes |
| player id        | UByte           | `0`     |       |
| start x position | LE Int          | `0`     |       |
| start y position | LE Int          | `0`     |       |
| start z position | LE Int          | `0`     |       |
| end x position   | LE Int          | `0`     |       |
| end y position   | LE Int          | `0`     |       |
| end z position   | LE Int          | `0`     |       |

## State Data
`Server->Client`

Indicates that the map transfer is complete. Also informs the client of numerous game parameters. Be aware that CTFState or TCState may be appended to the packet after the gamemode id portion.

| ----------: | -------- |
| Packet ID   | 20       |
| Total Size: | variable |

#### Fields

| Field Name             | Field Type     | Example   | Notes                     |
| ---------------------- | -------------- | --------- | ------------------------- |
| player id              | UByte          | 0         |                           |
| fog color (b, g, r)    | UByte[3]       | 127,63,63 |                           |
| team 1 color (b, g, r) | UByte[3]       | 127,63,63 |                           |
| team 2 color (b, g, r) | UByte[3]       | 127,63,63 |                           |
| team 1 score           | UByte          | 0         |                           |
| team 2 score           | UByte          | 0         |                           |
| score limit            | UByte          | 0         |                           |
| team name 1            | CP437 String   | Blue      |                           |
| team name 2            | CP437 String   | Green     |                           |
| mode name              | CP437 String   | CTF       |                           |
| entities               | Entity[n]      |           | Variable length           |

## Kill Action
#### Server->Client

Notify the client of a player's death.

| ----------: | -------- |
| Packet ID   | 21       |
| Total Size: | 5 bytes  |

| Field Name       | Field Type | Example | Notes                 |
|------------------|------------|---------|-----------------------|
| player ID        | UByte      | 12      | Player that died      |
| killer ID        | UByte      | 8       |                       |
| kill type        | UByte      | 0       | See table below       |
| respawn time     | UByte      | 1       | Seconds until respawn |

#### Kill Types

| Value | Type                 |
|-------|----------------------|
| 0     | WEAPON_KILL          |
| 1     | HEADSHOT_KILL        |
| 2     | MELEE_KILL           |
| 3     | GRENADE_KILL         |
| 4     | FALL_KILL            |
| 5     | TEAM_CHANGE_KILL     |
| 6     | CLASS_CHANGE_KILL    |

## Chat Message
#### Two-way

Reasonable limits must placed on length and frequency of chat messages.


| ----------: | -------- |
| Packet ID   | 22       |
| Total Size: | variable |

| Field Name   | Field Type                                                 | Example           | Notes           |
|--------------|------------------------------------------------------------|-------------------|-----------------|
| player id    | UByte                                                      | `0`               |                 |
| Chat Type    | UByte                                                      | `0`               | See table below |
| Chat Message | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `"join /squad 1"` |                 |



#### Fields

| Value | Type         |
|-------|--------------|
| 0     | CHAT_ALL     |
| 1     | CHAT_TEAM    |
| 2     | CHAT_SYSTEM  |
| 3     | CHAT_BIG     |

## Map Start
#### Server->Client

Sent after server packs when a client connects, or when a map
is advanced for already existing connections.

Should be the first packet received after server packs (if any).

| ----------: | -------- |
| Packet ID   | 23       |
| Total Size: | 5 bytes  |

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| size       | Uint32     | `4567`  |       |

## Map Chunk
#### Server->Client

Sent just after [Map Start](#map-start), repeatedly until the entire map is sent.

Should always be the next sequence of packets after a [Map Start](#map-start).


| ----------: | -------- |
| Packet ID   | 24       |
| Total Size: | depends  |

#### Fields

| Field Name | Field Type | Example | Notes                                                                                                                              |
|------------|------------|---------|------------------------------------------------------------------------------------------------------------------------------------|
| data       | UByte      | `0`     | [DEFLATE/zlib](http://en.wikipedia.org/wiki/DEFLATE) encoded [AOS map data](http://silverspaceship.com/aosmap/aos_file_format.html) |

## Pack Start
#### Server->Client

Sent when a client connects.

Should be the first packet received after a client connects (if packs exist, Map Start otherwise).

| ----------: | -------- |
| Packet ID   | 25       |
| Total Size: | 5 bytes  |

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| size       | Uint32     | `4567`  |       |

## Pack Response
#### Client->Server

Response by the client to [Pack Start](#pack-start).

Should always be the next packet after the client receives a [Pack Start](#pack-start).

| ----------: | --------- |
| Packet ID   | 26        |
| Total Size: | 2 bytes   |

#### Fields

| Field Name | Field Type | Example | Notes                                                  |
|------------|------------|---------|--------------------------------------------------------|
| value      | UByte      | `0`     | Whether or not the client has the server pack already. |

## Pack Chunk
#### Server->Client

Sent just after receiving [Pack Response](#pack-response) from the client (if value is 0),
repeatedly until the entire pack is sent.

Should always be the next sequence of packets after a [Pack Response](#pack-response)  (if value is 0).


| ----------: | -------- |
| Packet ID   | 27       |
| Total Size: | depends  |

#### Fields

| Field Name | Field Type | Example | Notes                                                                       |
|------------|------------|---------|-----------------------------------------------------------------------------|
| data       | UByte      | `0`     | [DEFLATE](http://en.wikipedia.org/wiki/DEFLATE) compressed ZIP archive data |


## Player Left
#### Server->Protocol

Sent when a player disconnects.


| ----------: | -------- |
| Packet ID   | 28       |
| Total Size: | 2 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes |
|------------|------------|---------|-------|
| player ID  | UByte      | `0`     |       |

## Progress Bar
#### Server->Client

Display a progress bar.

| ----------: | -------- |
| Packet ID   | 29       |
| Total Size: | 14 bytes |

#### Fields

| Field Name        | Field Type | Example     | Notes                                    |
|-------------------|------------|-------------|------------------------------------------|
| progress          | LE Float   | `0.5`       | In range [0, 1]                          |
| rate              | LE Float   | `0.1`       | In range [0. 1] (used for interpolation) |
| color1 (b, g, r)  | UByte[3]   | `127,63,63` |                                          |
| color2 (b, g, r)  | UByte[3]   | `127,63,63` |                                          |

## Restock
#### Server->Protocol

Id of the player who has been restocked.

| ----------: | -------- |
| Packet ID   | 30       |
| Total Size: | 2 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                          |
|------------|------------|---------|--------------------------------|
| player ID  | UByte      | `0`     | ID of the player who restocked |

## Fog Colour
#### Server->Client

Set the colour of a player's fog.

| ----------: | -------- |
| Packet ID   | 31       |
| Total Size: | 5 bytes  |

#### Fields

| Field Name | Field Type | Example      | Notes        |
| ---------- | ---------- | ------------ | ------------ |
| fog color  | UInt       | `0h00fefefe` | BGRA encoded |

## Weapon Reload
#### Client-->Server->Protocol

Sent by the client when the player reloads their weapon, and relayed to other clients after protocol logic applied.

This has no affect on animation, but is used to trigger sound effects on the other clients.


| ----------: | -------- |
| Packet ID   | 32       |
| Total Size: | 4 bytes |

#### Fields

| Field Name   | Field Type | Example | Notes               |
|--------------|------------|---------|---------------------|
| player ID    | UByte      | `0`     | Player who reloaded |
| clip ammo    | UByte      | `0`     |                     |
| reserve ammo | UByte      | `0`     |                     |

## Change Team
#### Client-->Server-->Protocol-->[Kill Action](#kill-action) & [Create Player](#create-player)

Sent by the client when the player changes team.
Is not relayed to all clients directly, but instead
uses [Kill Action](#kill-action) then [Create Player](#create-player)
to inform other clients of the team change.

| ----------: | -------- |
| Packet ID   | 33       |
| Total Size: | 3 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes                     |
|------------|------------|---------|---------------------------|
| player ID  | UByte      | `0`     | Player who changed team   |
| Team ID    | Byte       | `0`     | See values in table below |

#### Team IDs

| Value | Type      |
|------:|-----------|
| -1    | spectator |
| 0     | blue      |
| 1     | green     |

## Change Weapon
#### Client-->Server-->Protocol-->[Kill Action](#kill-action) & [Change Weapon](#change-weapon)

Sent by the client when player changes weapon, and relayed to clients by server after filter_visibility logic applied.

Receiving clients will also be sent a preceding [Kill Action](#kill-action) to inform them the player has died both of which are sent as reliable packets.


| ----------: | -------- |
| Packet ID   | 34       |
| Total Size: | 3 bytes  |


| Field Name | Field Type | Example | Notes                       |
|------------|------------|---------|-----------------------------|
| player ID  | UByte      | `0`     | Player who's changed weapon |
| Weapon ID  | UByte      | `0`     | See values in table below   |

#### Weapon ID

| Value | Type    |
|-------|---------|
| 0     | rifle   |
| 1     | smg     |
| 2     | shotgun |

## Set Score
#### Server->Client

Set a score

| ----------: | -------- |
| Packet ID   | 35       |
| Total Size: | 5 bytes  |

#### Fields

| Field Name | Field Type | Example | Notes           |
| ---------- | ---------- | ------- | --------------- |
| type       | UByte      | `0`     | See table below |
| specifier  | UByte      | `0`     | ^               |
| value      | UShort     | `0`     |                 |

#### Specifiers

| Value | Type             | Specifier      |
|------:|------------------|----------------|
| 0     | SET_TEAM_SCORE   | the team index |
| 1     | SET_PLAYER_SCORE | the player id  |