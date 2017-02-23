import os, sys, arcpy, json
# Please Ignore, Original Test Parameters:
#inputdata = r"C:\Users\lruiyang\Desktop\Age_Adjusted_rate_tool\fake_death.dbf"
#outputfolder = r"C:\Users\lruiyang\Desktop\Age_Adjusted_rate_tool"
#id_field = "GEOID10"
#age_field = "age"
#base_year = "2000"
#r_crit_level = "state"
#r_crit_state = "26"
#r_year = "2010"
#r_geolevel = "county"

## Get Input
#inputdata = arcpy.GetParameterAsText(0) # Input individual level dataset
#outputfolder = arcpy.GetParameterAsText(1) # Set Output folder
#id_field = arcpy.GetParameterAsText(2) # Identify field with Unique ID
#age_field = arcpy.GetParameterAsText(3) # Identify field with age recorded

#raw_data = arcpy.GetParameterAsText(4)

#raw_age = str(arcpy.GetParameterAsText(5)) # Get age category, it's the lower bound of age group

#nyear = float(arcpy.GetParameterAsText(6)) # Get number of year

#partial_data = str(arcpy.GetParameterAsText(7)).upper() # Turn on to switch to county only version

#ngbh_dict_loc = str(arcpy.GetParameterAsText(8)) # Location for the neighborhood relationship dictonary 

def RateStabilizingwithLocalData(inputdata, outputfolder, id_field, age_field, raw_data, raw_age, nyear, partial_data, ngbh_dict_loc):
	#Most common fine age_structure = [0,1,2,5,6,9,10,12,15,18,20,25,30,35,40,45,50,55,60,65,70,75,80,85]
	# Format age category to construct an age category array for calculation
	split_age = raw_age.split(";")
	num_age = []
	for str_a in split_age:
		num_age.append(int(str_a))
	age_structure = sorted(num_age)
	# This part of code enable a new feature in v0.9 - set an maximum age for oldest age category 
	if(age_structure[0] < 0):
		cap = age_structure[0]
		age_structure = age_structure[1:]
		age_structure.append(cap)
	if(age_structure[0] < 0): # Maximum of one cap per request
		raise ValueError("Please input one cap age only!!!")


	# Import Modules
	sys.path.append(os.path.split(os.path.realpath(__file__))[0])
	import fetch_data as fd # This module fetching data from Census Bureau
	fd = reload(fd) # Make sure newest module is loaded
	import construct_deathdata as cd # This module calculate rates from input data and fetched population data
	cd = reload(cd) # Make sure newest module is loaded
	import data_filter as df # This module filtered the result based on input
	df = reload(df) # Make sure newest module is loaded

	# Read local data fetched from 1st step 
	part1_input=open(raw_data, 'r')
	#exec(part1_input.read())
	r_crit_level = part1_input.readline().replace("\n","")
	r_crit = part1_input.readline().replace("\n","")
	age_vector = json.loads(part1_input.readline().replace("\n","")) 
	age_exp = json.loads(part1_input.readline().replace("\n","")) 
	r_num_table = json.loads(part1_input.readline().replace("\n","").replace("\'", "\"")) 
	r_note_col = json.loads(part1_input.readline().replace("\n","").replace("\'", "\""))

	[result, percent] = fd.summarize_to_age_structure (age_vector, age_exp, r_num_table, r_note_col, age_structure)

	if partial_data == 'TRUE':
		filt_dict = df.build_filt_dict (inputdata, id_field)
		[result, r_note_col] = df.filter_with_dict (result, r_note_col, "GEOID", filt_dict)   # Note Col structure: Name, State, County, (Tract,) GEOID

	# Write population matrix, and standard population structure into files
	f = open(outputfolder + "\\" + "PopAge_structure_" + r_crit_level + r_crit + ".csv", "w")
	head = True
	for row in result:
		if head:
			headerline = row
			head = False
		temp_text = cd.vect_to_str(row)
		f.writelines(temp_text + "\n")
	f.close()

	f = open(outputfolder + "\\" + "Standard_Age_structure.csv", "w")
	f.writelines(cd.vect_to_str(age_structure) + "\n")
	f.writelines(cd.vect_to_str(percent[0]) + "\n")
	f.close()

	# Call construct_deathdata function in cd module. This module returns the age adjusted rate
	outputpath = cd.construct_deathdata(r_note_col, result, percent, inputdata, outputfolder, id_field, age_field, nyear, ngbh_dict_loc=ngbh_dict_loc)

	# Update Schema.ini file
	f = open(outputfolder + "\\" + "schema.ini", "a")
	f.writelines("[Standard_Age_structure.csv]\n")
	f.writelines("Format=CSVDelimited\n")
	f.writelines("ColNameHeader=True\n")
	f.writelines("\n")
	f.writelines("[PopAge_structure_" + r_crit_level + r_crit + ".csv]\n")
	f.writelines("Format=CSVDelimited\n")
	f.writelines("ColNameHeader=True\n")

	i = 1
	for col in headerline:
		#arcpy.AddMessage(col)
		if col in ["NAME", "state", "county", "tract", "GEOID", "Alert"]:
			f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 30\n")
		elif col == "Population":
			f.writelines("Col" + str(i) + "=" + str(col) + " Long\n")
		else:
			f.writelines("Col" + str(i) + "=" + str(col) + " Double\n")
		i += 1

	f.writelines("\n")
	f.close()

	# Show Message to inform the output of the tool
	arcpy.AddMessage("\nFile Path:")
	arcpy.AddMessage("Age Adjust Rate: " + outputpath)
	arcpy.AddMessage("Age/Pop Table:   " + outputfolder + "\\" + "PopAge_structure_" + r_crit_level + r_crit + ".csv")
	arcpy.AddMessage("Age Structure:   " + outputfolder + "\\" + "Standard_Age_structure.csv\n")
