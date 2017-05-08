# read result from Random seed test
import arcpy, os, numpy

rnd_input = r"C:\Users\rl53\Desktop\test\RST_Random_Seed_Test\Random_RST_TEST"
file_name = 'age_adjust_NC_HeartDisease0608.csv'
ID_index = 11
collect_field_num = 7
output_file = r"C:\Users\rl53\Desktop\test\RST_Random_Seed_Test\rnd_seed_summary.csv"



# Check if a key exist in a dictionary
def if_key_exist (key, dictionary):
	try:
		dictionary[key]
		return True
	except KeyError:
		return False

def FileSearcher(folder, suffix): #suffix should not include '.'
	allfile = os.listdir(folder)
	return_value = []
	if(len(allfile) > 0):
		i = 0
		while(i < len(allfile)):
			temp = allfile[i].split('.')
			if (len(temp) > 1):
				act_suffix = temp[len(temp)-1]
			else:
				act_suffix = ''
			if(act_suffix == suffix):
				wholepath = folder + "\\" + allfile[i]
				return_value.append(wholepath)
			i += 1
	return return_value
	
# Push one element out of stack
def push_element(vector):
	return[vector[0], vector[1:]]

# Function to Push a word from a comma separated string
def push_word(string):
	i = 0
	quote = False
	while i < len(string):
		if quote:
			if string[i] == "\"" or string[i] == "\'":
				return [string[1:i], string[i+1:]]
			else:
				i += 1
		else:
			if(string[i] == "\"" or string[i] == "\'"):
				quote = True
			elif string[i] == "," or string[i] == "]":
				return [string[0:i], string[i:]]
			i += 1
	return [string[0+i], string[i+1:]]

# Function to Construct array from a comma separated string
def construct_list(string, listO):
	#arcpy.AddMessage("      Constructing list...")
	char = string[0]
	if char != "[":
		raise ValueError("Input is not a list string")
	string = string[1:]
	char = string[0]
	string = string[1:]
	while char != "]" and char != "":
		if char == "[":
			templist = list()
			[templist, string] = construct_list(char + string, list())
			listO.append(templist)
		elif char == "]":
			return [listO, string]
		elif char != "," and char != " " and  char != "\n":
			[word, string] = push_word(char+string)
			listO.append(word)
		char = string[0]
		string = string[1:]
	#arcpy.AddMessage("      List Constructed...")
	return [listO, string]
	
rnd_folder = FileSearcher(rnd_input, "")

# Structure -- id: [[crude],[Baye],[baye2p5],[baye97p5],[SpBaye],[SpBaye2p5],[SpBaye97p5]]
test_summary = dict()
for each_rnd_folder in rnd_folder:
	each_file = each_rnd_folder + "\\" + file_name
	print each_file
	f = open(each_file, 'r')
	field_name = construct_list('['+f.readline()+']', list())[0]
	read_input = f.readline()
	while read_input:
		row = construct_list('['+read_input+']', list())[0]
		id = row[ID_index]
		if if_key_exist(id, test_summary):
			i = 0
			while i < collect_field_num:
				test_summary[id][field_name[i]].append(float(row[i]))
				i += 1
		else:
			tb_struct = dict()
			i = 0
			while i < collect_field_num:
				tb_struct[field_name[i]]  = [float(row[i])]
				i += 1
			test_summary[id] = tb_struct
		read_input = f.readline()
	f.close()
	del f
		
		
field_header = ['tractID', 'avg_crude', 'avg_baye', 'dev_baye', 'max_baye', 'min_baye', 'avg_b2p5', 'dev_b2p5', 'max_b2p5', 'min_b2p5', 'avg_b97p5', 'dev_b97p5', 'max_b97p5', 'min_b97p5', 'avg_sb', 'dev_sb', 'max_sb', 'min_sb', 'avg_sb2p5', 'dev_sb2p5', 'max_sb2p5', 'min_sb2p5', 'avg_sb97p5', 'dev_sb97p5', 'max_97p5', 'min_97p5']	
result = []
for each_tract in test_summary:
	row = [each_tract]
	crude = test_summary[each_tract][field_name[0]]
	row.append(float(sum(crude))/ len(crude))
	
	l = test_summary[each_tract][field_name[1]] #baye
	l.sort()
	row.append(float(sum(l))/ len(l))
	row.append(numpy.std(l))
	row.append(l[0])
	row.append(l[-1])
	
	l = test_summary[each_tract][field_name[2]] #baye2p5
	l.sort()
	row.append(float(sum(l))/ len(l))
	row.append(numpy.std(l))
	row.append(l[0])
	row.append(l[-1])
	
	l = test_summary[each_tract][field_name[3]] #baye97p5
	l.sort()
	row.append(float(sum(l))/ len(l))
	row.append(numpy.std(l))
	row.append(l[0])
	row.append(l[-1])
	
	l = test_summary[each_tract][field_name[4]] #SpBaye
	l.sort()
	row.append(float(sum(l))/ len(l))
	row.append(numpy.std(l))
	row.append(l[0])
	row.append(l[-1])
	
	l = test_summary[each_tract][field_name[5]] #SpBaye2p5
	l.sort()
	row.append(float(sum(l))/ len(l))
	row.append(numpy.std(l))
	row.append(l[0])
	row.append(l[-1])
	
	l = test_summary[each_tract][field_name[6]] #SpBaye97p5
	l.sort()
	row.append(float(sum(l))/ len(l))
	row.append(numpy.std(l))
	row.append(l[0])
	row.append(l[-1])
	
	result.append(row)
	
f = open(output_file, 'w')
f.writelines(str(field_header).replace('[', '').replace(']','').replace('\'',''))
f.write('\n')
for each_row in result:
	f.writelines(str(each_row).replace('[', '').replace(']','').replace('\'',''))
	f.write('\n')
f.close()



