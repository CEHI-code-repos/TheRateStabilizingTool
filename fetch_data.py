### Fetch Data from Census
import urllib2, arcpy
from operator import itemgetter
import time


# Callback function for next function
def getkey(item):
    key = -2
    return item[key]

# Load apikey for Census Bureau API
def get_api_key():
    apikey = "b36c90fb31312a6f1a9c6e25b3b05ca8644077fc"
    return apikey


### Basic Function built-up
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
        raise ValueError(string + "\nis not a list string")
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

# Sum population of a selected field
def sum_pop_census(data, field):
    count = 0
    fname = data[0]
    f_index = fname.index(field)
    i = 1
    while i < len(data):
        #print str(i) + ":" + data[i][f_index]
        count += int(data[i][f_index])
        i += 1
    return count
    
# format list of field to a string
def construct_field_string(field_list):
    strings = ""
    for field in field_list:
        strings += field + ","
    strings += "NAME"
    return strings
    
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
    
# Select certain column from dataframe
def col_select(datalist, nvector):
    i = 0 
    while i < len(nvector):
        if(nvector[i] < 0):
            nvector[i] += len(datalist[0])
        i += 1
    select = [n for n in nvector]
    result = []
    for row in datalist:
        result.append(list(itemgetter(*select)(row)))
    return result    

# Merge Columns from two dataset with same number of rows
def c_merge (df1, df2):
    if (len(df1) != len(df2)):
        raise ValueError("Two data frames don't have the same number of row")
    i = 0
    result = []
    while i < len(df1):
        result.append(df1[i]+ df2[i])
        i += 1
    return result
    
# Add two numeric matrix 
def df_addition(df1, df2, header = True, ntype = "int"):
    if (len(df1) != len(df2)):
        raise ValueError("Two data frames don't have the same number of Row")
    elif (len(df1[0]) != len(df2[0])):
        raise ValueError("Two data frames don't have the same number of Column")
    i = 0
    result = []
    if header:
        i += 1
        result = [df1[0]]
    while i < len(df1):
        j = 0
        temprow = []
        while j < len(df1[0]):
            if(ntype == "int"):
                temprow.append(int(df1[i][j]) + int(df2[i][j]))
            else:
                temprow.append(float(df1[i][j]) + float(df2[i][j]))
            j += 1
        result.append(temprow)
        i += 1
    return result
    
# Divide numeric matrix by a number
def df_divide(df1, num, header = True):
    i = 0
    result = []
    if header:
        i += 1
        result = [df1[0]]
    while i < len(df1):
        j = 0
        temprow = []
        while j < len(df1[0]):
            temprow.append(float(df1[i][j]) / float(num))
            j += 1
        result.append(temprow)
        i += 1
    return result
    

    
# Merge certain elements in array
def merge_array_elements (array, index_vector):
    result = ""
    for i in index_vector:
        result += array[i]
    return result
    
# Fetch and Construct table from returns
def fetch_construct(request):
    restart = False
    first = True
    while (first or restart):
        try:
            first = False
            response = urllib2.urlopen(request)
            if restart == True:
                arcpy.AddWarning("Retry Successful!")
                restart = False
        except urllib2.HTTPError as e:
            #arcpy.AddMessage(request)
            arcpy.AddWarning(e)
            arcpy.AddWarning("Restarting Download in 5 seconds...")
            restart = True
            time.sleep(5)

    unformData = response.read().decode('utf-8')
    [censusdata, resid] = construct_list(unformData, list())
    if resid != "":
        raise ValueError("Error occurs when formatting data! Format error")
    result = [censusdata[0]]
    result.extend(sorted(censusdata[1:],key=getkey))
    return result
    
# We need to fetch data for multiple times because of the maximum of  50 field
# Each fetch will generate the same set of annotation field (name, geoid)
# This function is used to index repeated fields
def index_repeated_name (header):
    temp = dict()
    result = dict()
    vect = header
    count = 0
    while vect != []:
        [field, vect] = push_element(vect)
        if field not in temp:
            temp[field] = [1, [count]]
        else: 
            temp[field][0] += 1
            temp[field][1].append(count)
        count += 1
    for item in temp:
        if(temp[item][0] > 1):
            result.update({item:temp[item]})
    return result

