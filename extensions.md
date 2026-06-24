## Extension Negotiation Packet

### Overview

Each extension is given an unique id that is decided when it is first
registered. We differentiate between two types of packets:

*Those that:*

| Type          | Purpose                               | Extension id range |
| ------------- | ------------------------------------- | ------------------ |
| `HAS_PACKETS` | introduce new packets to the protocol | 0-191              |
| `PACKETLESS`  | don't use and need any packets        | 192-255            |

Each extension is given one legacy packet id equal to `64+extension_id`.
For `PACKETLESS` extensions this would mean that their packet ids are out
of spec `>255`, thus they don't have any.
An example for a packetless extension would be *OpenSpades'* UnicodeExt.

Each extension packet will contain 1 additional byte in its data, which is a
subpacket id, used to have multiple packets available for each extension. This
is always the case, even if an extension only needs 1 packet in total.

General extension packet structure:

| Field name    | Type      | Notes          |
| ------------- | --------- | -------------- |
| Packet id     | UByte     | 64-255         |
| Sub packet id | UByte     | 0-255          |
| Data          | UByte[]   | extension data |

### ExtInfo Packet

* Packet ID: 60
* Total size: `2+2*length`

| Field name | Field type   | Notes                        |
| ---------- | ------------ | ---------------------------- |
| length     | UByte        | `length` entries will follow |
| entries    | ExtInfoEntry | see below                    |

**ExtInfoEntry**

| Field name | Field type | Notes               |
| ---------- | ---------- | ------------------- |
| ext. ID    | UByte      | see #Overview       |
| version    | UByte      | Usually starts at 1 |

## Protocol Flow

The server should send an `ExtInfo` packet (optimally) after the Version Info response has been received to compatible clients
(OpenSpades versions > 0.1.3, see https://github.com/piqueserver/piqueserver/issues/504),
assuming it supports any. The client can store the list of extensions for later use and should
reply with an `ExtInfo` packet that lists the extensions it supports (if it does actually support any).

The client can omit any extensions that the server does not support from its
reply, but this is not necessary as the server can simply ignore them itself.


# HAS_PACKETS Packets
* [Player Properties](#player-properties)

## Player Properties

Sends additional player attributes from the server to the client.

| ---------: |-----|
| Packet ID: | 64  |
| Version:   | 1   |

| Sub ID | Name              | Direction        | Size |
|--------|-------------------|------------------|------|
| 0      | Player Properties | Server -> Client | 12   |

### Sub ID 0: Player Properties

The server sends this packet to inform the client of authoritative stats for
a single player. There is no client-to-server form. The 12-byte total
includes the Packet ID and Sub Packet ID as described in the
[general extension packet structure](#overview).

| Field Name    | Field Type | Example | Notes                                                                                                     |
|---------------|------------|---------|-----------------------------------------------------------------------------------------------------------|
| Packet ID     | UByte      | `64`    | Always `64`.                                                                                              |
| Sub Packet ID | UByte      | `0`     | Always `0` for this sub-packet.                                                                           |
| Player ID     | UByte      | `0`     | The id of the player these stats describe.                                                                |
| HP            | UByte      | `100`   | Health. A `UByte`, so the wire range is `0`..`255`; vanilla servers use `0`..`100`. Whether `0` HP marks the player as dead is client-specific (betterspades does not — the kill packet is authoritative for death; openspades does, but does not support this packet). |
| Blocks        | UByte      | `50`    | Block count currently carried by the player. Typically `0`..`50` for vanilla servers.                     |
| Grenades      | UByte      | `3`     | Grenade count currently carried by the player. Typically `0`..`3` for vanilla servers.                    |
| Magazine Ammo | UByte      | `10`    | Ammunition currently loaded in the player's equipped weapon clip.                                         |
| Reserve Ammo  | UByte      | `50`    | Spare ammunition the player has for the equipped weapon (outside the clip).                               |
| Score         | LE Uint    | `7`     | The player's score, as defined by the server (e.g. kills, or kills plus objective points). 32-bit little-endian integer. Reference clients treat it as unsigned (BetterSpades, KyroSpades); zerospades reads it into a signed `int`. Signedness is only observable for values >= 2^31. |

Byte layout (offsets are within the packet, including the Packet ID byte):

| Offset | Size | Field         |
|--------|------|---------------|
| 0      | 1    | Packet ID     |
| 1      | 1    | Sub Packet ID |
| 2      | 1    | Player ID     |
| 3      | 1    | HP            |
| 4      | 1    | Blocks        |
| 5      | 1    | Grenades      |
| 6      | 1    | Magazine Ammo |
| 7      | 1    | Reserve Ammo  |
| 8      | 4    | Score         |


# Packetless Packets
* [Player Limit](#player-limit)
* [Message Types](#message-types)
* [Kick Reason](#kick-reason)

## Player Limit

Tells client server supports up to 256 players.

| ---------: |-----|
| Packet ID: | 192 |
| Version:   | 1   |

## Message Types

This packet is an extension to the [Chat Message](protocol075.html#chat-message), it adds new chat types.
So clients can handle it how they want, in most clients it will display the message in different area/size/color/sound in
player's screen.

| ---------: |-----|
| Packet ID: | 193 |
| Version:   | 1   |

#### New Types:

| Value | Type         | Notes                                 |
|-------|--------------|---------------------------------------|
| 3     | CHAT_BIG     | Displayed on the center of the screen |
| 4     | CHAT_INFO    | Displays a notice                     |
| 5     | CHAT_WARNING | Displays a warning                    |
| 6     | CHAT_ERROR   | Displays a error                      |

## Kick Reason

Send a [Chat Message](protocol075.html#chat-message) with type 2 (CHAT_SYSTEM) and player id 255, before
kicking a player out of the server.

| ---------: |-----|
| Packet ID: | 194 |
| Version:   | 1   |

# Other Extensions
* [UTF-8 Chat](#utf-8-chat)

## UTF-8 Chat

Has no registered extension id. A [Chat Message](protocol075.html#chat-message)
whose data starts with a `0xff` byte is encoded in UTF-8 instead of Code Page
437. Messages without the prefix are interpreted as Code Page 437 as in the
base protocol.