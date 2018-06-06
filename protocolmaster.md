## Connection

The protocol is using [ENet](http://enet.bespin.org/) for transfer.
When you connect, you must send a version number as the initial data.

| Number |
| :----: |
| 31     |

Send your request to `master.buildandshoot.com` on port `32886`.

## Packets

There is only two kinds of packets, no packet id precedes the actual data.

## Table of Contents
* [Major update](#major-update)
* [Count update](#count-update)

## Data types

Generally, all fields in the Protocol are Low Endian if not specified.

The following shorthands are used in this document:

| Shorthand    | details                                                 |
| -----------: | ------------------------------------------------------- |
| UByte        | Unsigned 8 bit number                                   |
| UShort       | Unsigned 16 bit number                                  |
| CP437 String | String encoded with CP437. `\0` terminated.             |

## Major update
*Client -> Server*

Send on server startup or after the map was changed.
Master server assumes player count is reset back to zero.

| Field Name  | Field Type                                                 | Example        | Notes           |
| ----------: | ---------------------------------------------------------- | -------------- | --------------- |
| max players | UByte                                                      | `32`           |                 |
| port        | UShort                                                     | `32887`        |                 |
| name        | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `Deuce's Wild` | *max. 31 bytes* |
| game mode   | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `ctf`          | *max. 7 bytes*  |
| map         | [CP437](http://en.wikipedia.org/wiki/Code_page_437) String | `normandie`    | *max. 20 bytes* |

## Count update
*Client -> Server*

Used to update the master when a player joined or left the server.

| Field Name   | Field Type                                                 | Example        | Notes |
| -----------: | ---------------------------------------------------------- | -------------- | ----- |
| player count | UByte                                                      | `24`           |       |