# Create repeated array from repeated fields index
def create_repeated_array(r_dict, keep_index):
    result = []
    for item in r_dict:
        result.extend(col_erase([r_dict[item][1]],keep_index)[0])
    return result

# Construct population table (couple of requests since field request should be less than 50)
def construct_pop_table (base_year, base_string, field, geolevel, criteria, key = -2):    
    # Split 120 fields to 4 requests
    fields_f1 = construct_field_string(field[0:30])
    fields_f2 = construct_field_string(field[30:60])
    fields_f3 = construct_field_string(field[60:90])
    fields_f4 = construct_field_string(field[90:120])
    
    apikey = get_api_key()

    # Construct request string
    request1 = base_string.format(base_year, apikey, fields_f1, geolevel, criteria)
    request2 = base_string.format(base_year, apikey, fields_f2, geolevel, criteria)
    request3 = base_string.format(base_year, apikey, fields_f3, geolevel, criteria)
    request4 = base_string.format(base_year, apikey, fields_f4, geolevel, criteria)


    # Fetch data & Construct base population table
    df1 = fetch_construct(request1)
    df2 = fetch_construct(request2)
    df3 = fetch_construct(request3)
    df4 = fetch_construct(request4)

    # Merge 4 data request
    df = c_merge(df1,df2)
    df = c_merge(df,df3)
    df = c_merge(df,df4)
    
    # Remove repeated columns because of multiple request
    header = df[0]
    repeated_name =  sorted(create_repeated_array(index_repeated_name(header),[-1]))
    #repeated_name = [30,31,62,63,94,95]
    pop_table = col_erase(df, repeated_name)
    return pop_table
    
# Fetch the age from standard population. Calculate standard population structure
def construct_age(ageV, noteV, age_structure):    
    i = 0
    temp = 0
    structed_age = []
    actstruct = []
    first_record = True # to skip header
    while ageV != []: # push the element out when age vector is not empty
        [cnt, ageV] = push_element(ageV)
        [exp, noteV] = push_element(noteV)
        if(i == len(age_structure) or i == len(age_structure) - 1): # deal with the outflow issue when on the last age structure 
            if(age_structure[i] < 0):
                break
            temp += int(cnt)
        elif (exp >= age_structure[i]): 
            if first_record:
                actstruct.append(exp)
                first_record = False
            if exp < abs(age_structure[i+1]):
                temp += int(cnt)
            else:
                if(age_structure[i+1] > 0):
                    actstruct.append(exp)
                    structed_age.append(temp)
                    i += 1
                    temp = int(cnt)
    if(age_structure[i] > 0): # to get rid of the impact of cap age (using negative number)
        structed_age.append(temp)
    return [structed_age, actstruct]
    
def clean_note_col(r_note_col):
    i = 0
    while i < len(r_note_col):
        row = r_note_col[i]
        j = 0
        while j < len(row):
            row[j] = row[j].replace(',',';')
            j += 1
        i += 1
    return r_note_col
    
