#!/usr/bin/python3

#!/usr/bin/env python
###############################################################################
# $Id$
#
# Project:  GDAL Python framework_xsec
# Purpose:  This script produces cross sectional view of subsurface layer for
#           a set of values along a transect establish by two or more location
#           points. The subsurface layers are represented by one or more
#           rasters that represent the land surface elevation and the underlying
#           the geologic units or other subsurface features.
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
import math, random

import argparse

import frameworkUtils

program      = "USGS Cross Section Script"
version      = "3.02"
version_date = "December 21, 2023"
usage_message = """
Usage: framework_xsec.py
                [--help]
                [--usage]
                [--longitude               Provide a longitude value]
                [--latitude                Provide a latitude value]
                [--points                  Provide two or more sets of x and y coordinates]
                [--rasters                 Provide a set of rasters from land surface to bedrock (descending order)]
                [--title                   Provide a title for the plot]
                [--thick                   Indicates all rasters except land surface and in thickness units]
                [--xy                      Provide a XY multiplier (convert x and y locations to other length units)]
                [--z                       Provide a Z multiplier (convert elevations to other vertical units)]
                [--x_axis                  Provide a label for x axis]
                [--y_axis                  Provide a label for y axis]
                [--color                   Provide a color specification file name containing a list of description and colors for each unit]
                [--logging                 Enable debugging output operational report
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
points                = []
rasters               = []
process_by            = "Elevation"
xy_multiplier         = 1.0
z_multiplier          = 1.0
image_title           = None
color_file            = None
y_axis_label          = None
x_axis_label          = None
logging               = None

# Set arguments
#
parser = argparse.ArgumentParser(prog=program)

parser.add_argument("--usage", help="Provide usage",
                    type=str)

parser.add_argument("--points", help="Provide two or more sets of x and y coordinates x,y",
                    type=str, required=True, nargs='+')

parser.add_argument("--rasters", help="Provide a set of rasters from land surface to bedrock (descending order)",
                    type=str, required=True, nargs='+')

parser.add_argument("--title", help="Provide a title for the plot",
                    type=str, nargs='+')

parser.add_argument("--x_axis", help="Provide a label for x axis",
                    type=str, nargs='+')

parser.add_argument("--y_axis", help="Provide a label for y axis",
                    type=str, nargs='+')

parser.add_argument("--longitude", help="Provide a longitude value",
                    type=float)
#                    type=float, required=True)

parser.add_argument("--latitude", help="Provide a latitude value",
                    type=float)
#                    type=float, required=True)

parser.add_argument("--thick", help="Indicates all rasters except land surface and in thickness units",
                    type=str)

parser.add_argument("--xy", help="Provide a XY multiplier (convert x and y locations to other length units)",
                    type=float)

parser.add_argument("--z", help="Provide a Z multiplier (convert elevations to other vertical units)",
                    type=float)

parser.add_argument("--color", help="Provide a color specification file name containing a list of description and colors for each unit",
                    type=str, required=True)

parser.add_argument("--log", "--logging", help="Enable debugging output operational report",
                    action="store_true")
                    
 
# Parse arguments
#
args = parser.parse_args()

# Sets of x and y coordinates
#
if args.points:
            
    if len(args.points) < 2:
        frameworkUtils.display_error("Error: Provide two or more sets of x and y coordinates")
            
    while len(args.points) > 0:

        point = str(args.points.pop(0)).split(",")
        try:
            x_coordinate = float(point[0])
        except:
            frameworkUtils.display_error("Error: Provide a x coordinate")
            
        try:
            y_coordinate = float(point[1])
        except:
            frameworkUtils.display_error("Error: Provide a y coordinate")

        points.append((x_coordinate, y_coordinate))

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

# Check points
#
if len(points) == 0:
    frameworkUtils.display_error("Error: Provide two or more sets of x and y coordinates")

# Title
#
if args.title:
    image_title = args.title
    
else:
    image_title = "Geologic Cross Section"
    
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

# Check cross section coordinates
#
point_number   = 0
total_distance = 0

for location in points:
    point_number += 1
    x_coordinate  = location[0]
    y_coordinate  = location[1]

    x2            = x_coordinate
    y2            = y_coordinate
    
    if x_coordinate < x_left or  x_coordinate > x_right:
        frameworkUtils.display_error("Error: x coordinate (%s) of location %d is outside of raster (range %s to %s)" % (x_coordinate, point_number, x_left, x_right))
    
    if y_coordinate < y_lower or y_coordinate > y_upper:
        frameworkUtils.display_error("Error: y coordinate (%s) of location %d is outside of raster (range %s to %s)" % (y_coordinate, point_number, y_lower, y_upper))

    if point_number > 1:
        x_distance      = (x2 - x1) * (x2 - x1)
        y_distance      = (y2 - y1) * (y2 - y1)
        xy_distance     = math.sqrt(x_distance + y_distance)
        total_distance += xy_distance

    x1            = x_coordinate
    y1            = y_coordinate
        

# Compute cross section segments
#
rocks             = {}
elevation_max     = -9999999999999999.99
elevation_min     =  9999999999999999.99
segment_no        = 0
cell_count        = 0
transect_distance = 0.0
total_distance    = 0.0
rowscols          = []

for location in points:
    x_coordinate  = location[0]
    y_coordinate  = location[1]

    x2            = x_coordinate
    y2            = y_coordinate
   
    # Compute row
    #
    end_row       = int( ( y_upper - y_coordinate ) / abs( y_cell_size ) )
       
    end_row_nu    = ( y_upper - y_coordinate ) / abs( y_cell_size )
    
    # Compute column
    #
    end_col       = int( abs( x_left - x_coordinate ) / x_cell_size )
       
    end_col_nu    = abs( x_left - x_coordinate ) / x_cell_size

    rowscols.append((end_row, end_col))

    if segment_no > 0:
        x_distance      = (x2 - x1) * (x2 - x1)
        y_distance      = (y2 - y1) * (y2 - y1)
        xy_distance     = math.sqrt(x_distance + y_distance)
        total_distance += xy_distance
        
        delta_row_nu = float( end_row - start_row ) * x_cell_size
        delta_col_nu = float( end_col - start_col ) * x_cell_size
        
        # Sloping transect line
        #
        if delta_col_nu != 0.0:
            slope     = delta_row_nu / delta_col_nu
            b         = start_row_nu - slope * start_col_nu
                        
            delta_col =  1
            if end_col_nu < start_col_nu:
                delta_col = -1;
        
            delta_row =  1
            if end_row_nu < start_row_nu:
                delta_row = -1;
        
        # No sloping transect line
        #
        else:
            slope     = 0.0
            b         = start_row_nu
            delta_col =  0
            delta_row =  1
            if end_row_nu < start_row_nu:
                delta_row = -1;
        
        # Logging
        #
        if logging is not None:
           print("Delta col %d Deleta row %d" % (delta_col, delta_row))
           print("Start row %d Start row nu %d" % (start_row, start_row_nu))
           print("End row %d End row %d" % (end_row, end_row_nu))
           print("Start col %d Start col nu %d" % (start_col, start_col_nu))
           print("End col %d End col nu %d" % (end_col, end_col_nu))
           print("Cell size %f" % x_cell_size)
           print (" %10s %10s %15s %15s %15s" % ("Row", "Col", "Distance", "delta row", "delta col", "transect_distance"))

        # Build sampling points along row direction
        #
        row = start_row + delta_row
        while (row != end_row):

            if slope != 0.0:
                col_nu = ( row - b ) / slope
            else:
                col_nu = start_col
                
            col                   = int(col_nu)
                           
            delta_row_nu          = ( start_row_nu - row ) * x_cell_size
            segment_row           = math.pow(delta_row_nu, 2.0)
            delta_col_nu          = ( start_col_nu - col_nu ) * x_cell_size
            segment_col           = math.pow(delta_col_nu, 2.0)
            distance              = math.sqrt(segment_row + segment_col)
            sample_distance       = transect_distance + distance
            dist                  = int(sample_distance)

            if logging is not None:
                print (" %10d %10d %15d %15.3f %15.3f %15.3f" % (row, col, dist, delta_row_nu, delta_col_nu, transect_distance))
        
            # Loop through rasters
            #
            raster_no = 0
            
            for raster in rasters:

                cell_count += 1
        
                raster_name = raster[0]
                rc          = raster[1]

                if logging is not None:
                    print ("\t %s" % raster_name)
        
                top, NoData = frameworkUtils.getRasterValue( raster_name, col, row, rc)
                bot         = None

                if logging is not None:
                    print ("\t %s" % str(top))
                
                raster_no  += 1
        
                # Raster information
                #
                if top is not None:
                    top = float(top)
                    if top < elevation_min:
                        elevation_min = top
                    if top > elevation_max:
                        elevation_max = top

                    for i in range(raster_no,len(rasters)):
                        bot_raster  = rasters[i]
                        bot_rc      = bot_raster[1]
                        bot, NoData = frameworkUtils.getRasterValue( raster_name, col, row, bot_rc)
                        if bot is not None:
                            bot = float(bot)
                            if bot < elevation_min:
                                elevation_min = bot
                            break
                        
                # Set rocks
                #
                if not raster_name in rocks:
                    rocks[raster_name] = {}
                if not dist in rocks[raster_name]:
                    rocks[raster_name][dist] = {}
         
                rocks[raster_name][dist]["top"] = top
                rocks[raster_name][dist]["bot"] = bot
                        
            row += delta_row
        
        # Build sampling points along column direction
        #
        col = start_col + delta_col
        while (col != end_col):
        
            row_nu                = slope * col + b
            row                   = int(row_nu)
                           
            delta_row_nu          = ( start_row_nu - row ) * x_cell_size
            segment_row           = math.pow(delta_row_nu, 2.0)
            delta_col_nu          = ( start_col_nu - col ) * x_cell_size
            segment_col           = math.pow(delta_col_nu, 2.0)
            distance              = math.sqrt(segment_row + segment_col)
            sample_distance       = transect_distance + distance
            dist                  = int(sample_distance)
                
            # Loop through rasters
            #
            raster_no = 0
            
            for raster in rasters:

                cell_count += 1
        
                raster_name = raster[0]
                rc          = raster[1]
        
                top, NoData = frameworkUtils.getRasterValue( raster_name, col, row, rc)
                bot         = None
                
                raster_no  += 1
        
                # Raster information
                #
                if top is not None:
                    top = float(top)
                    if top < elevation_min:
                        elevation_min = top
                    if top > elevation_max:
                        elevation_max = top

                    for i in range(raster_no,len(rasters)):
                        bot_raster  = rasters[i]
                        bot_rc      = bot_raster[1]
                        bot, NoData = frameworkUtils.getRasterValue( raster_name, col, row, bot_rc)
                        if bot is not None:
                            bot = float(bot)
                            if bot < elevation_min:
                                elevation_min = bot
                            break
                                   
                # Set rocks
                #
                if not raster_name in rocks:
                    rocks[raster_name] = {}
                if not dist in rocks[raster_name]:
                    rocks[raster_name][dist] = {}
        
                rocks[raster_name][dist]["top"] = top
                rocks[raster_name][dist]["bot"] = bot
                        
            col += delta_col

    x1                 = x_coordinate
    y1                 = y_coordinate
    start_row          = end_row
    start_row_nu       = end_row_nu
    start_col          = end_col
    start_col_nu       = end_col_nu
    segment_no        += 1
    transect_distance  = total_distance

#frameworkUtils.display_error("Done")    
        
                
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
    
x_max          = -9999999999999999.99
x_min          =  0.0
        
# Logging
#
if logging is not None:
   sys.exit( 0 )

# Plot rasters
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
    print("  \"cell_width\"    : %15.2f," % x_cell_size)
    
    print("  \"points\" : ")
    print("           {")
     
    i      = 0
    for location in points:
        x_coordinate  = location[0]
        y_coordinate  = location[1]
        row           = rowscols[i][0]
        col           = rowscols[i][1]

        i += 1
        print("            \"point_%d\" : " % i)
        print("                      {")
        print("                       \"easting\"       : %15.2f," % x_coordinate)
        print("                       \"northing\"      : %15.2f," % y_coordinate)
        print("                       \"row\"           : %15d,"   % row)
        print("                       \"column\"        : %15d"   % col)
        comment = ","
        if i >= len(points):
            comment = ""
        print("                      }%s" % comment)
          
    print("           },")
    
    # Draw rasters
    #
    print("  \"rocks\" : ")
    print("             [")

    i = 0
    for raster in rasters:

        i += 1

        raster_name = raster[0]
        colorhtml   = raster_legend[raster_name]['htmlcolor']
        description = raster_legend[raster_name]['description']

        # Set unit
        #
        print("              {")
        print("               \"unit\"         : \"%s\"," % raster_name)
        print("               \"color\"        : \"%s\"," % colorhtml)
        print("               \"description\"  : \"%s\"," % description)
        print("               \"array\"        : ")
        print("                                [");

        # Loop through distance
        #
        last_distance = 0.0
        ii            = 0

        for distance in sorted(rocks[raster_name].keys()):

            ii += 1

            # Set top and bottom
            #
            top    = rocks[raster_name][distance]['top']
            bot    = rocks[raster_name][distance]['bot']
            
            if top is not None:
                top_txt = "%.2f" % top
                if bot is not None:
                    bot_txt = "%.2f" % bot
                else:
                    bot_txt = "%.2f" % y_min
            else:
                top_txt = "null"
                bot_txt = "null"
                
            print("                                 [ %10.3f, %s, %s ]," % (last_distance, top_txt, bot_txt))
            if ii < len(sorted(rocks[raster_name].keys())):
                print("                                 [ %10.3f, %s, %s ]," % (distance, top_txt, bot_txt))
            else:
                print("                                 [ %10.3f, %s, %s ]" % (distance, top_txt, bot_txt))

            last_distance = distance
        
            if distance > x_max:
                x_max = distance

        print("                                ]");
        
        if i < len(rasters):
            print("                                },");
        else:
            print("                                }");
            
    print("             ],")
            

    # Build cell fields
    #
    print("  \"cell_fields\": [ \"unit\", \"top\", \"bottom\", \"color\", \"description\" ],")

    # Record raster information
    #
    print("  \"cells\" : ")
    print("             [")

    raster      = rasters[0]
    raster_name = raster[0]
    distances   = sorted(rocks[raster_name].keys())

    # Loop through distances
    #
    i = 0
    for distance in distances:

        i += 1

        # Loop through rasters
        #
        ii = 0
        for raster in rasters:

            raster_name = raster[0]
            colorhtml   = raster_legend[raster_name]['htmlcolor']
            description = raster_legend[raster_name]['description']

            # Set layer
            #
            top    = rocks[raster_name][distance]['top']
            bot    = rocks[raster_name][distance]['bot']
            if top is None:
                top_txt = "null"
            else:
                top_txt = "%.2f" % top
            if bot is None:
                bot_txt = "null"
            else:
                bot_txt = "%.2f" % bot

            # Set unit
            #
            print("              {")
            print("               \"unit\"         : \"%s\"," % raster_name)
            print("               \"color\"        : \"%s\"," % colorhtml)
            print("               \"description\"  : \"%s\"," % description)

            print("               \"top\"          : %s," % top_txt)
            print("               \"bottom\"       : %s" % bot_txt)

            ii += 1
            if i >= len(distances) and ii >= len(rasters):
                print("              }")
            else:
                print("              },")

    print("             ],")
            

    # Build explanation
    #
    print("  \"explanation_fields\": [ \"unit\", \"color\", \"explanation\" ],")
    
    print("  \"explanations\" : ")
    print("             [")
    
    i = 0
    for raster in rasters:

        raster_name = raster[0]
        color       = raster_legend[raster_name]['htmlcolor']
        explanation = raster_legend[raster_name]['description']
    
        print("                 {")
        print("                   \"unit\": \"%s\"," % raster_name)
        print("                   \"color\": \"%s\"," % color)
        print("                   \"explanation\": \"%s\"" % explanation)
        comma = ","
        i += 1
        if i == len(rasters):
            comma = ''
        print("                 }%s" % comma)
    print("             ],")
  
    print("  \"cell_count\":    %15d,"   % cell_count)
    print("  \"x_axis_min\":    %15.2f," % x_min)
    print("  \"x_axis_max\":    %15.2f," % x_max)
    print("  \"elevation_min\": %15.2f," % elevation_min)
    print("  \"elevation_max\": %15.2f," % elevation_max)
    print("  \"y_axis_max\":    %15.2f," % y_max)
    print("  \"y_axis_min\":    %15.2f"  % y_min)
      
    print("}");

except IOError:
    frameworkUtils.display_error("Error: Cannot create cross section")
