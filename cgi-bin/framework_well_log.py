#!/usr/bin/env python
###############################################################################
# $Id$
#
# Project:  GDAL Python framework_well_log
# Purpose:  This script produces geologic information of subsurface layers for
#           a single location point. The subsurface layers are represented by
#           one or more rasters that represent the land surface elevation 
#           and the underlying the geologic units or other subsurface features.
#
# Author:   Leonard Orzol <llorzol@usgs.gov>
#
###############################################################################
# Copyright (c) Leonard Orzol <llorzol@usgs.gov>
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

try:
    from osgeo import osr
    from osgeo import gdal
    from osgeo.gdalconst import *
except ImportError:
    import gdal
    from gdalconst import *

import os
import sys
import random

import argparse

import frameworkUtils

program      = "USGS Well Log Script"
version      = "2.01"
version_date = "31May2023"
usage_message = """
Usage: framework_well_log.py
                [--help]
                [--usage]
                [--longitude               Provide a longitude value]
                [--latitude                Provide a latitude value]
                [--x                       Provide a x coordinate]
                [--y                       Provide a y coordinate]
                [--rasters                 Provide a set of rasters from land surface to bedrock (descending order)]
                [--title                   Provide a title for the plot]
                [--thick                   Indicates all rasters except land surface and in thickness units]
                [--xy                      Provide a XY multiplier (convert x and y locations to other length units)]
                [--z                       Provide a Z multiplier (convert elevations to other vertical units)]
                [--x_axis                  Provide a label for x axis]
                [--y_axis                  Provide a label for y axis]
                [--color                   Provide a color specification file name containing a list of description and colors for each unit]
"""
                    
# =============================================================================
def Usage():
    frameworkUtils.display_error("Error: usage_message")

# =============================================================================

# Initialize arguments
#
band_nu               = None
longitude             = None
latitude              = None
x                     = None
y                     = None
rasters               = []
process_by            = "Elevation"
xy_multiplier         = 1.0
z_multiplier          = 1.0
image_title           = None
color_file            = None
y_axis_label          = None
x_axis_label          = None

# Set arguments
#
parser = argparse.ArgumentParser(prog=program)

parser.add_argument("--usage", help="Provide usage",
                    type=str)

parser.add_argument("--longitude", help="Provide a longitude value",
                    type=float, required=True)

parser.add_argument("--latitude", help="Provide a latitude value",
                    type=float, required=True)

parser.add_argument("--x_coordinate", help="Provide a x coordinate",
                    type=float, required=True)

parser.add_argument("--y_coordinate", help="Provide a y coordinate",
                    type=float, required=True)

parser.add_argument("--rasters", help="Provide a set of rasters from land surface to bedrock (descending order)",
                    type=str, required=True, nargs='+')

parser.add_argument("--title", help="Provide a title for the plot",
                    type=str, nargs='+')

parser.add_argument("--thick", help="Indicates all rasters except land surface and in thickness units",
                    type=str)

parser.add_argument("--xy", help="Provide a XY multiplier (convert x and y locations to other length units)",
                    type=float)

parser.add_argument("--z", help="Provide a Z multiplier (convert elevations to other vertical units)",
                    type=float)

parser.add_argument("--x_axis", help="Provide a label for x axis",
                    type=str, nargs='+')

parser.add_argument("--y_axis", help="Provide a label for y axis",
                    type=str, nargs='+')

parser.add_argument("--color", help="Provide a color specification file name containing a list of description and colors for each unit",
                    type=str, required=True)

parser.add_argument("--northwest_corner", help="Provide a x and y coordinate for northwest corner of the rasters",
                    type=str)

parser.add_argument("--northeast_corner", help="Provide a x and y coordinate for northeast corner of the rasters",
                    type=str)

parser.add_argument("--southwest_corner", help="Provide a x and y coordinate for southwest corner of the rasters",
                    type=str)

parser.add_argument("--southeast_corner", help="Provide a x and y coordinate for southeast corner of the rasters",
                    type=str)

# Parse arguments
#
args = parser.parse_args()

