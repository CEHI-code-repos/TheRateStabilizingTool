import os, arcpy, numpy, numbers, ast
import datetime as dt
from operator import itemgetter
import data_filter as df # This module filtered the result based on input
df = reload(df) # Make sure newest module is loaded

### Basic Function built-up
# Check if a key exist in a dictionary
def if_key_exist (key, dictionary):
	try:
		dictionary[key]
		return True
	except KeyError:
		return False
	
# Generate a sequence of number
def sequence(start, length, step=1):
	result = []
	i = 0
	while i < length:
		result.append(start + i * step)
		i += 1
	return result

# Erase certain column from dataframe
def col_erase(datalist, nvector):
	i = 0 
	while i < len(nvector):
		if(nvector[i] < 0):
			nvector[i] += len(datalist[0])
		i += 1
	seq = sequence(0, len(datalist[0]), 1)
	select = [n for n in seq if not n in nvector]
	result = []
	for row in datalist:
		get_num = itemgetter(*select)(row)
		if type(get_num) is tuple:
			result.append(list(get_num))
		elif type(get_num) is list:
			result.append(get_num)
		elif type(get_num) is int or type(get_num) is float:
			result.append([get_num])
	return result

# Column merge two dataset
def c_merge (df1, df2):
	if (len(df1) != len(df2)):
		raise ValueError("Two data frames don't have the same number of row")
	i = 0
	result = []
	while i < len(df1):
		result.append(df1[i]+ df2[i])
		i += 1
	return result

# Create zero matrix
def create_zero_mat (nrow, ncol):
	result = []
	i = 0
	while i < nrow:
		result.append(sequence(0, ncol, 0))
		i += 1
	return result

# Build dictionary from dataframe
def df_to_dict(datalist, key_index):
	result = dict()
	for row in datalist:
		result.update({row[key_index]: row})
	return result

# Index right slot for age
def index_age (age, age_struct):
	i = 0
	while i < len(age_struct):
		if i == 0 and age < age_struct[0]:
			return 0
		elif age_struct[i] < 0:
			if(age < abs(age_struct[i])):
				return i - 1
			else:
				return -1
		elif i + 1 == len(age_struct):
			return i
		elif age >= age_struct[i] and age < age_struct[i + 1]:
			return i
		i += 1

# Vector divide X1i/y1i
def vector_divide(v1, v2):
	result = []
	if (len(v1) != len(v2)):
		raise ValueError("Length of Two Vector is not the same")
	else:
		i = 0
		while i < len(v1):
			if(v2[i] == 0):
				result.append(0)
			else:
				result.append(float(v1[i])/float(v2[i]))
			i += 1
		return result

# Vector multiplies X1i/y1i
def vector_multi (v1,v2):
	result = []
	if isinstance(v2, numbers.Number):
		i = 0
		while i < len(v1):
			result.append(float(v1[i])*float(v2))
			i += 1
		return result
	elif (len(v1) != len(v2)):
		raise ValueError("Length of Two Vector is not the same")
	else:
		i = 0
		while i < len(v1):
			result.append(float(v1[i])*float(v2[i]))
			i += 1
		return result
		
# Vector plus X1i + Y1i
def vector_plus (v1, v2):
	result = []
	if isinstance(v2, numbers.Number):
		i = 0
		while i < len(v1):
			result.append(float(v1[i]) + float(v2))
			i += 1
		return result
	elif (len(v1) != len(v2)):
		raise ValueError("Length of Two Vector is not the same")
	else:
		i = 0
		while i < len(v1):
			result.append(float(v1[i]) + float(v2[i]))
			i += 1
		return result

# Data frame Row sum
def row_sum (df):
	result = []
	for row in df:
		result.append([sum(row)])
	return result
	
def col_sum(df):
	result = []
	i = 0
	while i < len(df[0]):
		temp = 0
		for row in df:
			temp += row[i]
		result.append(temp)
		i += 1
	return result
		
	
# Construct string from vector
def vect_to_str(vector):
	result = ""
	for elem in vector:
		if(elem == str):
			result += "\'" + elem + "\', "
		else:
			result += str(elem) + ", "
	result = result[0:len(result)-2].replace(" ", "")
	return result
	
# Sample Gamma function
def gamma_sample (shape, scale, nSample):
	numpy.random.seed(20151201)
	if shape == 0:
		g_sample1000 = sequence(-1, nSample, 0)
	else:
		g_sample1000 = numpy.random.gamma(shape, scale, nSample)
	return g_sample1000

# Sum a numeric matrix
def df_sum(df):
	result = 0
	for row in df:
		result += sum(row)
	return result

