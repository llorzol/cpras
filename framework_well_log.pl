#! /usr/bin/perl

=head1 NAME

Retrieves Framework cross section geometry information 

=head1 HISTORY

version 1.05  November 05, 2012

=head1 DESCRIPTION

This program retrieves Framework well log geometry information for a location
through set of geologic rasters to produce an image of this geologic information.

=over 2

=head1 AUTHOR

Leonard L. Orzol 

U. S. Geological Survey - WRD

10615 SE. Cherry Blossom Drive 

Portland, Oregon 97216 USA

Internet: llorzol@usgs.gov 

Phone: (503) 251-3270 

=head1 COPYRIGHT

Copyright 2012 Leonard L Orzol <llorzol@usgs.gov>.

Permission is granted to copy, distribute and/or modify this 
document under the terms of the GNU Free Documentation 
License, Version 1.2 or any later version published by the 
Free Software Foundation; with no Invariant Sections, with 
no Front-Cover Texts, and with no Back-Cover Texts.

=head1 DISCLAIMER

Although this program has been used by the U.S. Geological Survey, 
no warranty, expressed or implied, is made by the USGS as to the 
accuracy and functioning of the program and related program 
material nor shall the fact of distribution constitute any such 
warranty, and no responsibility is assumed by the USGS in 
connection therewith. 

=cut

#use strict;
use CGI qw/param/;

# Globals
# 
my @return_string = ();
my @fields        = ();

# Parse arguments to perl script 
# 
$query = new CGI; 

# Latitude
# 
if($latitude = $query->param('latitude')) {
  if($latitude eq "") 
    {
     my @return_string = ("\"error\": " . "\"Missing a value for longitude or latitude\"");
     &error(\@return_string);
    }
}
if(not defined($latitude))
  {
   my @return_string = ("\"error\": " . "\"Missing a value for latitude\"");
   &error(\@return_string);
  }

# Longitude
# 
if($longitude = $query->param('longitude')) {
  if($longitude eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing a value for longitude or latitude\"");
     &error(\@return_string);
    }
}
if(not defined($longitude))
  {
   my @return_string = ("\"error\": " . "\"Missing a value for longitude\"");
   &error(\@return_string);
  }

# X coordinate
# 
my $x_coordinate = undef;
if($x_coordinate = $query->param('x_coordinate')) 
  {
  if($x_coordinate eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing a value for x coordinate\"");
     &error(\@return_string);
    }
}
if(not defined($x_coordinate))
  {
   my @return_string = ("\"error\": " . "\"Missing a value for x coordinate\"");
   &error(\@return_string);
  }

# Y coordinate
# 
my $y_coordinate = undef;
if($y_coordinate = $query->param('y_coordinate')) 
  {
  if($y_coordinate eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing a value for y coordinate\"");
     &error(\@return_string);
    }
}
if(not defined($y_coordinate))
  {
   my @return_string = ("\"error\": " . "\"Missing a value for y coordinate\"");
   &error(\@return_string);
  }

# Rasters
# 
my @rasters = ();
if($raster = $query->param('rasters')) 
  {
  if($raster eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing one or more sets of framework rasters\"");
     &error(\@return_string);
    }
}
if(not defined($raster))
  {
   my @return_string = ("\"error\": " . "\"Missing one or more sets of framework rasters\"");
   &error(\@return_string);
  }
#@rasters = split(/\s+/,$raster);
@rasters = split(/,/,$raster);
if(scalar(@rasters) < 1)
  {
   my @return_string = ("\"error\": " . "\"Missing one or more sets of framework rasters\"");
   &error(\@return_string);
  }

# Color specification file
# 
my $color_file = undef;
if($color_file = $query->param('color')) 
  {
  if($color_file eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing a file name for Color specification file\"");
     &error(\@return_string);
    }
}

# Output format 
# 
if($output_format = $query->param('output')) 
  {
  if($output_format eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing output format\"");
     &error(\@return_string);
    }
}

# Build argument list
#
my $program_arguments = "";
$program_arguments   .= "--latitude " . sprintf("%.6f ",$latitude);
$program_arguments   .= "--longitude " . sprintf("%.6f ",$longitude);
$program_arguments   .= "--x_coordinate " . sprintf("%.2f ",$x_coordinate);
$program_arguments   .= "--y_coordinate " . sprintf("%.2f ",$y_coordinate);
$program_arguments   .= "--rasters " . join(" ", @rasters) . " ";
$program_arguments   .= "--color $color_file ";

#$program_arguments   .= "--rasters " . join(" ", map { "tiffs/" . $_ . ".tif" } @rasters) . " ";

# Build image
#
my $program      = "/afs/.usgs.gov/www/or.water/cgi-bin/nacp/framework_well_log.py";
my $program      = "/var/www/cgi-bin/columbia/framework_well_log.py";

if(! -e $program)
  {
   my @return_string = ("\"warning\": " . "\"Program $program does not exist\""); 
   &error(\@return_string);   
  }

if(! -x $program)
  {
   my @return_string = ("\"warning\": " . "\"Insufficient rights to run $program\""); 
   &error(\@return_string);   
  }

my $Line = `$program $program_arguments`;

print "$Line";

exit(0); 

exec ("program $program_arguments")   or print STDERR "couldn't exec xsec: $!";
     
my $error = "Here 6";
my @return_string = ("\"error\":  \"$error\"");
&error(\@return_string);

exit(0); 

if( $? == -1 )
  {
   my @return_string = ("\"error\": " . "\"command failed: $!\"");
   &error(\@return_string);
  }
else
  {
   my $error = sprintf("command exited with value %d\n", $? >> 8);
   my @return_string = ("\"error\":  \"$error\"");
   &error(\@return_string);
  }
# Finished
#
exit(0); 
  
#         Subroutines
#
#===============================================================

sub error 
  {
   my $return_ref = shift;
   my @return_string   = @{$return_ref};
   
   # Html Header
   #
   print ("Content-type: application/json\n\n"); 
   
   # Error
   #
   print "{ " . "\n";

   print "    \"status\": " . "\"fail\",\n";
   print "    " . join(",\n    ",@return_string) . "\n";
   
   print "} " . "\n";

   # Finished
   #
   exit(0); 
  }
