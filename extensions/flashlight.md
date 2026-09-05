# Flashlight

A light a player carries and everybody sees. The point of the extension is the
second half: a flashlight only one client draws is a lamp in a mirror, useful to
nobody and invisible to the player it gives away. Here the state is the server's,
every client is told about every light, and a beam coming round a corner means
the same thing to the player holding it and to the player watching it arrive.

| ------------: | ------------- |
| Extension ID: | 3             |
| Packet ID:    | 67            |
| Version:      | 1             |
| Type:         | `HAS_PACKETS` |

The extension id, the number carried by `ExtInfo`, is `3`; the packet id is
`64 + extension id` as described in [Extension IDs](extension.html#extension-ids).

### Sub Packets:

| Sub ID | Name        | Direction         | Size |
|--------|-------------|-------------------|------|
| 0      | Config      | Server -> Client  | 3    |
| 1      | Light       | Client <-> Server | 4    |
| 2      | Light State | Server -> Client  | 2+   |

A client sends one of these and no other: a **Light** to ask for its own light on
or off. Config and Light State are the server speaking, and a server that
receives either from a client drops it. What a client sends is a request; the
server decides whether the light comes on and tells everybody it chose to tell.

## Sub ID 0: Config

The server says whether clients may work their own lights. The flag is a policy
switch, not a data gate: it decides who may ask, never who may see. A client with
it clear still renders every light the server tells it about, and lights the
server switches on itself are unaffected.

| Field Name    | Field Type | Example | Notes                                 |
|---------------|------------|---------|---------------------------------------|
| Packet ID     | UByte      | `67`    | Always `67`.                          |
| Sub Packet ID | UByte      | `0`     | Always `0` for this sub-packet.       |
| Flags         | UByte      | `0b1`   | See below.                            |

| Bit | Name         | Meaning                                                     |
|-----|--------------|-------------------------------------------------------------|
| 0   | `FLASHLIGHT` | Client may ask for its own light, with a Light packet.       |
| 1-7 | reserved     | Must be `0`. Clients must ignore unknown bits.               |

Nothing here describes the beam. Its reach, its width and its colour are fixed by
this specification, see [What the beam is](#what-the-beam-is), and no packet
carries them: every light on every server is the same light, and the only thing
anybody negotiates is who may switch one on.

**Until this packet arrives the client asks for nothing.** With no bitmask yet
received the feature is off, exactly as if the server had sent one with
`FLASHLIGHT` clear.

The server MAY send this at any time and the client applies it immediately — on a
map rotation, or when night falls in a game mode that has one. When `FLASHLIGHT`
clears, a client that had its light on stops asking for it and the server sends
the Light packets that turn the lights off; a client does not extinguish itself
on the flag alone, because the state on everybody else's screen is the server's
to change.

A Light already in flight when the config changes is simply dropped by the
server. This is not a protocol violation and needs no special handling.

## Sub ID 1: Light

Turns one player's light on or off. A client sends it to ask for its own; the
server relays the outcome to the clients of its choice. The server may also
originate one with no client involved — a game mode that kills the lights, an
admin dousing somebody, a scripted blackout.

| Field Name    | Field Type | Example | Notes                                              |
|---------------|------------|---------|-----------------------------------------------------|
| Packet ID     | UByte      | `67`    | Always `67`.                                        |
| Sub Packet ID | UByte      | `1`     | Always `1` for this sub-packet.                     |
| Player ID     | UByte      | `0`     | On relay, the player whose light this is. Ignored on the client -> server direction; the server fills it in authoritatively. |
| State         | UByte      | `1`     | `0` off, `1` on. See below.                         |

**State** is a byte and not a bit so that a later version can shape a light
without a new packet: version 1 defines `0` off and `1` on, `2`..`255` are
reserved for [a focused beam](#room-for-a-focused-beam), and a receiver treats
any value it does not know as on. A version 2 that spends them therefore degrades
into version 1 exactly — a lit player stays lit, drawn with the standard beam,
rather than going dark or dropping the packet.

A client's Light is a request, like every other thing a client asks for. The
server may refuse it, delay it, or answer with the opposite; it decides who is
told, and telling nobody is a decision too. A client whose request is refused
learns so by never receiving the relay.

A dead player carries no light. The client turns its own off when it dies and
does not ask again until it spawns, and the server drops a Light from a dead
player the way it drops one sent with `FLASHLIGHT` clear.

Server handling of a client -> server Light:

* Whatever a client puts in Player ID is ignored: the server fills it in from the
  connection the packet arrived on.

## Sub ID 2: Light State

Every light at once, for a client that has just arrived and knows none of them.
The server sends it after [State Data](../protocol075.html#state-data), alongside
the [Existing Player](../protocol075.html#existing-player) packets that introduce
the players it describes.

| Field Name    | Field Type | Example  | Notes                                            |
|---------------|------------|----------|---------------------------------------------------|
| Packet ID     | UByte      | `67`     | Always `67`.                                      |
| Sub Packet ID | UByte      | `2`      | Always `2` for this sub-packet.                   |
| States        | UByte[]    | `0b1010` | Bitmask, one bit per player id, the remaining bytes of the packet. |

Bit `n` of byte `n / 8` is the light of player id `n`, so byte 0 carries ids
`0`..`7` with id `0` in the low bit. The array is the remaining bytes of the
packet and its length is implied by the packet length: four bytes cover a vanilla
server's 32 ids, thirty-two cover all 256 under
[Player Limit](player-limit.html), and an id past the end of the array is off. A
server with every light off may send the packet empty, or not send it at all.

A bitmask rather than a list of ids because the answer is one bit wide and the
question is asked once per join: four bytes for a whole server beats a length
byte and a pair per lit player, and it costs nothing to write on either side.

Lights are per-player state, and it is the joining client that needs catching up,
not the players already there — a light that has been on for a minute is still
worth one bit. This is the only packet that carries more than one player's light,
and a server may also use it to resynchronise everybody after a blackout it
imposed itself, rather than sending a Light packet per player.

## Where the light points

Nowhere in this extension. A light is attached to the player who carries it and
aimed by the view direction the base protocol already sends, in
[Orientation Data](../protocol075.html#orientation-data) and every
[World Update](../protocol075.html#world-update-075). The client has the position
and the orientation of every player at all times, so a beam needs one bit of new
information — whether it is lit — and not one byte of geometry.

That is what keeps the extension small, and it is also what keeps it honest: a
light that pointed somewhere of its own would drift from the player's aim on
every packet loss, and the two would have to be reconciled. Here they cannot
disagree, because there is only one of them.

The beam therefore turns as fast as the orientation updates arrive, which is as
fast as everything else the client draws about that player, and it lags that
facing slightly on the way, see [What the beam is](#what-the-beam-is).

## What the beam is

One light, hardcoded, the same on every client and every server. These are the
values *OpenSpades* and *ZeroSpades* already light the local player with, and the
extension keeps them exactly rather than inventing a light of its own: the
behaviour players know is the behaviour they keep, and the only thing that
changes is who can see it.

| Property   | Value                            | Notes                                          |
|------------|----------------------------------|------------------------------------------------|
| Type       | Spotlight                        | A cone from the player's eye, along their view. |
| Reach      | `60` blocks                      | The radius at which the light has fallen off entirely. |
| Cone       | `90` degrees                     | Measured across the cone, not from its axis.   |
| Colour     | `(1.0, 0.7, 0.5)` linear RGB     | A warm white. Multiplied by the brightness below, and by whatever exposure the renderer works in. |
| Spill      | Point light, `10` blocks, `0.3x` | A second, dimmer light at the same origin, so the player is lit as well as the wall they face. |
| Warm-up    | `1 - e^(-5t)`                    | `t` in seconds since the light came on, so it reaches full in about a second rather than snapping. |

The beam follows the holder's view with a short lag rather than being welded to
it: the client interpolates towards the current facing each frame and clamps the
gap so the light never trails more than slightly behind a fast turn. It is a
torch held in a hand, not a laser bolted to the skull, and the smoothing is what
makes it read as one.

Fixed values because a light is a thing you see other people by. A server that
could set the reach could hand its regulars a longer one; a client that could
set the colour could pick the one that shows up worst on other people's screens
and best on its own. Neither is possible if there is nothing to set. It also
means the extension costs one bit per player and no configuration at all: a
server switches lights on and off, and does not describe them.

Changing any of this changes the version. There is no field to grow, so a version
2 that wants a dimmer torch, a coloured one, or one that differs per player says
so in the version byte and the whole server moves together.

### Room for a focused beam

Version 1 has one beam, and this section is only about the room left for a
version that has more than one. A focused light — narrow the cone and it throws
further, widen it and it floods the ground at your feet — is the obvious thing to
want next, and `2`..`255` of the [State](#sub-id-1-light) byte are held for it.
Nothing below is implemented, and a version 1 client that meets one of these
values draws the standard beam.

**One axis, not two.** Reach and cone are not independent settings a later
version would send separately: they are the two readings of a single focus
position, because a torch that concentrates its light throws it further by the
same act that narrows it. So the byte is a position on that axis, `1` is its
widest point and the beam version 1 already draws, and higher values narrow and
lengthen it together. A version that sent an angle and a range as two numbers
could describe a light that is both wide and long, which is a floodlight nobody
switched on.

**The curve belongs to the specification, not to the server.** Whatever relates
position to reach and cone must be written down and identical everywhere, for the
reason the version 1 numbers are: a server that could steepen the curve could
hand somebody a better torch. The natural shape holds the light's output constant
so that narrowing concentrates rather than creates — keeping the illumination at
the far edge roughly constant makes reach grow as the cone's solid angle
shrinks — but picking it is that version's work, not this one's.

**Mixed versions see different beams, and that is the cost.** A focused player is
drawn narrow and far by clients that speak version 2 and as the standard cone by
clients that do not, so for the length of a mixed server the light stops being
the same light for everybody — the one thing version 1 guarantees. A server can
buy the guarantee back by offering focus only when every client has negotiated
version 2, and by holding everybody at `1` until then.

**Focus is adjusted, not toggled.** A player working a focus ring generates a run
of values where version 1 generates one, so a later version needs a rate limit of
its own where version 1 needs none — sending where the ring settled rather than
every position it passed through, or a limit measured in updates per second
rather than toggles.

[Light State](#sub-id-2-light-state) carries one bit per player and cannot say
where a light is focused. A version that needs more than lit-or-not for a joining
client adds a sub-packet for it rather than widening that bitmask, which is why
the sub-packet ids are cheap and the bitmask stays a bitmask.

## What a client renders

A client that receives a light for a player with the state on **must show it**,
whichever team that player is on. Hiding the beam of an enemy who is lit on
everybody else's screen would hand the player hiding it the advantage of seeing
somebody who cannot be seen back, which is the one thing a shared light must
never allow.

The values above are the light; they are not a hint to be improved on, scaled to
taste, or exposed as a setting in the client's options. A beam that reaches
further than 60 blocks shows its holder things nobody else can see, and one that
reaches less hides a player who believes they are lit — both are the local lamp
again, wearing the extension's name.

The technique is the client's business, because clients differ enormously in what
they can draw. A renderer with dynamic lights adds the spotlight and the point
light and is done. One without can draw the cone itself, a glow at the player's
hands, a bright patch where the beam lands, or all three. Where a renderer cannot
reproduce the light exactly it approximates it, and it approximates towards these
numbers rather than towards what is convenient to draw.

The light does not reveal what the client would otherwise not know: a player lit
behind a wall is a player behind a wall, drawn no differently from an unlit one.
Nothing here is an ESP switch — it changes how a player looks, never whether they
are drawn at all.

## Per-player state

A light belongs to a player id and is freed with it. A client turns the light off
for an id, without waiting for a Light packet, when it receives:

* [Player Left](../protocol075.html#player-left) for that id. Ids are recycled, and
  a light outliving its owner lands on whoever takes the id next.
* [Create Player](../protocol075.html#create-player) for that id. A player spawns
  with their light off, whether they were killed, changed team, changed weapon or
  were moved by a script.
* [Kill Action](../protocol075.html#kill-action) for that id, since a corpse holds
  nothing.
* [Map Start](../protocol075.html#map-start-075), which clears every light on the
  server.

The server applies the same rules on its side and sends nothing for any of them.
Both ends already have the packet that causes them, so spending a Light packet on
a death that every client has just been told about is bandwidth for nothing.

See [Extensions](extension.html) for how the extension is negotiated.
