import os, sys, arcpy, json, datetime
import data_filter as df # This module filtered the result based on input
df = reload(df) # Make sure newest module is loaded

#state_shp = str(arcpy.GetParameterAsText(0)) # Shapefile for selected state. Optional, only needed when calculate spatial Bayesian 

#GeoID = str(arcpy.GetParameterAsText(1)) # GEOID used to identify census boundaries 

#outputfolder = str(arcpy.GetParameterAsText(2)) # Output folder for dictonary file


def get_formatted_time():
	time_now = datetime.datetime.now()
	result = str(time_now.year) + "." + str0(time_now.month,2) + "." + str0(time_now.day,2) + " " + str0(time_now.hour,2) + ":" + str0(time_now.minute,2) + "." + str0(time_now.second,2)
	return result
	
def str0(input, length):
	temp = str(input)
	while len(temp) < length:
		temp = '0' + temp
	return temp


def build_neighborhood_dict_driver(state_shp, GeoID, outputfolder):
	ferror = open(r"C:\Users\rl53\Desktop\test\RST_Random_Seed_Test\error_log.txt", "a")
	ferror.write(get_formatted_time() + " ")
	ferror.write("Building Neighborhood Dict...\n")
	
	try:
		# Construct neighborhood dictionary  (df module should be imported in the main driver)
		ngbh_dict = df.build_neighborhood_dict (state_shp, GeoID, selection_type = "First_Order")

		arcpy.AddMessage("Exporting neighborhood structure...")
		output_file = outputfolder + "\\" + os.path.splitext(os.path.split(state_shp)[1])[0] + "_neighborhood_dict.data"
		f = open(output_file, "w")
		f.write(str(ngbh_dict))
		f.close()
		return output_file
	except Exception as e:
		arcpy.AddError(e.message)
		ferror.write(get_formatted_time() + " ")
		ferror.write(e.message)
		ferror.write("\n")
		ferror.close()