# Longitude
#
if args.longitude:

    longitude = args.longitude

# Latitude
#
if args.latitude:

    latitude = args.latitude

# X coordinate
#
if args.x_coordinate:

    x_coordinate = args.x_coordinate

# Y coordinate
#
if args.y_coordinate:

    y_coordinate = args.y_coordinate

# Rasters
#
if args.rasters:

    while len(args.rasters) > 0:

        raster = str(args.rasters.pop(0))
            
        if not os.path.isfile(raster):
            frameworkUtils.display_error("Error: Raster file %s does not exist" % raster)

        rc = gdal.Open( raster, GA_ReadOnly )
    
        if rc is None:
            frameworkUtils.display_error("Error: Raster %s is not a raster" % raster)

        # Remove suffix .tif
        #
        (root, tif_suffix)   = os.path.splitext(raster)
        if tif_suffix is not None:
            (dir, raster) = os.path.split(root)

        rasters.append((raster, rc))

# Title
#
if args.title:
    image_title = args.title
    
else:
    image_title = "Simulated Well Log"
    
# Y axis label
#
if args.y_axis:
    y_axis_label = args.y_axis
    
else:
    y_axis_label = "ELEVATION, IN FEET ABOVE SEA LEVEL"
    x_axis_label = "Cell width"
    
# X axis label
#
if args.x_axis:
    x_axis_label = args.x_axis
    
else:
    x_axis_label = "Cell width, in feet"
    
# Thickness
#
if args.thick:
    process_by = "Thickness"
    
# XY multiplier
#
if args.xy:
    xy_multiplier = args.xy
    
# Z multiplier
#
if args.z:
    z_multiplier = args.z
    
# Color specification file
#
if args.color:

    color_file = args.color

    if not os.path.isfile(color_file):
        frameworkUtils.display_error("Error: The file containing a list of color specification %s does not exist" % color_file)

# Register drives
#
gdal.AllRegister()

# Gather land-surface raster information
#
lsd_raster = rasters[0]
lsd_name   = lsd_raster[0]
lsd        = lsd_raster[1]

raster_bands = lsd.RasterCount
if raster_bands > 0:
    inband           = lsd.GetRasterBand(raster_bands)
    lsd_nodata       = lsd.GetRasterBand(raster_bands).GetNoDataValue()
    sDT              = gdal.GetDataTypeName(inband.DataType).lower()
    #print("Raster %s is type %s" % (lsd_name, str(sDT)))
    datasize         = gdal.GetDataTypeSize(inband.DataType)

    min = inband.GetMinimum()
    max = inband.GetMaximum()
    if min is None or max is None:
        (min,max) = inband.ComputeRasterMinMax(1)

    if min == -3.4028234663852886e+038:
        lsd_nodata = -3.4028234663852886e+038
        min = None

# Gather raster projection information
#
projection     = lsd.GetProjection()
geotransform   = lsd.GetGeoTransform()
ncols          = lsd.RasterXSize
nrows          = lsd.RasterYSize
nbands         = lsd.RasterCount

parms          = osr.SpatialReference()
parms.ImportFromWkt(str(projection))
projcs         = parms.GetAttrValue('PROJCS')
geogcs         = parms.GetAttrValue('GEOGCS')
spheroid       = parms.GetAttrValue('SPHEROID')
false_easting  = parms.GetProjParm('false_easting')
false_northing = parms.GetProjParm('false_northing')
datum          = parms.GetAttrValue('DATUM')
units          = parms.GetAttrValue('UNIT')
proj_name      = parms.GetAttrValue('PROJECTION')
if parms.IsGeographic():
    geographic   = "Geographic"
else:
    geographic   = "Projected"

# Set grid origin
#
x_origin    = geotransform[0]
y_origin    = geotransform[3]
x_cell_size = geotransform[1]
y_cell_size = geotransform[5]

x_left      = x_origin
x_right     = x_origin + ncols * x_cell_size
y_upper     = y_origin
y_lower     = y_origin + nrows * y_cell_size

