#! /usr/bin/perl

=head1 NAME

Retrieves Framework cross section geometry information 

=head1 HISTORY

version 1.05  November 05, 2012

=head1 DESCRIPTION

This program retrieves Framework cross section geometry information for a set of cells
along a cross-section profile from a set of array files in tiff format. The information
is used to generate an image of a cross section of this geologic information.

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

#use JSON;

use Cwd;

# Globals
# 
my @return_string = ();
my @fields        = ();
my $os            = $^O;

my $presentDir    = getcwd();

# Parse arguments to perl script 
# 
$query = new CGI; 

# Points
# 
my @points = ();
if($point = $query->param('points')) 
  {
  if($point eq "")
    {
     my @return_string = ("\"error\": " . "\"Missing two or more sets of x and y coordinates\"");
     &error(\@return_string);
    }
}
if(not defined($point))
  {
   my @return_string = ("\"error\": " . "\"Missing two or more sets of x and y coordinates\"");
   &error(\@return_string);
  }
my @points = split(/\s+/,$point);
if(scalar(@points) < 2)
  {
   my @return_string = ("\"error\": " . "\"Missing two or more sets of x and y coordinates\"");
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
@rasters = split(/\s+/,$raster);
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

# Build argument list
#
my $program_arguments = "";
$program_arguments   .= "--points " . join(" ", @points) . " ";
$program_arguments   .= "--rasters " . join(" ", @rasters) . " ";
$program_arguments   .= "--color $color_file ";

#$program_arguments   .= "--rasters " . join(" ", map { "tiffs/" . $_ . ".tif" } @rasters) . " ";

# Build image
#
my $program      = join("/", $presentDir, "/", "framework_xsec.py");

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
