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
* [Teamplay](#teamplay)

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

## Teamplay

Gathers the features a team needs to play together and a client cannot provide on
its own: seeing teammates through walls, marking a place in the world, being
pointed at a player by the server, and telling one player something without
telling the rest. Each client-side feature is permitted independently by the
server through a feature bitmask, so a server can enable any combination (or
none) of them.

| ---------: |-----|
| Packet ID: | 66  |
| Version:   | 1   |

The extension id, the number carried by `ExtInfo`, is `2`; the packet id is
`64 + extension id` as described in [#Overview](#overview).

#### Sub Packets:

| Sub ID | Name     | Direction         | Size |
|--------|----------|-------------------|------|
| 0      | Config   | Server -> Client  | 3    |
| 1      | Ping     | Client <-> Server | 20+  |
| 2      | ESP Mark | Server -> Client  | 9+   |

A client sends one of these and no other: a **Ping** to point at a place. Config
and ESP Mark are the server speaking; a server that receives either from a client
drops it. Whatever a client sends is a request: the server decides whether it
happens at all, who it reaches, and how it is presented.

### Sub ID 0: Config

The server announces which features are permitted. The server MAY send this
sub-packet at any time; the client applies the new bitmask immediately (for
example to change policy on a map rotation). A feature is only available to the
client while its bit is set.

| Field Name    | Field Type | Example | Notes                                              |
|---------------|------------|---------|----------------------------------------------------|
| Packet ID     | UByte      | `66`    | Always `66`.                                       |
| Sub Packet ID | UByte      | `0`     | Always `0` for this sub-packet.                    |
| Features      | UByte      | `0b110` | Feature bitmask, see below.                        |

Feature bitmask:

| Bit | Name           | Meaning                                                                 |
|-----|----------------|-------------------------------------------------------------------------|
| 0   | `TEAM_ESP`     | Client may render teammates through walls, see [What ESP renders](#what-esp-renders). |
| 1   | `PING_WORLD`   | Client may render received pings as 3D markers in the world.            |
| 2   | `PING_MINIMAP` | Client may render received pings on the minimap.                        |
| 3-7 | reserved       | Must be `0`. Clients must ignore unknown bits.                          |

`TEAM_ESP` only renders teammate positions the client already receives from the
base protocol, so it discloses nothing new; the bit is a fair-play policy toggle,
not a data gate.

`PING_WORLD` and `PING_MINIMAP` are independent and not alternatives. Setting
both — the expected configuration — means the same ping is drawn in the world
*and* on the minimap at once, which is how a marker is both something you turn
towards and something you locate on the map. Either one alone is equally valid:
world only for a server that wants players to look up rather than down, minimap
only for one that wants no marker cluttering the view.

If both `PING_WORLD` and `PING_MINIMAP` are clear the client must not send Ping
packets, and the server must ignore any it receives.

A client always renders what the server sends it, exactly as it always renders
received chat. No bit turns that off; the server simply stops sending.

After the server changes the config, a Ping the client sent before receiving the
new bitmask may still be in transit. The server simply drops such pings; this is
not a protocol violation and needs no special handling.

### Durations

Pings and ESP marks both carry a lifetime, encoded the same way: an `LE float32`
number of seconds, counted by the client from the moment it receives the packet.

| Value             | Meaning                                                             |
|-------------------|---------------------------------------------------------------------|
| `0`               | Remove: clears the ping or the mark this packet refers to.          |
| positive, finite  | Lifetime in seconds, after which the client removes it by itself.   |
| `+inf` (`0x7F800000`) | Stays until the server removes it or the target leaves.         |
| negative, NaN     | Invalid. The receiver drops the packet.                             |

A float because both ends of the range are real: a spotting ping worth 1.5
seconds and an objective marker worth an hour are written the same way, with no
unit to agree on and no rounding.

The point of the encoding is to let a server pick how much work it wants to do. A
server with nothing special in mind sends a finite duration and forgets the whole
thing: no timer, no removal packet, no state. A server that wants a marker to
follow its own logic sends `+inf` and removes it when its logic says so, which is
the on/off behaviour with no extra packet type. Both spellings cost the same four
bytes.

A server keeping `+inf` marks must remember them anyway, if only to send them to
players who join later; a server using finite durations should re-send an active
mark to a joining client with the time that is left, not the time it started
with. Pings are not re-sent: they are events, not state, and a player who was not
there when the ping was made has nothing to catch up on.

Expiry itself is always client-side. A client may cap how many pings and marks it
displays at once, dropping the oldest first, and is never obliged to render an
absurd number of them.

### Sub ID 1: Ping

A single packet used in both directions. A client sends it to ping the world
position its crosshair points at, with the label it wants; the server validates
all of that and relays it to the players of its
choice, filling in the originating Player ID. The server may also originate a
Ping on its own — objective markers, scripted events, admin callouts — with no
client involved. The position uses the same coordinate frame and `LE float32`
encoding as the base protocol position packets. The client's X/Y/Z coordinates
are required: the server uses them to validate that the client and server agree
on the target's position, preventing desync before performing its own raycasting
validation to confirm line-of-sight.

| Field Name    | Field Type | Example     | Notes                                              |
|---------------|------------|-------------|----------------------------------------------------|
| Packet ID     | UByte      | `66`        | Always `66`.                                       |
| Sub Packet ID | UByte      | `1`         | Always `1` for this sub-packet.                    |
| Player ID     | UByte      | `0`         | On relay, the player that pinged. `255` means the ping originated from the server itself. Ignored on the client -> server direction; the server fills it in authoritatively. |
| X             | LE float32 | `256.0`     | World X coordinate.                                |
| Y             | LE float32 | `256.0`     | World Y coordinate.                                |
| Z             | LE float32 | `40.0`      | World Z coordinate.                                |
| Duration      | LE float32 | `5.0`       | Display time, see [Durations](#durations). Server -> client only: a client sends `0` here and the server, which is authoritative, fills it in. |
| Message ID    | UByte      | `0`         | Reserved. Must be `0` in version 1, see below.     |
| Reason        | UTF-8 text | `""`        | Free-form label, the remaining bytes of the packet. |

A player has one active ping at a time: a new ping from the same Player ID
replaces the previous one and restarts its lifetime, and a Duration of `0`
removes it without placing another. The server's own pings (Player ID `255`)
behave the same way, so a server that wants several permanent markers at once
needs ESP marks or a ping per originating id, not several pings from `255`.

A ping always points somewhere: there is no way to send one that means something
without meaning it about a place.

A ping carries no audience. The client has no way to ask for team only, for the
whole server, or for one player, because it has no business knowing: it points at
a place and the server decides who is shown it. The same is true of the label —
a client attaches the label it likes, and the server keeps it, replaces it or
drops the ping entirely.

The label of a ping is a free string. **Message ID** is reserved: version 1 sends
`0` and a receiver drops a packet carrying anything else. The byte is here so
that a later version can name a label instead of spelling it, without moving
where the Reason begins or changing how long it is. It carries the name it will
have then, and reserving it now is what keeps that version additive.

The Reason occupies the remaining bytes of the packet (no length prefix or
terminator); its length is implied by the packet length, and it may be empty,
which is the shortest form of the packet at 20 bytes and a neutral "look here"
marker. It is a free-form, client-defined UTF-8 string, consistent with the
[UTF-8 Chat](#utf-8-chat) convention. Before relaying, the server must validate
it as well-formed UTF-8 and drop (or sanitise) anything malformed rather than
forwarding bytes verbatim. The server should cap its length, truncating on a
codepoint boundary if needed. Clients render the string as received and fall back
to a neutral marker for anything they do not recognise.

A Reason says anything a player wants said — a place name, a plan, a joke. The
cost is that **free text falls out of translation**: it travels as the bytes the
sender wrote, and every reader sees those same bytes in the sender's language,
however many of them speak it. A server that wants a room where everybody
understands everybody can clear the Reason and relay the marker alone.

A dead player does not ping. A client must not send a Ping while its player is
dead, and the server drops any it receives from a dead player, exactly as it
drops one sent while the feature is switched off. Waiting to respawn is not a
vantage point, and a corpse pointing at things the living cannot see is a way of
spectating the enemy. Whether spectators may ping is the server's call.

To identify the target of a ping, the server performs a raycasting check from the
client's position through their crosshair direction using the X/Y/Z coordinates
sent by the client to validate sync and confirm line-of-sight, rather than
relying on client data to identify the target.

Server handling of a client -> server Ping:

* The server should rate-limit requests (a sane default is at most one per player
  per second).
* The label a client asks for is a request like the rest: the server may replace
  it, empty it, or drop the ping over it.
* The server must validate the coordinates by comparing them against its own state
  for the pinged player (at least the map bounds of 512 x 512 x 64, and the
  player's actual position for sync checking). The server should reject pings to
  positions that diverge significantly from its own tracked state.
* Who receives the relayed Ping is left to the server's discretion (team only,
  everyone, spectators, etc.); the protocol does not mandate a distribution
  policy. Relaying it to nobody is a valid decision too.

How long a ping stays is the server's call alone, never the pinging client's:
Duration is only meaningful on the relay. A client asks for a ping, the server
decides what that ping is worth — `5.0` seconds is the conventional value and
what a server with no opinion should send, while a server building something of
its own can make a ping last a round or vanish in half a second, without the
client needing to know that policy or the server needing a removal packet.

### Sub ID 2: ESP Mark

Marks a player as visible through walls to whoever receives the packet. Unlike
`TEAM_ESP`, which lets a client reveal its own team on its own initiative, a mark
is decided by the server, targets one player, and is unrelated to teams: the
server can reveal a player to their own team, to the other team, to everyone, or
to a single player. That covers spotting the scoreboard leader, showing a hunted
player to the hunters, exposing a cheater to the whole server, or a game mode that
reveals a carrier while they hold the intel.

This sub-packet travels **server -> client only**. Unlike the Ping and the
Message, it has no client-sent form: a client never asks for a mark and never
sends sub-packet `2`. A server receiving it from a client must drop it, since the
only thing such a packet can be is an attempt to reveal a player to somebody the
server did not choose.

| Field Name    | Field Type | Example    | Notes                                          |
|---------------|------------|------------|------------------------------------------------|
| Packet ID     | UByte      | `66`       | Always `66`.                                   |
| Sub Packet ID | UByte      | `2`        | Always `2` for this sub-packet.                |
| Player ID     | UByte      | `7`        | The player to reveal.                          |
| Duration      | LE float32 | `10.0`     | Lifetime, see [Durations](#durations).         |
| Flags         | UByte      | `0b1`      | Lifetime modifiers, see below.                 |
| Message ID    | UByte      | `0`        | Reserved, as on the [Ping](#sub-id-1-ping). Must be `0`. |
| Reason        | UTF-8 text | `"leader"` | Free-form label, the remaining bytes of the packet. |

Flags:

| Bit | Name               | Meaning                                                                     |
|-----|--------------------|-----------------------------------------------------------------------------|
| 0   | `CLEAR_ON_RESPAWN` | The mark ends the next time the marked player spawns.                       |
| 1   | `SHOW_NAME`        | The client shows the marked player's name. Clear, it shows the outline alone.|
| 2-7 | reserved           | Must be `0`. Clients must ignore unknown bits.                              |

`CLEAR_ON_RESPAWN` is keyed to the spawn rather than to the death: any
[Create Player](protocol075.html#create-player) for that id ends the mark,
whether the player was killed, changed team, changed weapon or was moved by a
script, and the client needs no death bookkeeping to implement it. A mark on a
player who dies and stays dead lasts until they come back, which is what
"reveal them until they get away" wants anyway.

`SHOW_NAME` is the server's call, not the client's, because only the server knows
what it is revealing. Marking the scoreboard leader for their own team is worth a
name; marking an enemy for the team hunting them may not be, when the outline
says where and the name would hand over who. A client shows the name when the bit
is set and must not when it is clear — a mark is an instruction, and this part of
it is no different.

Duration and the lifetime flag are independent, so every lifetime a server is
likely to want falls out of the same five bytes:

| Intent                                      | Duration | Flags              |
|---------------------------------------------|----------|--------------------|
| Reveal for a while                          | `3.5`    | `0`                |
| Reveal until the server clears it           | `+inf`   | `0`                |
| Reveal until they respawn                   | `+inf`   | `CLEAR_ON_RESPAWN` |
| Reveal for a while, or until they respawn   | `3.5`    | `CLEAR_ON_RESPAWN` |
| Clear the mark now                          | `0`      | `0`                |

`SHOW_NAME` is orthogonal to all of these and may be set with any of them.

The label works exactly as on a Ping, Message ID reserved and Reason following
the same rules — remaining bytes of the packet, no length prefix or terminator,
validated by the server as well-formed UTF-8, capped and truncated on a codepoint
boundary — and the client falls back to a neutral highlight for anything it does
not recognise. An empty Reason is valid and is the common case: the packet is
then 9 bytes and the client shows the player highlighted with no label.
`"cheater"`, `"leader"` and `"carrier"` are examples, not assigned values.

The audience is the set of clients the server sends the packet to; there is no
audience field. A field would have to be enforced by the client, and a client
that ignores it would reveal players it was never meant to see — the same reason
the Ping relay leaves distribution to the server. It also means a player is not
told they are being revealed to others unless the server includes them in the
recipients, which is what the punishment case wants; a client that receives a
mark for its own player id may show it as a "you are marked" indicator.

A mark is an instruction rather than a permission, so the client renders it
whatever the `TEAM_ESP` bit says, and marks are not gated by the Config bitmask.
A client with `TEAM_ESP` clear still shows a marked teammate.

#### What ESP renders

The two paths are not held to the same rendering, because one is the client
showing its own team and the other is the server pointing at somebody.

`TEAM_ESP` is left to the client: a body outline, a box around the player, a
chevron above them, a dot on the edge of the screen — whatever the client
considers good practice — as long as it is drawn in that player's team colour,
the one the server sent in [State Data](protocol075.html#state-data), so the
highlight reads as team information at a glance. Showing the name alongside is
recommended and also the client's call.

An **ESP Mark must draw the player's body outline through walls**, following the
body and its pose rather than standing in for it with a box, a dot or a floating
marker. The server marked one specific player, and the audience has to see where
exactly they are, not merely that somebody is around there.

Whether the name goes with it is the server's decision, carried by the
`SHOW_NAME` flag: set, the client shows the marked player's name; clear, it shows
the outline and nothing else. A mark has no imposed colour, though — the client
is free to distinguish it from a plain teammate highlight, which is also what the
label is there for.

The rest is the client's business in both cases: outline thickness, opacity,
whether the highlight fades with distance, and how the label is rendered beside
it, if at all.

Marks are state held per player id, and one mark per player: a new mark replaces
the previous one and restarts its timer. A mark is dropped when its Duration
expires, when a mark with Duration `0` arrives for that id, when its target
spawns and `CLEAR_ON_RESPAWN` is set, or under the general rules of
[Per-player state](#per-player-state). Without `CLEAR_ON_RESPAWN` it survives
death and respawn, so a punishment mark does not have to be re-sent every time
its target is killed.

### Direct chat

A chat type this extension adds to the base
[Chat Message](protocol075.html#chat-message) packet, for a line the server sends
to one player alone.

| Value | Name          | Lands as                                                            |
|-------|---------------|---------------------------------------------------------------------|
| 7     | `CHAT_DIRECT` | A message to the receiving client alone, rendered as a private one. |

The packet needs no new field for it: it already carries the sender in its Player
ID — `255` for the server itself — and the recipient is the client it was sent
to.

Server -> client only, and a server sends it only to a client that negotiated
this extension; for the rest it uses `2` (CHAT_SYSTEM) or whatever private form
it already has. A client never sends `7`, and asks for a private message the way
its server already provides. A client renders it wherever it already shows a
private message and adds nothing new.

This is the same shape as [Message Types](#message-types), which adds `3`-`6` to
the same packet and is negotiated the same way.

### Per-player state

Everything this extension creates belongs to a player id, and all of it is freed
the moment that player leaves. When a client receives
[Player Left](protocol075.html#player-left) for an id it drops, for that id: the
player's active ping and the ESP mark on them if any. The server drops the same
things on its side and stops referring to the id.

The reason is that ids are recycled. A mark or a ping outliving its owner does
not fade away quietly — it lands on whoever takes the id next, and that player is
suddenly revealed to the enemy team, or pinned to a marker they never made.

A map change ([Map Start](protocol075.html#map-start-075)) clears everything for
every id, on both ends. Nothing this extension holds is meant to survive a world.


# Extensions Without New Packet Types
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