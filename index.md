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

| ID | String ID     | Description                                          | Link | Implementers |
|----|---------------|------------------------------------------------------|------|--------------|
| 0  | `unicode`     | Strings can contain unicode if prefixed with `0xFF`  | todo | os           |
| 1  | `powerthirst` | Large modification sadly used only for a single game | todo |              |
| 2  | `version_get` | Allows servers to request version information        | todo | os, pq       |

### Implementers legend
 * `os`: [OpenSpades](https://github.com/yvt/openspades)
 * `pq`: [piqueserver](https://github.com/piqueserver/piqueserver)
 * `bs`: [BetterSpades](https://github.com/xtreme8000/BetterSpades)

## Other Protocols

 * [Master Server Protocol](protocolmaster.html)
 * [Ping Protocol](protocolping.html)

# Other Resources
* [KVX File Format Specification](https://web.archive.org/web/20100102023608/http://mystaddict.tlayeh.com/Computer%20Camp/Slab6/slab6.txt) - An archive of the mirror of the readme for Slab6 which contains the .kvx file format, the format that the AoS model format is based on
* [VXL File Format Specification](http://silverspaceship.com/aosmap/aos_file_format.html) - A description of the .vxl file format, the format used for AoS maps ([mirror](aos_file_format.html))
