This page documents the networking Protocol of Ace of Spades 0.75, as well as
the extensions made by the community.

# Overview
[Ace of Spades](http://buildandshoot.com/) uses the [ENet networking
library](http://enet.bespin.org/Features.html) for all server-client
communication. The initial source for the protocol information was the original
[pyspades](http://code.google.com/p/pyspades/) source code, for which the
source for 1.0 was not released. Nonetheless, the 1.0 alpha client has been
reverse engineered to document the protocol.

## Versions

 * [0.75 (and 0.76) documentation](protocol075.html)
 * [1.0 alpha documentation](protocol100a1.html)

## Extensions

The 0.75 protocol supports extensions, which allow adding new packets as well as
querying the support for client and server functionality.

### Extensions providing packets

Packetful extensions are extensions that can be used to send packets. Each
extension has 256 packet types reserved for itself. This is useful for adding
functionality that requires sending additional information from or to the client.

| ID | Name          | Description                                          | Link | Implementers |
|----|---------------|------------------------------------------------------|------|--------------|


### Packetless Extensions

Packetless extensions are extensions that can not send any packets. This is useful
for signalling support for additional values in or certain behaviours related to
existing packets.

Packetless extensions exist as an artefact of the implementation of extensions.
As the space reserved for extension packets is limited, values above 192 do not
have any packet types left.

| ID  | Name          | Description                                           | Link |
|-----|---------------|-------------------------------------------------------|------|
| 192 | Player Limit  | Support for up to 256 players                         | TODO |
| 193 | Message Types | Additional message types such as warnings and satuses | TODO [#14](https://github.com/piqueserver/aosprotocol/issues/14) |
| 194 | Kick Reason   | Repurposes the chat to send a disconnect reason text  | TODO |

### Implementers
 * [OpenSpades](https://github.com/yvt/openspades)
 * [piqueserver](https://github.com/piqueserver/piqueserver)
 * [BetterSpades](https://github.com/xtreme8000/BetterSpades)

Links to the respective projects pages that detail the extensions evailable in
each version should be linked here.

## Other Protocols

 * [Master Server Protocol](protocolmaster.html)
 * [Ping Protocol](protocolping.html)

# Other Resources
* [KVX File Format Specification](https://web.archive.org/web/20100102023608/http://mystaddict.tlayeh.com/Computer%20Camp/Slab6/slab6.txt) - An archive of the mirror of the readme for Slab6 which contains the .kvx file format, the format that the AoS model format is based on
* [VXL File Format Specification](mapformat.html) - A description of the .vxl file format, the format used for AoS maps<br />([original](http://silverspaceship.com/aosmap/aos_file_format.html), [mirror](aos_file_format.html))