def download_age_from_api (base_year, r_crit_level, r_crit, r_year, r_geolevel):
    arcpy.AddMessage("Setting up connections to Census Bureau Server...")

    # Map fields (convert field name to meaningful number)
    age_exp = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,105,110]

    # Population is by age & sex, so fetch both male and female
    sf2010_f = ["PCT0120107","PCT0120108","PCT0120109","PCT0120110","PCT0120111","PCT0120112","PCT0120113","PCT0120114","PCT0120115","PCT0120116","PCT0120117","PCT0120118","PCT0120119","PCT0120120","PCT0120121","PCT0120122","PCT0120123","PCT0120124","PCT0120125","PCT0120126","PCT0120127","PCT0120128","PCT0120129","PCT0120130","PCT0120131","PCT0120132","PCT0120133","PCT0120134","PCT0120135","PCT0120136","PCT0120137","PCT0120138","PCT0120139","PCT0120140","PCT0120141","PCT0120142","PCT0120143","PCT0120144","PCT0120145","PCT0120146","PCT0120147","PCT0120148","PCT0120149","PCT0120150","PCT0120151","PCT0120152","PCT0120153","PCT0120154","PCT0120155","PCT0120156","PCT0120157","PCT0120158","PCT0120159","PCT0120160","PCT0120161","PCT0120162","PCT0120163","PCT0120164","PCT0120165","PCT0120166","PCT0120167","PCT0120168","PCT0120169","PCT0120170","PCT0120171","PCT0120172","PCT0120173","PCT0120174","PCT0120175","PCT0120176","PCT0120177","PCT0120178","PCT0120179","PCT0120180","PCT0120181","PCT0120182","PCT0120183","PCT0120184","PCT0120185","PCT0120186","PCT0120187","PCT0120188","PCT0120189","PCT0120190","PCT0120191","PCT0120192","PCT0120193","PCT0120194","PCT0120195","PCT0120196","PCT0120197","PCT0120198","PCT0120199","PCT0120200","PCT0120201","PCT0120202","PCT0120203","PCT0120204","PCT0120205","PCT0120206","PCT0120207","PCT0120208","PCT0120209"]
    sf2010_m = ["PCT0120003","PCT0120004","PCT0120005","PCT0120006","PCT0120007","PCT0120008","PCT0120009","PCT0120010","PCT0120011","PCT0120012","PCT0120013","PCT0120014","PCT0120015","PCT0120016","PCT0120017","PCT0120018","PCT0120019","PCT0120020","PCT0120021","PCT0120022","PCT0120023","PCT0120024","PCT0120025","PCT0120026","PCT0120027","PCT0120028","PCT0120029","PCT0120030","PCT0120031","PCT0120032","PCT0120033","PCT0120034","PCT0120035","PCT0120036","PCT0120037","PCT0120038","PCT0120039","PCT0120040","PCT0120041","PCT0120042","PCT0120043","PCT0120044","PCT0120045","PCT0120046","PCT0120047","PCT0120048","PCT0120049","PCT0120050","PCT0120051","PCT0120052","PCT0120053","PCT0120054","PCT0120055","PCT0120056","PCT0120057","PCT0120058","PCT0120059","PCT0120060","PCT0120061","PCT0120062","PCT0120063","PCT0120064","PCT0120065","PCT0120066","PCT0120067","PCT0120068","PCT0120069","PCT0120070","PCT0120071","PCT0120072","PCT0120073","PCT0120074","PCT0120075","PCT0120076","PCT0120077","PCT0120078","PCT0120079","PCT0120080","PCT0120081","PCT0120082","PCT0120083","PCT0120084","PCT0120085","PCT0120086","PCT0120087","PCT0120088","PCT0120089","PCT0120090","PCT0120091","PCT0120092","PCT0120093","PCT0120094","PCT0120095","PCT0120096","PCT0120097","PCT0120098","PCT0120099","PCT0120100","PCT0120101","PCT0120102","PCT0120103","PCT0120104","PCT0120105"]

    sf2000_f = ["PCT012107","PCT012108","PCT012109","PCT012110","PCT012111","PCT012112","PCT012113","PCT012114","PCT012115","PCT012116","PCT012117","PCT012118","PCT012119","PCT012120","PCT012121","PCT012122","PCT012123","PCT012124","PCT012125","PCT012126","PCT012127","PCT012128","PCT012129","PCT012130","PCT012131","PCT012132","PCT012133","PCT012134","PCT012135","PCT012136","PCT012137","PCT012138","PCT012139","PCT012140","PCT012141","PCT012142","PCT012143","PCT012144","PCT012145","PCT012146","PCT012147","PCT012148","PCT012149","PCT012150","PCT012151","PCT012152","PCT012153","PCT012154","PCT012155","PCT012156","PCT012157","PCT012158","PCT012159","PCT012160","PCT012161","PCT012162","PCT012163","PCT012164","PCT012165","PCT012166","PCT012167","PCT012168","PCT012169","PCT012170","PCT012171","PCT012172","PCT012173","PCT012174","PCT012175","PCT012176","PCT012177","PCT012178","PCT012179","PCT012180","PCT012181","PCT012182","PCT012183","PCT012184","PCT012185","PCT012186","PCT012187","PCT012188","PCT012189","PCT012190","PCT012191","PCT012192","PCT012193","PCT012194","PCT012195","PCT012196","PCT012197","PCT012198","PCT012199","PCT012200","PCT012201","PCT012202","PCT012203","PCT012204","PCT012205","PCT012206","PCT012207","PCT012208","PCT012209"]
    sf2000_m = ["PCT012003","PCT012004","PCT012005","PCT012006","PCT012007","PCT012008","PCT012009","PCT012010","PCT012011","PCT012012","PCT012013","PCT012014","PCT012015","PCT012016","PCT012017","PCT012018","PCT012019","PCT012020","PCT012021","PCT012022","PCT012023","PCT012024","PCT012025","PCT012026","PCT012027","PCT012028","PCT012029","PCT012030","PCT012031","PCT012032","PCT012033","PCT012034","PCT012035","PCT012036","PCT012037","PCT012038","PCT012039","PCT012040","PCT012041","PCT012042","PCT012043","PCT012044","PCT012045","PCT012046","PCT012047","PCT012048","PCT012049","PCT012050","PCT012051","PCT012052","PCT012053","PCT012054","PCT012055","PCT012056","PCT012057","PCT012058","PCT012059","PCT012060","PCT012061","PCT012062","PCT012063","PCT012064","PCT012065","PCT012066","PCT012067","PCT012068","PCT012069","PCT012070","PCT012071","PCT012072","PCT012073","PCT012074","PCT012075","PCT012076","PCT012077","PCT012078","PCT012079","PCT012080","PCT012081","PCT012082","PCT012083","PCT012084","PCT012085","PCT012086","PCT012087","PCT012088","PCT012089","PCT012090","PCT012091","PCT012092","PCT012093","PCT012094","PCT012095","PCT012096","PCT012097","PCT012098","PCT012099","PCT012100","PCT012101","PCT012102","PCT012103","PCT012104","PCT012105"]

    
    ## Get Standard structure
    if base_year == "2010":  # 2010 Oct update on Census 2010 changed the base string structure
        base_string = "https://api.census.gov/data/{0}/dec/sf1?key={1}&get={2}&for={3}:*{4}"
    elif base_year == "2000":
        base_string = "https://api.census.gov/data/{0}/sf1?key={1}&get={2}&for={3}:*{4}"

    # Population by age is in field PCT0120003 to PCT0120209 for 2010, PCT012003 to PCT012209 for 2000
    #geolevel = "tract"
    #criteria = "&in=state:48%20county:001"  # Sample call structure for tract level 
    geolevel = "state"
    criteria = ""

    if base_year == "2010": # Census changed it back to the same variable name in Oct.2018. Keep the old one in case it changed back.
        field_m = sf2000_m
        field_f = sf2000_f
    elif base_year == "2000":
        field_m = sf2000_m
        field_f = sf2000_f

    arcpy.AddMessage("Retrieving information for standard population...")    
    pop_table_m = construct_pop_table (base_year, base_string, field_m, geolevel, criteria)
    pop_table_f = construct_pop_table (base_year, base_string, field_f, geolevel, criteria)
    note = col_select(pop_table_m, [-1,-2])

    num_m = col_erase(pop_table_m, [-1,-2])
    num_f = col_erase(pop_table_f, [-1,-2])
    num_table = df_addition(num_m, num_f)

    # Fetching standard age structure data
    header = pop_table_m[0]
    age_vector = []
    i = 0
    while i < len(header) and header[i] != "NAME":
        age_vector.append(sum_pop_census(num_table, header[i]))
        i += 1

    arcpy.AddMessage("Retrieving information for " + r_geolevel + " level population...")    
    # Fetch data for rate calculation
    r_criteria = "&in=" + r_crit_level + ":" + r_crit

    if r_year == "2010": # Census changed it back to the same variable name in Oct.2018. Keep the old one in case it changed back.
        field_m = sf2000_m
        field_f = sf2000_f
    elif r_year == "2000":
        field_m = sf2000_m
        field_f = sf2000_f
    
    if r_geolevel == "county":
        key_level = -3
    elif r_geolevel == "tract":
        key_level = -4
    elif r_geolevel == "state":
        key_level = -2
    else:
        raise ValueError("Unsupported Geographic level!!")
    
    key_col = []
    i = -1
    while i >= key_level:
        key_col.append(i)
        i -= 1
   
    if r_year == "2010" and r_geolevel == "tract":  # 2010 Oct Census update can't get all counties, has to loop through
        arcpy.AddMessage("Fetching county code...")
        cnty_code_request = base_string.format(r_year, get_api_key(), "NAME", "county", r_criteria)
        cnty_code_df = fetch_construct(cnty_code_request)
        cnty_codes = []
        for each_row in cnty_code_df[1:]:
            cnty_codes.append(each_row[-1])
        
        
        from copy import deepcopy
        pop_table_m = ""
        pop_table_f = ""
        for each_cnty_code in cnty_codes:
            r_criteria_cnty = r_criteria + "%20county:" + each_cnty_code
            
            arcpy.AddMessage("Fetching Male data for county "+each_cnty_code+"...")
            pop_table_m_temp = construct_pop_table (r_year, base_string, field_m, r_geolevel, r_criteria_cnty, key_level)
            if pop_table_m == "":
                pop_table_m = deepcopy(pop_table_m_temp)
            else:
                pop_table_m.extend(deepcopy(pop_table_m_temp[1:]))
            
            arcpy.AddMessage("Fetching Female data for county "+each_cnty_code+"...")
            pop_table_f_temp = construct_pop_table (r_year, base_string, field_f, r_geolevel, r_criteria_cnty, key_level)
            if pop_table_f == "":
                pop_table_f = deepcopy(pop_table_m_temp)
            else:
                pop_table_f.extend(deepcopy(pop_table_m_temp[1:]))
   
    else:    
        arcpy.AddMessage("Fetching Male data...")
        pop_table_m = construct_pop_table (r_year, base_string, field_m, r_geolevel, r_criteria, key_level)
        arcpy.AddMessage("Fetching Female data...")
        pop_table_f = construct_pop_table (r_year, base_string, field_f, r_geolevel, r_criteria, key_level)

    r_num_m = col_erase(pop_table_m, key_col)
    r_num_f = col_erase(pop_table_f, key_col)
    r_note_col = col_erase(pop_table_m, sequence(0, len(pop_table_m[0])+ key_level))
    r_note_col = clean_note_col(r_note_col)
    r_num_table = df_addition(r_num_m, r_num_f)
    return [age_vector, age_exp, r_num_table, r_num_m, r_num_f, r_note_col]
    