# Get prior events and prior population for each age categories in each geographic area
def get_a0_n0 (result, ncol, death_count, percentile, a00=0, n00=0):  # Set a00 n00 0 for global a0 and n0 calculation
	pop_mat = col_erase(result, sequence(-1, ncol, -1))
	case_mat = col_erase(death_count, sequence(-1, ncol, -1))
	#n_tot = df_sum(pop_mat)
	#c_tot = df_sum(case_mat)
	n_tot = col_sum(pop_mat)
	c_tot = col_sum(case_mat)
	lamadj = vector_divide(vector_plus(c_tot, a00), vector_plus(n_tot, n00))

	if n00 == 0:
		num_col = len(result[0]) - ncol
		n0 = []
		i = 0
		while i < num_col:
			temp = []
			for row in pop_mat:
				temp.append(row[i])
			s_temp = sorted(temp)
			n0.append(s_temp[int(percentile * len(result))])
			i += 1
	else:
		n0 = n00
		
	a0adj = vector_multi(n0, lamadj)
	return [a0adj, n0]
	
# Sample the vector based on percentile, Unit in /100,000people
def sample_percentile (vector, percentile_vector):
	temp = sorted(vector)
	result = []
	for percent in percentile_vector:
		result.append(temp[int(percent * len(vector))]*100000)
	return result

def col_divide(df, ncol, num, header = False):
	if header:
		i = 1
	else:
		i = 0
	while i < len(df):
		df[i][ncol] /= num
		i += 1
	return df

