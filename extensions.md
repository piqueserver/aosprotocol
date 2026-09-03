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
pointed at a player by the server, and saying a short thing to the team in a
language every player reads in their own. Each client-side feature is permitted
independently by the server through a feature bitmask, so a server can enable any
combination (or none) of them.

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
| 3      | Message  | Client <-> Server | 6+   |

A client sends two of these and no others: a **Ping** to point at a place, and a
**Message** to say one of the [predefined messages](#predefined-messages). They
are separate packets because they are separate acts — a message is not a marker
that happens to carry words, and most of the catalogue points at nothing. A
message id may also label a Ping, which is the marker being named, not a second
way of speaking.

Config and ESP Mark are the server speaking; a server that receives either from a
client drops it. Whatever a client sends is a request: the server decides whether
it happens at all, who it reaches, and how it is presented.

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
| 3   | `QUICK_CHAT`   | Client may send Message packets, which is its quick chat menu.          |
| 4-7 | reserved       | Must be `0`. Clients must ignore unknown bits.                          |

`TEAM_ESP` only renders teammate positions the client already receives from the
base protocol, so it discloses nothing new; the bit is a fair-play policy toggle,
not a data gate.

`PING_WORLD` and `PING_MINIMAP` are independent and not alternatives. Setting
both — the expected configuration — means the same ping is drawn in the world
*and* on the minimap at once, which is how a marker is both something you turn
towards and something you locate on the map. Either one alone is equally valid:
world only for a server that wants players to look up rather than down, minimap
only for one that wants no marker cluttering the view.

Each of the two client-sent packets has its own switch. If both `PING_WORLD` and
`PING_MINIMAP` are clear the client must not send Ping packets, and the server
must ignore any it receives; if `QUICK_CHAT` is clear the same goes for Message
packets. A server can therefore run pings without quick chat, quick chat without
pings, or neither.

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

### Message parameters

Some [predefined messages](#predefined-messages) are templates rather than fixed
sentences: *"There are `%1$i` of them"* is one phrase that says any number. The
values fill the template at the far end, after translation, so a parameter costs
nothing in understanding — a French player sends `16` and a `3`, and a Japanese
player reads *"敵は3人だ"*.

| Marker | Field Type | Size | Renders as                                                      |
|--------|------------|------|-----------------------------------------------------------------|
| `%i`   | LE int32   | 4    | The number.                                                     |
| `%f`   | LE float32 | 4    | The number, formatted by the client's own locale.               |
| `%p`   | UByte      | 1    | The name of that player id, which the receiving client already has. |

None of them is text. That is the whole point of the set: a number is a number in
every language, and `%p` travels as a player id the receiver already has a name
for, so a parametric message is still something every client reads in its own
language, and still something a client cannot smuggle words through.

Version 1 defines no entry that uses `%f`. The type is defined here so a later
version can add one without changing the wire format; a version 1 implementation
never encounters it.

#### On the wire

A message id fixes its own parameters: how many, of which types, in which order.
Both ends know them from the catalogue, so nothing describes them on the wire —
the values follow one another raw, in the order the template declares, with no
count, no type tags and no padding.

That signature is **as frozen as the text is**. A later version of this extension
may never add a parameter to an existing id, remove one, or change its type; it
allocates a new id instead. A version 1 client parsing a version 2 packet has
only the id to go on, and it has to be right.

Where the values go depends on the packet, and follows the Message ID that
selects the template:

| Packet                          | Message ID `0`                      | Message ID not `0`                |
|---------------------------------|-------------------------------------|-----------------------------------|
| [Ping](#sub-id-1-ping)          | Remaining bytes are `Reason`.       | Remaining bytes are the values.   |
| [ESP Mark](#sub-id-2-esp-mark)  | Remaining bytes are `Reason`.       | Remaining bytes are the values.   |
| [Message](#sub-id-3-message)    | Not valid, see the packet.          | Remaining bytes are the values.   |

An id with no parameters is followed by nothing, which is why an ordinary Message
is still 6 bytes. No entry may take more than four parameters, and none in
version 1 takes more than one.

#### In the catalogue text

The id is the translation key. The canonical English is the reference rendering
of the entry — what a translator works from, and what a peer without the
extension receives — and it is where an entry's parameters are declared: how
many, of which types, in which order they arrive on the wire.

Markers are written positionally — `%1$i` is the first value, `%2$p` the second —
because word order is not the same in every language and a translation has to be
free to move them. No version 1 entry takes more than one parameter, so nothing
yet needs reordering; the notation is fixed now so that a later version adding a
two-value entry does not have to change how translations are written.

A literal percent sign is written `%%`. This applies to catalogue text only: a
`Reason` string is free text, never a template, and a `%` in it is always a
percent sign.

Grammar around a value is the translation's business, not the protocol's. A
client applies its own language's plural rules to the value it substitutes; the
canonical English is one rendering of the phrase, not a form every language has
to bend into. The catalogue phrasings avoid the problem where they can.

#### Validation

The values are as authoritative as the id. A server validates them before it
relays anything, and a client validates them before it renders anything:

* The block must match the id's signature exactly. Too few bytes and too many
  bytes are both invalid, and the packet is dropped rather than parsed leniently.
* `%f` is invalid if NaN or infinite, as in [Durations](#durations).
* `%p` must name a player currently in the game; the packet is dropped otherwise.
* A server should clamp `%i` and `%f` to a range its game can mean. A client
  asking to announce two billion enemies is a client to be ignored, the same way
  a ping to an impossible coordinate is.

A server that does not know a newer id cannot validate its values and does not
try: unknown ids are not relayed, as before.

### Sub ID 1: Ping

A single packet used in both directions. A client sends it to ping the world
position its crosshair points at, naming the player it is aiming at and the label
it wants; the server validates all of that and relays it to the players of its
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
| Message ID    | UByte      | `33`        | [Predefined message](#predefined-messages) the ping carries, `0` for none. |
| Reason        | UTF-8 text | `""`        | Free-form label, used only when Message ID is `0`. |
| Arguments     | varies     | —           | Values for the Message ID's parameters, used only when Message ID is not `0`. See [Message parameters](#message-parameters). |

A player has one active ping at a time: a new ping from the same Player ID
replaces the previous one and restarts its lifetime, and a Duration of `0`
removes it without placing another. The server's own pings (Player ID `255`)
behave the same way, so a server that wants several permanent markers at once
needs ESP marks or a ping per originating id, not several pings from `255`.

A ping always points somewhere. A player who wants to say something without
pointing at anything sends a [Message](#sub-id-3-message) instead — that is what
it is for, and it is why the two are separate packets.

A ping carries no audience. The client has no way to ask for team only, for the
whole server, or for one player, because it has no business knowing: it points at
a place and the server decides who is shown it. The same is true of the label —
a client attaches the id it likes, and the server keeps it, replaces it or drops
the ping entirely.

The label of a ping is either a catalogue id or a free string, and the two share
the tail of the packet. When Message ID is not `0` the client renders the
[predefined message](#predefined-messages) for that id, translated, and the
remaining bytes are that id's [parameter values](#message-parameters) — nothing
at all for the great majority of ids, which take none. When Message ID is `0` the
client renders the remaining bytes as Reason, and an empty Reason is a neutral
"look here" marker.

Which id a client attaches to a ping is the client's own business. The catalogue
groups its entries by what they usually mean, not by what may label a marker, and
this extension puts no restriction on the combination. The one thing a client may
not do is invent ids: only the ones the catalogue defines.

The Reason occupies the remaining bytes of the packet when Message ID is `0` (no
length prefix or terminator); its length is implied by the packet length, and it
may be empty, which is the shortest form of the packet at 20 bytes. It
is a free-form, client-defined UTF-8 string, consistent with the
[UTF-8 Chat](#utf-8-chat) convention. Before relaying, the server must validate
it as well-formed UTF-8 and drop (or sanitise) anything malformed rather than
forwarding bytes verbatim. The server should cap its length, truncating on a
codepoint boundary if needed. Clients render the string as received and fall back
to a neutral marker for anything they do not recognise.

A client is free to ping with a Reason it typed rather than a catalogue id, and
the field exists precisely so that anything the catalogue does not cover can
still be said — a place name, a plan, a joke, a language the catalogue was never
going to hold. The cost is that **free text falls out of translation**: it
travels as the bytes the sender wrote and every reader sees those same bytes,
in the sender's language, however many of them speak it. A catalogue id is read
by each player in their own language; a Reason string is read by whoever happens
to share the writer's. Clients should prefer an id whenever one fits, and servers
that want a room where everybody understands everybody can clear the Reason and
keep the id.

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
* The label a client asks for (Message ID and its
  [parameter values](#message-parameters), or Reason).
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
| Message ID    | UByte      | `0`        | [Predefined message](#predefined-messages) labelling the mark, `0` for none. |
| Reason        | UTF-8 text | `"leader"` | Free-form label, used only when Message ID is `0`. |
| Arguments     | varies     | —          | Values for the Message ID's parameters, used only when Message ID is not `0`. See [Message parameters](#message-parameters). |

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

The label works exactly as on a Ping: a non-zero Message ID renders the
[predefined message](#predefined-messages) for that id, translated, and the
remaining bytes are that id's [parameter values](#message-parameters) rather than
a Reason. Otherwise the client renders Reason, which follows the Ping's rules —
remaining bytes of the packet, no length prefix or terminator, validated by the
server as well-formed UTF-8, capped and truncated on a codepoint boundary — and
falls back to a neutral highlight for anything it does not recognise. Both empty
is valid and is the common case: the packet is then 9 bytes and the client shows
the player highlighted with no label.

A Reason is for a label the catalogue has no id for. Where it has one — the
single-word entries at [208-223](#singling-out-a-player) exist for exactly this
job — a server sends the id instead, so that the label arrives translated rather
than in the server's language.

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

### Sub ID 3: Message

Says one of the [predefined messages](#predefined-messages) by its catalogue id.
This is how a player speaks: the client sends the id it wants, the server decides
what to do with it and relays it to the players it chooses. Clients that support
the extension translate the id themselves in their own language; clients without
the extension receive the canonical English text as fallback.

A single packet used in both directions, as for the Ping. Nothing but ids and
numbers travels here — there is no text field at all, so a client cannot smuggle
words through it, and everything it can say is something every other client can
already read.

| Field Name    | Field Type | Example | Notes                                                                   |
|---------------|------------|---------|---------------------------------------------------------------------------|
| Packet ID     | UByte      | `66`    | Always `66`.                                                              |
| Sub Packet ID | UByte      | `3`     | Always `3` for this sub-packet.                                           |
| Player ID     | UByte      | `4`     | On relay, the player speaking; `255` means the server itself. Ignored on the client -> server direction; the server fills it in authoritatively. |
| Target ID     | UByte      | `9`     | The player the message is addressed to, `255` for nobody in particular. Set by the client. |
| Chat Type     | UByte      | `1`     | Where the message lands, see below. Server -> client only: a client sends `0` and the server assigns it. |
| Message ID    | UByte      | `52`    | Catalogue id, `1`-`255`. `0` must not be sent; Message packets require a predefined message. |
| Arguments     | varies     | —       | Values for the Message ID's parameters, empty for an id that takes none. See [Message parameters](#message-parameters). |

**Target ID** determines the message channel: a specific player ID sends a direct message to that player; `255` sends a team message that the server relays only to the team. The server decides whether to relay the message.

**Chat Type** is how the message reaches the player, and the server is the only
one who chooses it. A client asks to say something; it does not decide whether
its words reach its team, the whole server, or one player, any more than it
decides who sees its pings. The values are those of the base
[Chat Message](protocol075.html#chat-message) packet, plus the
[Message Types](#message-types) ones and one this extension adds:

| Value | Name           | Lands as                                                     |
|-------|----------------|--------------------------------------------------------------|
| 0     | `CHAT_ALL`     | A global chat line.                                          |
| 1     | `CHAT_TEAM`    | A team chat line.                                            |
| 2     | `CHAT_SYSTEM`  | A server line.                                               |
| 3-6   | Message Types  | Big, info, warning, error — the coloured and centred forms.  |
| 7     | `CHAT_DIRECT`  | A message to the Target ID alone, rendered as a private one. |

Values `3`-`6` need the [Message Types](#message-types) extension; a server sends
them only to clients that negotiated it and downgrades to `2` (CHAT_SYSTEM) for the
rest. `7` is this extension's own, and a client that negotiated it has already
said it understands the value.

`7` is equally valid on the base [Chat Message](protocol075.html#chat-message)
packet, which is how a server sends a private line of free text: that packet
carries the sender in its Player ID and the recipient is the client it was sent
to, so nothing else is needed. Both packets follow the same rule as `3`-`6` —
server -> client only, sent only to a client that negotiated this extension, `2`
or the server's existing private form for the rest. A client never sends `7` in
either packet, and asks for a private message the way its server already
provides.

A client renders each type where its existing chat already puts it — a chat line
in the chat window, `3`-`6` in whatever alert or centre-screen view it uses for
them, `7` wherever it shows a private message — and adds nothing new. The
extension changes what travels on the wire, not where a message appears on
screen.

The packet is 6 bytes and carries no text: the id *is* the message. That is the
whole point, and it is why a message costs 6 bytes where the same sentence costs
20 to 60 as chat. The few ids that take
[parameters](#message-parameters) add their values to that — four bytes for a
number, one for a player — so *"there are 3 of them"* is 10 bytes and
*"Ana has the intel"* is 7, and neither is a string.

#### English fallback

The catalogue is normative on both ends, so either side can always fall back to
words when its peer cannot speak in ids:

* **Server without the extension.** The client has no Message packet to send, so
  its quick chat sends the [canonical English text](#predefined-messages) as an
  ordinary [Chat Message](protocol075.html#chat-message) — which is what such a
  menu does today anyway. Nothing is lost but the translation.
* **Client without the extension.** The server sends that client an ordinary Chat
  Message containing the canonical English text, with the base chat type matching
  what it chose, so the line still appears in the right place and colour. A
  `CHAT_DIRECT` message becomes whatever private form that server already uses.
* **Client with an older version of the extension.** `ExtInfo` carries a version
  per extension, so the server knows a client's catalogue. Ids beyond it are sent
  to that client as English text rather than as a Message packet.

Whoever writes the fallback line fills the template in: a server sending an id
with [parameters](#message-parameters) to a client that cannot receive one
substitutes the values into the canonical English itself, rendering `%p` as the
player's name, and sends the finished sentence. A client falling back the other
way does the same with the values it was about to send.

Canonical strings are pure ASCII, so the fallback survives the base protocol's
CP437 chat encoding without needing the [UTF-8 Chat](#utf-8-chat) convention. A
substituted player name is the exception and is not ASCII in general; a server
encodes such a line as its chat encoding requires, which is the same problem the
name already poses everywhere else it appears.

A client that receives an id it does not know renders nothing for it. It must not
invent a placeholder line, and it must not disconnect.

#### Server handling

* Rate-limit messages as you rate-limit chat. A menu makes them cheap to spam;
  a sane default is the chat limit.

### Predefined messages

The catalogue is a fixed table of short phrases, each with a one byte id. A
client sends the id — in a Message, or as the label of a Ping — and the server
relays it to other clients. A few of the phrases are templates that take
[parameters](#message-parameters), and the values travel with the id. Clients that support the extension translate the id
in their own language; the canonical English text below is what clients without
the extension receive as fallback, and what goes on the wire when a peer does not
support the extension.

The table is the same for everybody, which is the only reason this works: a
French player sends `52`, a Japanese player reads *"援護してくれ"*, and neither
client learned anything from the other. It also means **ids are frozen forever**.
Version 1 of this extension defines the ids below; a later version may only
append into the reserved space. An id is never renumbered and never reused for
another meaning, because clients record demos of games they replay years later.

The entries are chosen for how Ace of Spades is actually played — blocks run out,
spades dig, tents restock, intel gets carried, and someone is always digging under
someone — rather than translated from a generic shooter. Ids are grouped in blocks
of sixteen, and each block keeps its tail free so a later version can extend a
category without scattering it. Ids not listed here are reserved and must not be
sent.

Id `0` is not a message. It is the "no message" value the Ping and ESP Mark
packets use, and it must never appear in a Message packet.

#### 1-15 — Answers and courtesy

| Id | English text | Id | English text |
|----|--------------|----|--------------|
| 1  | Yes          | 9  | Hello        |
| 2  | No           | 10 | Good game    |
| 3  | Affirmative  | 11 | Nice shot    |
| 4  | Negative     | 12 | Well played  |
| 5  | Understood   | 13 | Wait         |
| 6  | Thank you    | 14 | Ready        |
| 7  | Sorry        | 15 | Not ready    |
| 8  | My bad       |    |              |

#### 16-31 — Parametric messages

Where a [parametric](#message-parameters) entry goes when it belongs to no one
category in particular. An entry that clearly belongs to a category stays with it
— [208-223](#singling-out-a-player) and [224-239](#server-notices) below carry
their own — and the Parameters column declares the signature wherever it appears.

| Id | English text            | Parameters   |
|----|-------------------------|--------------|
| 16 | There are %1$i of them  | `%i`         |
| 17 | %1$i enemies left       | `%i`         |
| 18 | I need %1$i more        | `%i`         |
| 19 | %1$p has the intel      | `%p`         |
| 20 | Follow %1$p             | `%p`         |
| 21 | Cover %1$p              | `%p`         |
| 22 | Help %1$p               | `%p`         |
| 23 | Enemy at %1$i o'clock   | `%i`         |
| 24 | Target at %1$i o'clock  | `%i`         |
| 25 | Enemy at %1$i degrees   | `%i`         |
| 26 | %1$i minutes remain     | `%i`         |
| 27 | %1$i seconds remain     | `%i`         |
| 28-31 | reserved             |              |

There is deliberately no entry that is only a number. A bare `7` is not a thing
anybody says; it is an answer to a question the catalogue cannot see, and a
listener who missed the question reads nothing at all. *"There are 7 of them"*
says the same thing on its own, in one id, for any number — which is what a table
of the digits `1` to `10` was reaching for and could not hold.

`I need %1$i more` names no object on purpose. What is needed is what the player
is short of, and the ping or the situation says which; an id per resource would
be a row of near-identical entries that translate no better.

The `%p` entries are the only way this catalogue names anybody. Everything else
in it is first or third person — `Follow me`, `Cover me`, `I have the intel`,
`They have our intel` — and a player who wants to say *who* has had no id for it
and has had to fall back to chat, in their own language, which is the thing this
extension exists to avoid.

The three bearing entries are read against the **sender**, like the
[64-79](#directions-relative-to-the-sender) block and unlike the
[48-63](#directions-relative-to-the-addressed-player) one: `12` o'clock is where
the sender is looking, `3` is their right, and a bearing in degrees is a compass
reading on the map, `0` at north and rising clockwise. A server clamps the clock
entries to `1`-`12` and the degree one to `0`-`359`, as
[Validation](#validation) requires of any `%i`.

#### 32-47 — Enemy contact

| Id | English text    | Id | English text              |
|----|-----------------|----|---------------------------|
| 32 | Enemy spotted   | 39 | They are pushing          |
| 33 | Enemies here    | 40 | They are flanking         |
| 34 | Enemy sniper    | 41 | Spawnkiller!              |
| 35 | Enemy camping   | 42 | Clear                     |
| 36 | Enemy tunneling | 43 | All clear                 |
| 37 | Enemy building  | 44 | They are digging under us |
| 38 | Enemy tower     | 45 | Enemy in our base         |
|    |                 | 46 | We got a digger           |

#### 48-63 — Directions, relative to the addressed player

These are read against the **Target ID** of the message: "you" is that player, and
the direction is the one they are facing.

| Id | English text  | Id | English text     |
|----|---------------|----|------------------|
| 48 | Behind you    | 53 | In front of you  |
| 49 | On your left  | 54 | They see you     |
| 50 | On your right | 55 | Watch your back  |
| 51 | Above you     | 56 | Look behind you  |
| 52 | Below you     |    |                  |

#### 64-79 — Directions, relative to the sender

These are read against the sender, the **Player ID** of the message. Splitting the
two families is deliberate: "on the right" is the oldest ambiguity in team games,
and here the id itself says whose right it is.

| Id | English text   | Id | English text    |
|----|----------------|----|-----------------|
| 64 | Behind us!     | 71 | They are below  |
| 65 | On our left    | 72 | Over there      |
| 66 | On our right   | 73 | Up there        |
| 67 | Above us       | 74 | Down there      |
| 68 | Below us       | 75 | Everywhere!     |
| 69 | In front of us | 76 | Right here      |
| 70 | They are above |    |                 |

#### 80-95 — Requests

| Id | English text   | Id | English text     |
|----|----------------|----|------------------|
| 80 | Help me        | 88 | Help me build    |
| 81 | Cover me       | 89 | Give me a boost  |
| 82 | Follow me      | 90 | Open the wall    |
| 83 | Wait for me    | 91 | Close the wall   |
| 84 | Come here      | 92 | Let me through   |
| 85 | I need blocks  | 93 | Guard this spot  |
| 86 | I need ammo    | 94 | Heal me          |
| 87 | I need health  | 95 | Dig me out       |

#### 96-111 — Orders and tactics

| Id  | English text          | Id  | English text     |
|-----|-----------------------|-----|------------------|
| 96  | Attack                | 104 | On my command    |
| 97  | Defend                | 105 | Prepare for assault |
| 98  | Fall back             | 106 | Flank left       |
| 99  | Regroup               | 107 | Flank right      |
| 100 | Push up               | 108 | Go around        |
| 101 | Hold position         | 109 | Rush them        |
| 102 | Spread out            | 110 | Take cover       |
| 103 | All together          | 111 | Kick their butt  |

#### 112-127 — Objective

| Id  | English text         | Id  | English text        |
|-----|----------------------|-----|---------------------|
| 112 | Get the intel        | 119 | Capture this point  |
| 113 | I have the intel     | 120 | Defend this point   |
| 114 | They have our intel  | 121 | Enemy base          |
| 115 | Defend our intel     | 122 | Our base            |
| 116 | Bring it home        | 123 | Meet at our base    |
| 117 | I am escorting you   | 124 | Go restock          |
| 118 | Cover the carrier    | 125 | Restock first       |
|     |                      | 126 | Our base is under assault |

#### 128-143 — Building and digging

| Id  | English text        | Id  | English text     |
|-----|---------------------|-----|------------------|
| 128 | Build here          | 136 | Do not dig here  |
| 129 | Dig here            | 137 | Tear it down!    |
| 130 | Build a bridge here | 138 | Nice build       |
| 131 | Dig a tunnel here   | 139 | Watch the fall   |
| 132 | Build a wall here   | 140 | I am building    |
| 133 | Build a tower here  | 141 | Block the way    |
| 134 | Make stairs here    |     |                  |
| 135 | Fill this hole      |     |                  |

#### 144-159 — Own status

| Id  | English text       | Id  | English text        |
|-----|--------------------|-----|---------------------|
| 144 | On my way          | 152 | I am dead           |
| 145 | In position        | 153 | Respawning          |
| 146 | I follow you       | 154 | I am sniping here   |
| 147 | I am low           | 155 | I am flanking       |
| 148 | I am out of blocks | 156 | I am digging in     |
| 149 | I am out of ammo   | 157 | Going back to base  |
| 150 | Reloading          | 158 | I am lost           |
| 151 | I am hit           |     |                     |

#### 160-175 — Warnings

| Id  | English text     | Id  | English text     |
|-----|------------------|-----|------------------|
| 160 | Grenade!         | 167 | Cave in!         |
| 161 | Watch out!       | 168 | Do not shoot     |
| 162 | Look up          | 169 | Hold your fire   |
| 163 | Look down        | 170 | Friendly fire!   |
| 164 | Careful          | 171 | Stop             |
| 165 | Do not go there  | 172 | Stop griefing    |
| 166 | Falling blocks!  | 173 | Do not fall      |

#### 176-191 — Reactions

| Id  | English text | Id  | English text |
|-----|--------------|-----|--------------|
| 176 | Lol          | 183 | Good try     |
| 177 | Nice         | 184 | Revenge!     |
| 178 | Wow          | 185 | Camper       |
| 179 | Oops         | 186 | Too easy     |
| 180 | Close one    | 187 | Rip          |
| 181 | Let's go     | 188 | Loser        |
| 182 | We got this  |     |              |

This block is the one a server is most likely to filter, and filtering it is
expected: a server that considers `Too easy` or `Camper` an invitation to
needling drops those ids and relays the rest. That decision belongs to the
server, which is why the catalogue carries them rather than pretending players
will not find a way to say them.

#### 192-207 — Places

Landmarks every Ace of Spades map has, whatever it looks like. These pair
naturally with a Ping, which supplies the *where* while the id supplies the
*what*.

| Id  | English text     | Id  | English text     |
|-----|------------------|-----|------------------|
| 192 | At the tent      | 200 | On the hill      |
| 193 | At the intel     | 201 | In the trench    |
| 194 | On the bridge    | 202 | In their base    |
| 195 | Under the bridge | 203 | In our base      |
| 196 | In the tunnel    | 204 | At the wall      |
| 197 | In the water     | 205 | In the open      |
| 198 | On the roof      | 206 | In the river     |
| 199 | Behind the wall  |     |                  |

#### 208-223 — Singling out a player

Entries about one player in particular: the quarry of a manhunt, a hostage, the
intel carrier, a suspected cheater, a griefer, an idler.

| Id  | English text             | Parameters |
|-----|--------------------------|------------|
| 208 | Target                   |            |
| 209 | Hunt %1$p                | `%p`       |
| 210 | Kill %1$p                | `%p`       |
| 211 | %1$p is enemy number one | `%p`       |
| 212 | The hunt is over         |            |
| 213 | Cheater                  |            |
| 214 | %1$p is a cheater        | `%p`       |
| 215 | Griefer                  |            |
| 216 | %1$p is afk              | `%p`       |
| 217 | Cleared                  |            |
| 218 | I killed %1$p            | `%p`       |
| 219 | %1$p is under assault    | `%p`       |
| 220 | Enemy                    |            |
| 221 | Hostage                  |            |
| 222 | Leader                   |            |
| 223 | Carrier                  |            |

The single-word entries name nobody: they are labels for a
[Ping](#sub-id-1-ping) or an [ESP Mark](#sub-id-2-esp-mark), whose Player ID
already says who is meant. `Enemy`, `Hostage`, `Leader` and `Carrier` are roles a
server assigns; `Target`, `Cheater`, `Griefer` and `Cleared` are what it or a
team says about the player holding one.

The accusing entries are the block a server is most likely to filter after
[Reactions](#reactions). A server may drop `%1$p is a cheater` and `Griefer`
outright, relay them to admins alone, or let them through; the protocol takes no
position.

#### 224-239 — Server notices

The server talking to a player about their connection, and announcing what only
the server knows. Everything here is sent with Player ID `255`, normally as
`CHAT_SYSTEM` or as one of the [Message Types](#message-types) warning forms; a
client never sends these, and a server drops them if one does.

| Id  | English text                                  | Parameters |
|-----|-----------------------------------------------|------------|
| 224 | Your client is outdated, please upgrade       |            |
| 225 | Your client is missing features required here |            |
| 226 | You are at a disadvantage                     |            |
| 227 | You seem afk                                  |            |
| 228 | Final warning                                 |            |
| 229 | You will be kicked in %1$i seconds            | `%i`       |
| 230 | The bridge has collapsed                      |            |
| 231 | The tower has collapsed                       |            |
| 232 | Welcome to the server, %1$p                   | `%p`       |
| 233 | Intel captured                                |            |
| 234 | Intel lost                                    |            |
| 235 | Our intel has disappeared                     |            |
| 236 | Base captured                                 |            |
| 237 | Base lost                                     |            |
| 238-239 | reserved                                  |            |

`224` and `225` follow from what [`ExtInfo`](#extinfo-packet) told the server;
`226` is for a client that connects but lacks something the server's game leans
on. `228` and `229` are the warning before a kick, where
[Kick Reason](#kick-reason) carries the reason itself.

`233`-`237` are read from the receiving team's side: captured is the recipient's
team taking it, lost is the recipient's team losing it, and the server sends each
side the one that applies.

#### 240-255 — Reserved

Free for later versions of this extension. A version 1 client or server must not
send them and ignores them on receipt.

#### Notes for implementers

The **id** is the translation key. A client translates by id, never by matching
the English text it received, and never localises anything a peer might parse
back. English is one language in the table like any other, and a client whose
user reads English looks the id up exactly as every other client does.

A translation of a parametric entry must carry every marker its canonical English
carries, exactly once each, and may put them in any order using their positional
form.

Canonical English is written in sentence case: the first word is capitalised and
the rest are not. A translation follows its own language's rules instead, and a
client is free to case an entry as its interface wants.

### Per-player state

Everything this extension creates belongs to a player id, and all of it is freed
the moment that player leaves. When a client receives
[Player Left](protocol075.html#player-left) for an id it drops, for that id: the
player's active ping, the ESP mark on them if any, and any predefined message
still displayed that named them as sender, as target, or as the value of a
[`%p`](#message-parameters). The server drops the same things on its side and
stops referring to the id.

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