# Ace of Spades Map File Format version 1

#### Revision History

* 2011-05-14 First release (Sean Barrett)

## Introduction

This document describes the format of the Ace of Spades version 1 map file.

#### Issues
The map file appears to be a binary dump of the memory format of the voxel storage of the voxlap engine.

It is unclear what happens if you don't obey the "surface" voxel rule, i.e. supply colors for voxels which are hidden. They may work correctly, or they might break the voxlap engine since it loads the data unaltered. I haven't checked.

Similarly, I don't know what would happen if you stored data out of order or tried to encode 0-length top color runs.

#### Map structure and motivation

The AoS map consists of a 2D array of "columns" of voxels. The 2D array is `width * height` in size; in the current file format width and height are both `512`.

Each voxel column is stored independently of every other column.

AoS distinguishes between three kinds of voxels: open voxels (which represent air), solid voxels (which represent solid space, but which aren't visible), and colored voxels (which represent solid blocks which are visible, and so must be drawn as some particular color). Colored voxels are also called "surface voxels", because to be visible they must be exposed to air on at least one side, that is, they represent the "surface" of the object.
## File format

#### Spawning
In this version of the file format, spawn locations are implicit.

* Blue spawns in the region from `(0,128)` to `(256,384)`
* Green spawns in the region from `(384,128)` to `(512,384)`

#### Gross file structure
The file is described here as a binary file of bytes (so there are no endianness issues).

The file contains no header. The only way to detect that a file is an AoS map of type version 1 is to check the first 4 bytes and see if they are a legitimate span descriptor (see below).

The file stores the column data for each of the 2D map squares. These are stored left-to-right, top-to-bottom; the first column stored is `(0,0)`, the 511th column stored is `(511,0)`, and the 512th column stored is `(0,1)`.

#### Column data
Each column consists of a variable number of "spans", where each span contains several runs of voxel data. The spans are encoded using explicit positions rather than lengths; we will refer to these positions as "heights". Heights are measured starting from z=0, which is the highest position in the sky, to z=63, which is the lowest position (and must always be solid--it behaves as water). Blocks at z=62 which are solid are indestructible; they represent the lowest level of non-water ground.

A span consists of the following runs of voxels in order:

* 0 or more open voxels
* 1 or more colored voxels (this document refers to these as the "top" colored run)
* 0 or more solid voxels
* 0 or more colored voxels (this document refers to these as the "bottom" colored run)

A single column consists of repetitions of this span format. The last span in each column is special, and ends with solid voxels extending down to z=63.

(Note the straightforward rationale for this encoding: between any open voxel and invisible solid voxel, there must be a colored voxel. In a normal map, the ground is solid and the sky is air, so when encoding from the sky down, it makes sense to start with a run of air and end with a run of solid.)

Spans are stored sorted from top to bottom *(from z=0 to z=63)*.

Each span is stored as the following sequence of bytes:

| byte offset | name | meaning                                                                      |
| ----------: | :--: | ---------------------------------------------------------------------------- |
| `0`           | N    | length of span data (`N*4` bytes including span header)                        |
| `1`           | S    | starting height of top colored run                                           |
| `2`           | E    | ending height of top colored run (length is `E-S+1`)                           |
| `3`           | A    | starting height of air run (first span ignores value and assumes A=0)        |
| `4 + i*4`     | b    | blue color for colored voxel #i                                              |
| `5 + i*4`     | g    | green color for colored voxel #i                                             |
| `6 + i*4`     | r    | red color for colored voxel #i                                               |
| `7 + i*4`     | a    | alpha channel for colored voxel #i, actually used for shading in unknown way |

Colors of both the top run and bottom run are stored in the array. i goes from 0 to N-1, first encoding the top colors, and then encoding the bottom colors. The voxel heights for the bottom colors are implied by the starting height of the air run of the next span; they appear just above the air.

The next byte after the above list `(at 8+N*4)` is the first byte of the next span of the column. Thus the location of the air run of the next span is at `(8+N*4+3)`.

As a special case, an N value of 0 means this is the last span of the column. The last span contains air, a top-colored span, and all voxels below down to 63 are solid. The actual storage used by the span is determined by the number of top colors; in other words, it is `4*(1 + (E-S+1))`. Thus, that is the offset to the first span of the next column.

We now summarize the interpretation of the lengths and positions of the runs.

```
Let K = E - S + 1
Let Z = (N-1) - K, or 0 if N=0
Let M = A stored in *next* span, or 64 if the last span of the column
```

| Run    | Start | End   | Length      |
| ------ | ----- | ----- | ----------- |
| air    | A     | S-1   | S-A         |
| top    | S     | E     | E-S+1       |
| solid  | E+1   | M-Z-1 | M-Z - (E+1) |
| bottom | M-Z   | M-1   | Z           |

## Sample C/C++ code
The following code examples use two arrays; `map[x][y][z]` stores whether a voxel is open or solid (counting colored voxels as solid), and the array `color[x][y][z]` stores the color of the voxel if it is a surface voxel.

Note the map is stored as `map[x][y][z]`, which is reversed from the traditional C way of storing things.

#### Reading a map

```C
/*
 * this code is adapted from the sample code in vxlform.txt
 */

void setgeom(int x, int y, int z, int t)
{
   assert(z >= 0 && z < 64);
   map[x][y][z] = t;
}

// need to convert for endianness here if we read 32-bits at a time
void setcolor(int x, int y, int z, uint32 c)
{
   assert(z >= 0 && z < 64);
   color[x][y][z] = c;
}

void load_map(uint8 *v, int len)
{
   uint8 *base = v;
   int x,y,z;
   for (y=0; y < 512; ++y) {
      for (x=0; x < 512; ++x) {
         for (z=0; z < 64; ++z) {
            setgeom(x,y,z,1);
         }
         z = 0;
         for(;;) {
            uint32 *color;
            int i;
            int number_4byte_chunks = v[0];
            int top_color_start = v[1];
            int top_color_end   = v[2]; // inclusive
            int bottom_color_start;
            int bottom_color_end; // exclusive
            int len_top;
            int len_bottom;

            for(i=z; i < top_color_start; i++)
               setgeom(x,y,i,0);

            color = (uint32 *) (v+4);
            for(z=top_color_start; z <= top_color_end; z++)
               setcolor(x,y,z,*color++);

            len_bottom = top_color_end - top_color_start + 1;

            // check for end of data marker
            if (number_4byte_chunks == 0) {
               // infer ACTUAL number of 4-byte chunks from the length of the color data
               v += 4 * (len_bottom + 1);
               break;
            }

            // infer the number of bottom colors in next span from chunk length
            len_top = (number_4byte_chunks-1) - len_bottom;

            // now skip the v pointer past the data to the beginning of the next span
            v += v[0]*4;

            bottom_color_end   = v[3]; // aka air start
            bottom_color_start = bottom_color_end - len_top;

            for(z=bottom_color_start; z < bottom_color_end; ++z) {
               setcolor(x,y,z,*color++);
            }
         }
      }
   }
   assert(v-base == len);
}
```

#### Writing a map
The following code outputs a map according to the surface voxel rule; it does not write out colors for voxels which are not surface voxels.

Note the map is stored as `map[x][y][z]`, which is reversed from the traditional C way of storing things.

```C
int is_surface(int x, int y, int z)
{
   if (map[x][y][z]==0) return 0;
   if (x   >   0 && map[x-1][y][z]==0) return 1;
   if (x+1 < 512 && map[x+1][y][z]==0) return 1;
   if (y   >   0 && map[x][y-1][z]==0) return 1;
   if (y+1 < 512 && map[x][y+1][z]==0) return 1;
   if (z   >   0 && map[x][y][z-1]==0) return 1;
   if (z+1 <  64 && map[x][y][z+1]==0) return 1;
   return 0;
}

void write_color(FILE *f, uint32 color)
{
   // assume color is ARGB native, but endianness is unknown

   // file format endianness is ARGB little endian, i.e. B,G,R,A
   fputc((uint8) (color >>  0), f);
   fputc((uint8) (color >>  8), f);
   fputc((uint8) (color >> 16), f);
   fputc((uint8) (color >> 24), f);
}

#define MAP_Z  64
void write_map(char *filename)
{
   int i,j,k;
   FILE *f = fopen(filename, "wb");

   for (j=0; j < 512; ++j) {
      for (i=0; i < 512; ++i) {
         int written_colors = 0;
         int backpatch_address = -1;
         int previous_bottom_colors = 0;
         int current_bottom_colors = 0;
         int middle_start = 0;

         k = 0;
         while (k < MAP_Z) {
            int z;

            int air_start;
            int top_colors_start;
            int top_colors_end; // exclusive
            int bottom_colors_start;
            int bottom_colors_end; // exclusive
            int top_colors_len;
            int bottom_colors_len;
            int colors;

            // find the air region
            air_start = k;
            while (k < MAP_Z && !map[i][j][k])
               ++k;

            // find the top region
            top_colors_start = k;
            while (k < MAP_Z && is_surface(i,j,k))
               ++k;
            top_colors_end = k;

            // now skip past the solid voxels
            while (k < MAP_Z && map[i][j][k] && !is_surface(i,j,k))
               ++k;

            // at the end of the solid voxels, we have colored voxels.
            // in the "normal" case they're bottom colors; but it's
            // possible to have air-color-solid-color-solid-color-air,
            // which we encode as air-color-solid-0, 0-color-solid-air

            // so figure out if we have any bottom colors at this point
            bottom_colors_start = k;

            z = k;
            while (z < MAP_Z && is_surface(i,j,z))
               ++z;

            if (z == MAP_Z || 0)
               ; // in this case, the bottom colors of this span are empty, because we'l emit as top colors
            else {
               // otherwise, these are real bottom colors so we can write them
               while (is_surface(i,j,k))  
                  ++k;
            }
            bottom_colors_end = k;

            // now we're ready to write a span
            top_colors_len    = top_colors_end    - top_colors_start;
            bottom_colors_len = bottom_colors_end - bottom_colors_start;

            colors = top_colors_len + bottom_colors_len;

            if (k == MAP_Z)
               fputc(0,f); // last span
            else
               fputc(colors+1, f);
            fputc(top_colors_start, f);
            fputc(top_colors_end-1, f);
            fputc(air_start, f);

            for (z=0; z < top_colors_len; ++z)
               write_color(f, color[i][j][top_colors_start + z]);
            for (z=0; z < bottom_colors_len; ++z)
               write_color(f, color[i][j][bottom_colors_start + z]);
         }  
      }
   }
   fclose(f);
}
```

## Credits
* [Ace of Spades](http://ace-spades.com) is by Ben Aksoy.

* The Ace of Spades file format is an adaptation of the Voxlap VXL file format, by [Ken Silverman](http://advsys.net/ken).

* The C code for reading a map provided above is a refactoring of the code from VXLFORM.TXT by Ken Silverman, refactored by Sean Barrett.

* The C code for writing a map provided above and the textual description of the file format are by [Sean Barrett](http://silverspaceship.com).

*This document is in the public domain. Please be polite when you change it.*