### Function to be call by the main core. It is the wrapped function for this module
def construct_deathdata (r_note_col, result, percent, inputdata, outputfolder, id_field, age_field, nyear, state_shp="", GeoID="", ngbh_dict_loc=""):
	nyear = int(nyear)
	arcpy.AddMessage("Constructing disease/death rate from individual records...")
	## Construct basic matrix for each geographic boundary
	num_count = len(percent[0])
	header_zero = result[0][0:num_count]
	if(header_zero[len(header_zero)-1] < 0):
		num_count -= 1
	zero_mat = create_zero_mat(len(result)-1, num_count)

	death_count = c_merge(zero_mat, r_note_col[1:])
	death_count_dict = df_to_dict(death_count, len(death_count[0])-1)

	## Go through each record to generate disease/death count in each age categories for each geographic boundary 
	cursor = arcpy.SearchCursor(inputdata)
	errorID = []
	for row in cursor:
		temp_ID = str(row.getValue(id_field))
		temp_age = row.getValue(age_field)
		if(not if_key_exist(temp_ID, death_count_dict)):
			errorID.append(temp_ID)
		else:
			idx = index_age(temp_age, header_zero)
			if(idx != -1):
				death_count_dict[temp_ID][idx] += 1

	###
	### For Empirical Bayesian 
	###
	ncol = len(r_note_col[0])
	[a0, n0] = get_a0_n0 (result[1:], ncol, death_count, 0.1)
	i = 0
	aar_bayesian = []
	field_name = ["Baye_AAR", "Baye_2p5", "Baye_97p5"]
	aar_bayesian.append(field_name)
	while i < len(death_count):
		Y = death_count[i][0:num_count]
		n = result[i+1][0:num_count]
		j = 0
		age_group = []
		while j < num_count:
			g_samps_per = vector_multi(gamma_sample(Y[j] + a0[j], 1.0/(n[j] + n0[j]), 1000), percent[0][j])
			age_group.append(g_samps_per)
			j += 1
		aar_bayesian.append(sample_percentile(col_sum(age_group), [0.5, 0.025, 0.975]))
		i += 1

	aar_bayesian = col_divide(aar_bayesian,0,nyear, True)
	aar_bayesian = col_divide(aar_bayesian,1,nyear, True)
	aar_bayesian = col_divide(aar_bayesian,2,nyear, True)
	### Bayesian ends here


	arcpy.AddMessage("Calculating age adjusted rate...")
	# Calculate Age adjusted rate for each county
	i = 1
	num_rate = []
	while i < len(result):
		key_id = r_note_col[i][len(r_note_col[0])-1]
		num_rate.append(vector_multi(vector_divide(death_count_dict[key_id][0:num_count], result[i][0:num_count]), 100000))
		i += 1

	rate = []
	for row in num_rate:
		rate.append(vector_multi(percent[0], row))
	age_adj_rate = [["Age_adjust_rate"]]
	age_adj_rate.extend(col_divide(row_sum(rate),0,nyear))


	###
	### For Empirical Bayesian
	###
	age_adj_rate = c_merge(age_adj_rate, aar_bayesian)

	aver_rate = float(sum(a0)) / sum(n0)

	pop_seq = col_erase(result[1:], sequence(-1, ncol, -1))
	pop_sum = row_sum(pop_seq)
	#arcpy.AddMessage(len(pop_sum))
	#arcpy.AddMessage(len(aar_bayesian))
	i = 1
	while i < len(aar_bayesian):
		row = pop_sum[i-1]
		if float(aar_bayesian[i][0]) < float(aar_bayesian[i][2])-float(aar_bayesian[i][1]):
			row.append("Alert:Unreliable Estimate!!!!")
		else:
			row.append("-")
		i += 1
	pop_name = [["Population", "Alert"]]
	pop_name.extend(pop_sum)
	### Bayesian ends here

	
	
	if state_shp != "" or ngbh_dict_loc != "":
		arcpy.AddMessage("Spatial smoothing the results...")
		
		### Spatial Bayesian Starts here
		if ngbh_dict_loc != "":
			fngbh = open(ngbh_dict_loc, 'r')
			ngbh_dict = ast.literal_eval(fngbh.read())
			fngbh.close()
			del fngbh
		else:
			ngbh_dict = df.build_neighborhood_dict (state_shp, GeoID, selection_type = "First_Order")

		
		i = 0
		sp_aar_bayesian = []
		field_name = ["SpBay_AAR", "SpBay_2p5", "SpBay_97p5"]
		sp_aar_bayesian.append(field_name)
		while i < len(death_count):
			Geokey = result[i+1][-1]
			data_list_dict = ngbh_dict[Geokey]
			[temp_result, temp_col] = df.filter_with_dict (result, r_note_col, "GEOID", data_list_dict, cnty_filter = False)
			death_with_header = [result[0]]
			death_with_header.extend(death_count)
			[temp_death, temp_dcol] = df.filter_with_dict (death_with_header, r_note_col, "GEOID", data_list_dict, cnty_filter = False)

			[a0i, n0i] = get_a0_n0 (temp_result[1:], ncol, temp_death[1:], 0.1, a0, n0)
			
			Y = death_count[i][0:num_count]
			n = result[i+1][0:num_count]
			j = 0
			sp_age_group = []
			while j < num_count:
				sp_g_samps_per = vector_multi(gamma_sample(Y[j] + a0i[j], 1.0/(n[j] + n0i[j]), 1000), percent[0][j])
				sp_age_group.append(sp_g_samps_per)
				j += 1
			sp_aar_bayesian.append(sample_percentile(col_sum(sp_age_group), [0.5, 0.025, 0.975]))
			i += 1

		sp_aar_bayesian = col_divide(sp_aar_bayesian,0,nyear, True)
		sp_aar_bayesian = col_divide(sp_aar_bayesian,1,nyear, True)
		sp_aar_bayesian = col_divide(sp_aar_bayesian,2,nyear, True)
		age_adj_rate = c_merge(age_adj_rate, sp_aar_bayesian)
		

	output = c_merge(age_adj_rate, r_note_col)
	output_pop = c_merge(output, pop_name)

	# Write output to csv file
	filename = os.path.splitext(os.path.split(inputdata)[1])[0]
	f = open(outputfolder + "\\" + "age_adjust_" + filename + ".csv", "w")
	head = True
	for row in output_pop:
		if head:
			head = False
			headerline = row
		temp_text = vect_to_str(row)
		f.writelines(temp_text + "\n")
	f.close()

	# Write Schema.ini file
	f = open(outputfolder + "\\" + "schema.ini", "w")
	f.writelines("[age_adjust_" + filename + ".csv]\n")
	f.writelines("Format=CSVDelimited\n")
	f.writelines("ColNameHeader=True\n")
	i = 1
	for col in headerline:
		#arcpy.AddMessage(col)
		if col in ["NAME", "state", "county", "tract", "GEOID", "Alert"]:
			f.writelines("Col" + str(i) + "=" + col + " Text Width 30\n")
		elif col == "Population":
			f.writelines("Col" + str(i) + "=" + col + " Long\n")
		else:
			f.writelines("Col" + str(i) + "=" + col + " Double\n")
		i += 1
	f.writelines("\n")
	f.close()
		
	
	if(errorID != []):
		arcpy.AddWarning("Warning: Following ID is not identified in census data: " + str(errorID) + "!!!")
	else:
		arcpy.AddMessage("Age adjusted rate successfully calculated with no error!!!")
	
	return (outputfolder + "\\" + "age_adjust_" + filename + ".csv")