# Check well log coordinates
#
if x_coordinate < x_left or  x_coordinate > x_right:
    frameworkUtils.display_error("Error: starting x coordinate (%s) is outside of raster (range %s to %s)" % (x_coordinate, x_left, x_right))

if y_coordinate < y_lower or y_coordinate > y_upper:
    frameworkUtils.display_error("Error: starting y coordinate (%s) is outside of raster (range %s to %s)" % (y_coordinate, y_lower, y_upper))
   
# Compute row
#
row    = int( ( y_upper - y_coordinate ) / abs( y_cell_size ) )
   
row_nu = ( y_upper - y_coordinate ) / abs( y_cell_size )

# Compute column
#
col    = int( abs( x_left - x_coordinate ) / x_cell_size )
   
col_nu = abs( x_left - x_coordinate ) / x_cell_size

# Check rasters for extent and other vital information
#
frameworkUtils.CheckRasters(rasters, x_origin, y_origin, nrows, ncols)

# Loop through rasters
#
rocks         = {}
units         = []
band_nu       = 1
elevation_max = -9999999999999999.99
elevation_min =  9999999999999999.99
cell_count    = 0

# Loop through rasters
#
for raster in rasters:

    raster_name          = raster[0]
    rc                   = raster[1]
    (dir_path, dir_name) = os.path.split(raster_name)

    line                 = "%15s%15s%15s" % (row, col, raster_name)

    (RasterVal, NoData)  = frameworkUtils.getRasterValue( raster_name, col, row, rc)

    # Raster information
    #
    if RasterVal is not None:
        RasterVal = float(RasterVal)
        line += "%15.2f" % RasterVal
        if RasterVal < elevation_min:
            elevation_min = RasterVal
        if RasterVal > elevation_max:
            elevation_max = RasterVal

        cell_count += 1
                
    else:
        line += "%15s" % RasterVal
                           
    # Set top elevation for rocks
    #
    if RasterVal is not None:
        if not raster_name in rocks:
            rocks[raster_name] = {}
        rocks[raster_name]['top'] = RasterVal

        units.append(raster_name)
                
# Check for units
#
if cell_count < 1:
    frameworkUtils.display_error("Error: Site is outside the extent of the geologic units")    

# Legend file
#
raster_legend = {}
if color_file is not None:
    # Open file
    #
    fh = open(color_file, 'r')
    if fh is None:
        frameworkUtils.display_error("Error: Can not open file %s" % color_file)
        
    # Remove user comment lines
    #
    while fh:
        line = fh.readline()
        if line[0] != "#" and line[0] != "@":
            break

    # Parse columns
    #
    line    = line.strip("\n|\r")
    cols    = line.split("\t")
    nFields = len(cols)
    i       = 0

    # Check columns
    #
    if nFields < 3:
        frameworkUtils.display_error("Error: Need at least 3 fields (raster, color, description) in file %s" % color_file)

    wanted_columns  = ["raster", "color", "description"]
    missing_columns = ["raster", "color", "description"]
    for column in cols:
        if column in wanted_columns:
            missing_columns.remove(column)

    if len(missing_columns) > 0:
        frameworkUtils.display_error("Error: Missing fields %s in file %s" % (", ".join(missing_columns), color_file))

    # Remove user comment lines
    #
    for line in fh:
        line    = line.strip("\n|\r")
        if line[0] == "#" and line[0] == "@":
            continue

        datacols    = line.split("\t")
        raster      = datacols[cols.index("raster")]
        description = datacols[cols.index("description")]
        colorhtml   = datacols[cols.index("color")]

        if raster not in raster_legend:
            raster_legend[raster] = {}
        raster_legend[raster]["description"] = description
        raster_legend[raster]["color"]       = frameworkUtils.HTMLColorToRGB(colorhtml)
        raster_legend[raster]["htmlcolor"]   = colorhtml

# Min and max
#
if elevation_min == elevation_max:
    elevation_min = elevation_max - 100
(y_min, y_max, y_interval) = frameworkUtils.get_max_min(elevation_min, elevation_max)