def summarize_to_age_structure (age_vector, age_exp, r_num_table, r_note_col, age_structure):
    arcpy.AddMessage("Constructing standard population structure...")    
    [structed_age, act_struct] = construct_age(age_vector, age_exp, age_structure)

    # Getting Percentage of standard age structure
    total = sum(structed_age)
    percent = df_divide([structed_age],total, header = False)
    
    arcpy.AddMessage("Calculating population by input age structure...")
    requested_age_pop = []
    header = True
    for row in r_num_table:
        if not header:
            [row_age, r_struct] = construct_age(row, age_exp, age_structure)
            requested_age_pop.append(row_age)
        else:
            header = False
    
    r_age_pop_table = [age_structure]
    r_age_pop_table.extend(requested_age_pop)
    result = c_merge(r_age_pop_table, r_note_col)
    return [result, percent]
    
    
### Function to be call by the main core. It is the wrapped function for this module
def fetch_data(base_year, r_crit_level, r_crit, r_year, r_geolevel, age_structure):
    [age_vector, age_exp, r_num_table, r_note_col] = download_age_from_api(base_year, r_crit_level, r_crit, r_year, r_geolevel)
    i = 0
    ncol = len(r_note_col[0])
    while i < len(r_note_col):
        if i == 0:
            r_note_col[i].append("GEOID")
        else:
            indexV = col_erase([sequence(0,ncol)],[0])[0]
            r_note_col[i].append(merge_array_elements(r_note_col[i], indexV))    
        i += 1
        
    [result, percent]=summarize_to_age_structure (age_vector, age_exp, r_num_table, r_note_col, age_structure)
    return [r_note_col, result, percent]

