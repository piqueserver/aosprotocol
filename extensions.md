## Extension Negotiation Packet

### Overview

Each extension is given an unique id that is decided when it is first
registered. We differentiate between two types of packets:

*Those that:*

| Type          | Purpose                               | Extension id range |
| ------------- | ------------------------------------- | --------------- |
| `HAS_PACKETS` | introduce new packets to the protocol | 0-191           |
| `PACKETLESS`  | don't use and need any packets        | 192-255         |

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
* Total size: `2+2*n`

| Field name | Field type   | Notes                          |
| ---------- | ------------ | ------------------------------ |
| length     | UByte        | `length+1` entries will follow |
| entries    | ExtInfoEntry | see below                      |

**ExtInfoEntry**

| Field name | Field type | Notes         |
| ---------- | ---------- | ------------- |
| ext. ID    | UByte      | see #Overview |
| version    | UByte      | starting at 0 |

## Protocol Flow

The server MUST send an `ExtInfo` packet on connect. The client can store
the list of extensions and MUST reply with an `ExtInfo` packet that lists
the extensions it supports.

It SHOULD omit any extensions that the server does not support from it's
reply.