if elevation_min == y_min:
    y_min -= y_interval

x_min = 0.0
x_max = x_cell_size

# Output raster information
#
try:
    # Begin JSON format
    #
    print("Content-type: application/json\n")
    print("{")
    print("  \"status\"        : \"success\",")
    print("  \"nrows\"         : %15d," % nrows)
    print("  \"ncols\"         : %15d," % ncols)
    print("  \"nlays\"         : %15d," % len(rasters))
    print("  \"xy_multiplier\" : %15.2f," % xy_multiplier)
    print("  \"z_multiplier\"  : %15.2f," % z_multiplier)
    
    print("  \"longitude\"     : %15.2f," % longitude)
    print("  \"latitude\"      : %15.2f," % latitude)
    print("  \"easting\"       : %15.2f," % x_coordinate)
    print("  \"northing\"      : %15.2f," % y_coordinate)
    print("  \"row\"           : %15d," % row)
    print("  \"column\"        : %15d," % col)
          
    print("  \"cell_width\"    : %15.2f," % x_cell_size)

    # Build explanation
    #
    print("  \"explanation_fields\": [ \"unit\", \"color\", \"explanation\" ],")
    
    print("  \"explanations\" : ")
    print("             [")
    
    i = 0
    for raster in units:
        color       = raster_legend[raster]['htmlcolor']
        explanation = raster_legend[raster]['description']
    
        print("                 {")
        print("                   \"unit\": \"%s\"," % raster)
        print("                   \"color\": \"%s\"," % color)
        print("                   \"explanation\": \"%s\"" % explanation)
        comma = ","
        i += 1
        if i == len(units):
            comma = ''
        print("                 }%s" % comma)
    print("             ],")

    # Build well log fields
    #
    print("  \"well_log_fields\": [ \"unit\", \"top\", \"bottom\", \"color\", \"description\" ],")
    
    print("  \"well_log\" : ")
    print("             [")

    # Draw rasters
    #
    for i in range(len(units)):

        raster = units[i]
        
        top    = rocks[raster]['top']

        j      = i + 1
        if j >= len(units):
            bot = y_min
        else:
            bot = rocks[units[j]]['top']
            rocks[raster]['bot'] = bot

        # Set color according to specification file
        #
        if color_file is not None:

            description = raster_legend[raster]['description']
            color       = raster_legend[raster]['color']
            colorhtml   = raster_legend[raster]["htmlcolor"]

        # Set color according to random settings
        #
        else:

            description = raster
            r = "%d" % int(random.randrange(100, 230))
            b = "%d" % int(random.randrange(100, 230))
            g = "%d" % int(random.randrange(100, 230))

            colorhtml                            =  '#%02x%02x%02x' % (int(r), int(g), int(b))
        
            if raster not in raster_legend:
                raster_legend[raster]            = {}
                
            raster_legend[raster]['color']       = (r, g, b)
            raster_legend[raster]['description'] = description
            raster_legend[raster]['htmlcolor']   = colorhtml

        # Set layer
        #
        print("              {")
        print("               \"unit\"         : \"%s\"," % raster)
        print("               \"top\"          : %15.2f," % top)
        print("               \"bottom\"       : %15.2f," % bot)
        print("               \"color\"        : \"%s\"," % colorhtml)
        print("               \"description\"  : \"%s\"" % description)
            
        if i < len(units) - 1:
            print("               }, ")
        else:
            print("               } ")
    
    print("      ], ")
  
    print("  \"cell_count\":    %15d,"   % cell_count)
    print("  \"x_axis_min\":    %15.2f," % 0.0)
    print("  \"x_axis_max\":    %15.2f," % x_cell_size)
    print("  \"elevation_min\": %15.2f," % elevation_min)
    print("  \"elevation_max\": %15.2f," % elevation_max)
    print("  \"y_axis_max\":    %15.2f," % elevation_max)
    print("  \"y_axis_min\":    %15.2f"  % y_min)
      
    print("}");

except IOError:
    frameworkUtils.display_error("Error: Cannot create pdf file xsec.pdf")
