import os, sys, arcpy, json
import data_filter as df # This module filtered the result based on input
df = reload(df) # Make sure newest module is loaded

state_shp = str(arcpy.GetParameterAsText(0)) # Shapefile for selected state. Optional, only needed when calculate spatial Bayesian 

GeoID = str(arcpy.GetParameterAsText(1)) # GEOID used to identify census boundaries 

outputfolder = str(arcpy.GetParameterAsText(2)) # Output folder for dictonary file

# Construct neighborhood dictionary  (df module should be imported in the main driver)
ngbh_dict = df.build_neighborhood_dict (state_shp, GeoID, selection_type = "First_Order")

arcpy.AddMessage("Exporting neighborhood structure...")
output_file = outputfolder + "\\" + os.path.splitext(os.path.split(state_shp)[1])[0] + "_neighborhood_dict.data"
f = open(output_file, "w")
f.write(str(ngbh_dict))
f.close()