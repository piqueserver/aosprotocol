## Connection

This protocol is used to measure the connection delay (latency/ping) between your local computer and a server.

You will need to measure the actual time difference yourself:

```
ping = dt/2
```

Open up a raw UDP connection to the server's port, and send a packet.

## Packets

There is only two kinds of packets, no packet id precedes the actual data.

## Table of Contents
* [Ping start](#ping-start)
* [Ping acknowledge](#ping-acknowledge)

## Ping start
*Client->Server*

After server recieved this packet, a ping acknowledge is sent back immediately.

| Length  | Value   | Field Type   | Notes                                  |
| ------- | ------- | ------------ | -------------------------------------- |
| 5 bytes | `HELLO` | CP437 String | fixed length, never send anything more |

## Ping acknowledge
*Server->Client*

| Length  | Value | Field Type   | Notes        |
| ------- | ----- | ------------ | ------------ |
| 2 bytes | `HI`  | CP437 String | fixed length |
