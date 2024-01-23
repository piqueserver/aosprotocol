## Extension Negotiation Packet

### Overview

Each extension is given a unique ID that is decided when it is first
registered. We differentiate between two types of extensions:

| Type          | Purpose                               | Extension id range |
| ------------- | ------------------------------------- | ------------------ |
| `HAS_PACKETS` | Introduce new packets to the protocol | 0-191              |
| `PACKETLESS`  | Don't have any packets                | 192-255            |

Each extension is given one legacy packet ID equal to `64+extension_id`.
For a `PACKETLESS` extension this would mean that its packet ID is out
of range for the UByte used to store IDs (UByte values range from 0 to 255).
Therefore, it cannot support packets. An example of a `PACKETLESS` extension
would be the [Message Types](https://github.com/piqueserver/aosprotocol/issues/14)
extension, with an extension ID of 193. Note that OpenSpades' UTF-8 extension
used to be here as the example, but this extension actually does not use
`ExtInfo`! Instead, UTF-8 encoded messages are prefixed with a 0xFF byte.

Each extension packet contains 1 byte in its data after the packet ID, which is a
subpacket ID that used to have multiple packets available for each extension. This
is always the case, even if an extension only needs 1 packet in total. The reason
for this is unknown, considering the version of all extensions supported by either
the client OR the server are specified in the `ExtInfo` transaction, which should
make it easily possible to tell if the extension is a version that needs more than
one packet or not.

General extension packet structure:

| Field name   | Type      | Notes          |
| ------------ | --------- | -------------- |
| Packet ID    | UByte     | 64-255         |
| Subpacket ID | UByte     | 0-255          |
| Data         | UByte[]   | Extension data |

### ExtInfo Packet

* Packet ID: 60
* Total size: `2+2*Length`

| Field name | Field type   | Notes                        |
| ---------- | ------------ | ---------------------------- |
| Length     | UByte        | `Length` entries will follow |
| Entries    | ExtInfoEntry | See below                    |

**ExtInfoEntry**

| Field name | Field type | Notes               |
| ---------- | ---------- | ------------------- |
| Ext. ID    | UByte      | See #Overview       |
| Version    | UByte      | Usually starts at 1 |

## Protocol Flow

The server should send an `ExtInfo` packet (optimally) after the Version Info response has been received and checked to be from a compatible client
(OpenSpades versions > 0.1.3, see https://github.com/piqueserver/piqueserver/issues/504),
assuming the server supports any. The client can store the list of extensions for later use and should
reply with an `ExtInfo` packet that lists the extensions *it* supports (if it does actually support any).

The client can omit any extensions that the server does not support from its
reply, but this is not necessary as the server can simply ignore them itself.


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