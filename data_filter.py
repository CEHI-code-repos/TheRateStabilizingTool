import os, arcpy

### This module is used to filter the original data to make it possible to do Bayesian smoothing for specific area

### Basic Function built-up
# Check if a key exist in a dictionary
def if_key_exist (key, dictionary):
	try:
		dictionary[key]
		return True
	except KeyError:
		return False

# Check if a key exist in a dataframe		
def if_fieldname_exist (field, fieldnames):	
	i = 0
	f_index = -1
	while i < len(fieldnames):
		if fieldnames[i] == field:
			f_index = i
			break
		i += 1
	if f_index == -1:
		raise ValueError("Input field name dose not exist in the data set!!!")
	return f_index

# Build county code dictionary from patients data
def build_filt_dict (indi_data, id_field):
	filt_dict = dict()
	cursor = arcpy.SearchCursor(indi_data)
	for row in cursor:
		cnty_id = str(row.getValue(id_field))[0:5]
		if if_key_exist(cnty_id, filt_dict):
			filt_dict[cnty_id] += 1
		else:
			filt_dict[cnty_id] = 1
	return filt_dict	

# Filter data based on county code dictionary
def filter_with_dict (data, note_col, id_field, filt_dict, cnty_filter = True):
	fieldnames = note_col[0]	
	#arcpy.AddMessage(fieldnames)
	f_index = if_fieldname_exist(id_field, fieldnames)

	result_index = []
	i = 1
	while i < (len(note_col)):
		row_data = note_col[i]
		if cnty_filter:
			key_value = row_data[f_index][0:5]
		else:
			key_value = row_data[f_index]
		if if_key_exist(key_value, filt_dict):
			result_index.append(i)
		i += 1
		
	filtered_result = [data[0]]
	filtered_note_col = [note_col[0]]
	for row_index in result_index:
		filtered_result.append(data[row_index])
		filtered_note_col.append(note_col[row_index])
	
	return [filtered_result, filtered_note_col]
	

def build_neighborhood_dict (input_shp, GeoIDfield, selection_type = "First_Order"):
	arcpy.AddMessage("Start to build neighborhood dictonary...")
	input_fields = arcpy.ListFields(input_shp)
	id_type=""
	duplicated=False
	arcpy.AddMessage("Checking file for potential errors...")
	for field in input_fields:
		if field.name == GeoIDfield:
			id_type = field.type
			break
	if id_type =="":
		arcpy.AddError("GEOID field does not exist!!!")
	sc = arcpy.SearchCursor(input_shp)
	IDlist = dict()
	row = sc.next()
	while row is not None:
		tempid = row.getValue(GeoIDfield)
		if if_key_exist(tempid, IDlist):
			duplicated=True
			arcpy.AddError("Duplicate GeoIDs detected in Shapefile... Please Clean data first...")
		else:	
			IDlist[row.getValue(GeoIDfield)] = 1
		row = sc.next()
	table_view = arcpy.MakeFeatureLayer_management(input_shp, "temp_tv")
	del sc
	del row
	
	arcpy.AddMessage("Searching for neighborhoods...")
	neighbor_dict = dict()
	i = 0
	for geoid in IDlist:
		temp_dict = dict()
		if not id_type == "String":
			arcpy.SelectLayerByAttribute_management(table_view,"NEW_SELECTION", GeoIDfield + " = " + str(geoid))
		else:
			arcpy.SelectLayerByAttribute_management(table_view,"NEW_SELECTION", GeoIDfield + " = '" + str(geoid)+"'")
		if selection_type == "First_Order":
			arcpy.SelectLayerByLocation_management(table_view,"INTERSECT", table_view, selection_type="ADD_TO_SELECTION")
			sc = arcpy.SearchCursor(table_view)
			row = sc.next()
			while row is not None:
				temp_dict[row.getValue(GeoIDfield)] = 1
				row = sc.next()
		neighbor_dict[geoid] = temp_dict
		if i % 100 == 0:
			arcpy.AddMessage("%.2f" % (float(i)/len(IDlist)*100) + "% Done..." )
		i += 1
	
	arcpy.Delete_management(table_view)
	if duplicated:
		arcpy.AddError("Please make sure your unique ID is unique!!!")
	else:
		arcpy.AddMessage("Neighborhood dictionary built successfully!!")
	return neighbor_dict











