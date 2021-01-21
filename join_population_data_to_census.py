import arcpy, os, json, sys
import datetime as dt

#raw_data = r'C:\\Users\rl53\Desktop\test\RST_Random_Seed_Test\RawData_state37_tract.data'
#shp_container = r'C:\Users\rl53\Desktop\test\rst_test_join\tl_2010_37_tract10.shp'
#shp_Geoid = 'GEOID10'
#outputfolder = r'C:\Users\rl53\Desktop\test\rst_test_join'
#raw_age = '0;20;40;60;-80'
raw_data = arcpy.GetParameterAsText(0)
shp_container = arcpy.GetParameterAsText(1)
shp_Geoid = arcpy.GetParameterAsText(2)
outputfolder = arcpy.GetParameterAsText(3)
raw_age = str(arcpy.GetParameterAsText(4)) # Get age category, it's the lower bound of age group
	
sys.path.append(os.path.split(os.path.realpath(__file__))[0])	
import fetch_data as fd # This module fetching data from Census Bureau
fd = reload(fd) # Make sure newest module is loaded
import construct_deathdata as cd # This module calculate rates from input data and fetched population data
cd = reload(cd) # Make sure newest module is loaded

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
	
# Read local data fetched from 1st step 
part1_input=open(raw_data, 'r')
#exec(part1_input.read())
r_crit_level = part1_input.readline().replace("\n","").replace("u\"", "\"")
r_crit = part1_input.readline().replace("\n","").replace("u\"", "\"")
age_vector = json.loads(part1_input.readline().replace("\n","").replace("u\"", "\"")) 
age_exp = json.loads(part1_input.readline().replace("\n","").replace("u\"", "\"")) 
r_num_table = json.loads(part1_input.readline().replace("\n","").replace("\'", "\"").replace("u\"", "\"")) 
r_note_col = json.loads(part1_input.readline().replace("\n","").replace("\'", "\"").replace("u\"", "\""))

[result, percent] = fd.summarize_to_age_structure (age_vector, age_exp, r_num_table, r_note_col, age_structure)

i = 0
age_structure_note = []
age_structure_note.extend(age_structure)
for each_element in age_structure_note:
	if i < len(age_structure_note) and i > 0:
		age_structure_note[i-1] = 'age' + str(age_structure_note[i-1]) + '_' + str(abs(each_element))
		if i == len(age_structure_note) - 1:
			if int(each_element) < 0:
				age_structure_note.remove(each_element)
			else:
				age_structure_note[i] = 'age' + str(each_element) + 'p'
	i += 1
	

# Write population matrix, and standard population structure into files
outfilename = "PopAge_structure_" + os.path.splitext(os.path.split(raw_data)[1])[0].split('_')[1] + '_'  + os.path.splitext(os.path.split(raw_data)[1])[0].split('_')[2] + ".csv"
f = open(outputfolder + "\\" + outfilename, "w")
head = True
for row in result:
	if head:
		headerline = age_structure_note + row[len(age_structure_note):]
		head = False
		temp_text = cd.vect_to_str(headerline)
	else:
		temp_text = cd.vect_to_str(row)
	f.writelines(temp_text + "\n")
f.close()

# Update Schema.ini file
f = open(outputfolder + "\\" + "schema.ini", "a")
f.writelines("["+outfilename+"]\n")
f.writelines("Format=CSVDelimited\n")
f.writelines("ColNameHeader=True\n")

i = 1
for col in headerline:
	#arcpy.AddMessage(col)
	if col in ["NAME", "state", "county", "tract", "GEOID"]:
		f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 30\n")
	elif col == "Alert":
		f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 100\n")
	elif col == "Population":
		f.writelines("Col" + str(i) + "=" + str(col) + " Long\n")
	else:
		f.writelines("Col" + str(i) + "=" + str(col) + " Double\n")
	i += 1

f.writelines("\n")
f.close()

temp_shp = arcpy.MakeFeatureLayer_management(shp_container, 'temp_shp')
max_left = len(arcpy.Describe(temp_shp).fields)
arcpy.AddJoin_management(temp_shp, shp_Geoid, outputfolder+'\\'+outfilename, 'GEOID')

# Create age fields based on age structure. This will help to keep only important fields.
age_fields = []
for i in range(len(age_structure)):
    if i < len(age_structure)-1:
        age_fields.append('age{0}_{1}'.format(age_structure[i], age_structure[i+1]))
    else:
        age_fields.append('age{0}p'.format(age_structure[i]))

fms = arcpy.FieldMappings()

fms_left = arcpy.FieldMappings()
fms_left.addTable(temp_shp)
i = 0
for each_fm in fms_left:
	if i < 	max(max_left-2,0):
		fms.addFieldMap(each_fm)
	elif each_fm.getInputFieldName(0).split('.')[-1] in age_fields:
		temp = each_fm.outputField
		temp.name = each_fm.getInputFieldName(0).split('.')[-1]
		each_fm.outputField = temp
		fms.addFieldMap(each_fm)
		
	i += 1
	
outshp = os.path.splitext(os.path.split(shp_container)[1])[0]+'_pop'
arcpy.FeatureClassToFeatureClass_conversion(temp_shp, outputfolder, outshp, field_mapping = fms)
