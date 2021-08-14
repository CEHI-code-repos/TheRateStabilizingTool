import os, arcpy, numpy, numbers, ast, bisect
import datetime as dt
from operator import itemgetter
import data_filter as df # This module filtered the result based on input
df = reload(df) # Make sure newest module is loaded
import update_schema as us # This module cleans schema file to make sure same name file exists only 1 time in schema
us = reload(us) # Make sure newest module is loaded

### Basic Function built-up
# Check if a key exist in a dictionary
def if_key_exist (key, dictionary):
    try:
        dictionary[key]
        return True
    except KeyError:
        return False
    
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
            elif string[i] == "," or string[i] == "]" or string[i] == '\n':
                return [string[0:i], string[i:]]
            i += 1
    if(i < len(string)):
        return [string[0+i], string[i+1:]]
    else:
        return [string, '']
    
def index_field(string, field_name):
    i = 0
    [current, string] = push_word(string)
    while current != "":
        if (current == field_name):
            return i
        [current, string] = push_word(string[1:])
        i += 1
    return NameError('No Field Found')  

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
            return -1
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
    if isinstance(v2, numbers.Number):
        i = 0
        while i < len(v1):
            result.append(float(v1[i])/v2)
            i += 1
        return result
    elif (len(v1) != len(v2)):
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
            result += "\'" + elem + "\',"
        else:
            result += str(elem) + ","
    result = result[0:len(result)-1]#.replace(" ", "")
    return result
    
# Sample Gamma function
def gamma_sample (shape, scale, nSample, geoid):
    numpy.random.seed(20151201)
    if shape == 0:
        g_sample1000 = sequence(0, nSample, 0)
        arcpy.AddWarning("Some age group in " + geoid + " don't have any incident!!!")
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
def get_a0_n0 (result, ncol, death_count, percentile, a00=[], n00=[], minimum_n0 = 5, debug=False):  # Set a00 n00 0 for global a0 and n0 calculation
    Y_prior = 6.0
    pop_mat = col_erase(result, sequence(-1, ncol, -1))
    case_mat = col_erase(death_count, sequence(-1, ncol, -1))
    #n_tot = df_sum(pop_mat)
    #c_tot = df_sum(case_mat)
    n_tot = col_sum(pop_mat)
    if n_tot == 0:
        return([a00, n00])
    
    c_tot = col_sum(case_mat)
    lam = vector_divide(c_tot, n_tot)
    
    if debug:
        arcpy.AddWarning(c_tot)
        arcpy.AddWarning(n_tot)
        arcpy.AddWarning("!--------!") 
    
    if n00 == []: # if n00 = 0 we are calculating n00 
        pi_lam = vector_multi(percentile, lam)
        lam0d = sum(pi_lam)
        pct_age_spec = vector_divide(pi_lam, lam0d)
        a0adj = vector_multi(pct_age_spec, Y_prior)
        n0 = vector_divide(a0adj, lam)
        if debug:
            arcpy.AddWarning(lam)
        return [a0adj, n0]
            
    else:
        lamadj = []
        a0adj_00 = []
        i = 0
        while i < len(n_tot):
            each_n = n_tot[i]
            if each_n == 0:
                #arcpy.AddMessage('!!!')
                #arcpy.AddMessage(float(a00[i])/n00[i])
                lamadj.append(float(a00[i])/n00[i])
            else:
                omega = min(float(each_n)/n00[i], 0.99)
                if debug:
                    arcpy.AddWarning("000000")
                    arcpy.AddWarning(omega)
                    arcpy.AddWarning("000000")
                lamadj.append(omega*c_tot[i]/each_n + (1-omega)*a00[i]/n00[i])
            i += 1
            
        pi_lamadj = vector_multi(percentile, lamadj)
        lamadj0d = sum(pi_lamadj)
        pct_age_spec_adj = vector_divide(pi_lamadj, lamadj0d)
        a0adj_00 = vector_multi(pct_age_spec_adj, Y_prior)

        n0 = vector_divide(a0adj_00, lamadj)
            
        if debug:
            arcpy.AddWarning("#####")
            arcpy.AddWarning(lamadj)
            arcpy.AddWarning(n0)
            arcpy.AddWarning("#####")
        
        return [a0adj_00, n0]
    
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
    
def check_a0_okay(a0):
    for a0k in a0:
        if a0k < 0.000001: # Can't use equals to 0 when comparing float points
            return False
    return True
    
def check_age_group_case_count(death_count, dataCol_cnt):
    result = death_count[0][0:dataCol_cnt]
    i = 1
    while i < len(death_count):
        result = vector_plus(result, death_count[i][0:dataCol_cnt])
        #print result
        if not 0.0 in result:
            return True
        i += 1
    return False
    

### Function to be call by the main core. It is the wrapped function for this module
def construct_deathdata (r_note_col, result, percent, inputdata, outputfolder, id_field, age_field, nyear, state_shp="", GeoID="", ngbh_dict_loc=""):
    nyear = float(nyear)

    input_ext =  os.path.splitext(os.path.split(inputdata)[1])[1]
    if input_ext == '.csv':
        temp_f = open(inputdata, 'r')
        header_string = temp_f.readline().replace('\n', '')
        temp_f.close()
        
        id_id = index_field(header_string, id_field)
        
        f = open(os.path.split(inputdata)[0] + '\\schema.ini', 'a')
        f.write('['+ os.path.split(inputdata)[1] +']\n')
        f.write('Col{0}={1} Text Width 30\n'.format(id_id+1, id_field))
        f.close()
        

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
    total_death = 0
    for row in cursor:
        temp_ID = str(row.getValue(id_field))
        temp_age_check = row.getValue(age_field)
        
        try: 
             temp_age = float(temp_age_check)
        except ValueError:
            arcpy.AddWarning('Age input for ID ' + temp_ID + ' is \''+ str(temp_age_check) + '\'!! Clean data or Program will consider this age as 0!!!')
            temp_age = 0
            
        if(not if_key_exist(temp_ID, death_count_dict)):
            errorID.append(temp_ID)
        else:
            idx = index_age(temp_age, header_zero)
            if(idx != -1):
                death_count_dict[temp_ID][idx] += 1
                
    if not check_age_group_case_count(death_count, len(death_count[0])-len(r_note_col[0])):
        arcpy.AddWarning(death_count)
        arcpy.AddError("Some age group don't have any case in it!!! Please summarize your data based on the age and then redesign your age group.")
        
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
    ratesum = row_sum(rate)
        

    unsmooth_pctl_ns = [['ns_percentile']]

    ###
    ### For non-spatial Bayesian 
    ###
    ncol = len(r_note_col[0])
    [a0, n0] = get_a0_n0 (result[1:], ncol, death_count, percent[0])

    i = 0
    aar_bayesian = []
    field_name = ["Baye_AAR", "Baye_2p5", "Baye_97p5"]
    aar_bayesian.append(field_name)
    while i < len(death_count):
        Y = death_count[i][0:num_count]
        n = result[i+1][0:num_count]
        Geokey = r_note_col[i][-1]
        # Make sure n is always equal or larger than Y
        k = 0
        while k < len(n):
            n[k]=max(Y[k],n[k])
            k += 1

        j = 0
        age_group = []
        while j < num_count:
            g_samps_per = vector_multi(gamma_sample(Y[j] + a0[j], 1.0/(n[j] + n0[j]), 5000, Geokey), percent[0][j])
            age_group.append(g_samps_per)
            j += 1
        aar_bayesian.append(sample_percentile(col_sum(age_group), [0.5, 0.025, 0.975]))
        unsmooth_pctl_ns.append([bisect.bisect(col_sum(age_group), ratesum[i][0]/100000)/50.0])
        i += 1

    aar_bayesian = col_divide(aar_bayesian,0,nyear, True)
    aar_bayesian = col_divide(aar_bayesian,1,nyear, True)
    aar_bayesian = col_divide(aar_bayesian,2,nyear, True)
    ### Bayesian ends here


    if state_shp != "" or ngbh_dict_loc != "":
        arcpy.AddMessage("Spatial smoothing the results...")
        
        
        unsmooth_pctl_sp = [['sp_percentile']]
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

            #arcpy.AddMessage(Geokey)  ###For debug ----
            # if Geokey == '37019020304':
                # [a0i, n0i] = get_a0_n0 (temp_result[1:], ncol, temp_death[1:], percent[0], a0, n0, 5, True)
                # arcpy.AddWarning(a0)
                # arcpy.AddWarning(n0)
                # arcpy.AddWarning("========")
            # else:
                # [a0i, n0i] = get_a0_n0 (temp_result[1:], ncol, temp_death[1:], percent[0], a0, n0)
            [a0i, n0i] = get_a0_n0 (temp_result[1:], ncol, temp_death[1:], percent[0], a0, n0)
                    
            Y = death_count[i][0:num_count]
            n = result[i+1][0:num_count]
            
            # Make sure n is always equal or larger than Y
            k = 0
            while k < len(n):
                n[k]=max(Y[k],n[k])
                k += 1

            j = 0
            sp_age_group = []
            while j < num_count:
                if n[j] + n0i[j] == 0:
                    arcpy.AddError(n)
                    arcpy.AddError(n0i)
                sp_g_samps_per = vector_multi(gamma_sample(Y[j] + a0i[j], 1.0/(n[j] + n0i[j]), 5000, Geokey), percent[0][j])
                # if Geokey == '37019020304':  ###For debug
                    # arcpy.AddWarning(Y[j] + a0i[j])
                    # arcpy.AddWarning(n[j] + n0i[j])
                    # arcpy.AddWarning(sample_percentile(gamma_sample(Y[j] + a0i[j], 1.0/(n[j] + n0i[j]), 5000, Geokey), [0.5, 0.025, 0.975]))
                    # arcpy.AddWarning(percent[0][j])
                    # arcpy.AddWarning("-------")
                
                sp_age_group.append(sp_g_samps_per)
                j += 1
            sp_aar_bayesian.append(sample_percentile(col_sum(sp_age_group), [0.5, 0.025, 0.975]))
            unsmooth_pctl_sp.append([bisect.bisect(col_sum(sp_age_group), ratesum[i][0]/100000)/50.0])
            i += 1
        
            # if Geokey == '37019020304': ###For debug
                # arcpy.AddWarning(Y)
                # arcpy.AddWarning(n)
                # arcpy.AddWarning(a0i)
                # arcpy.AddWarning(n0i)
                # arcpy.AddWarning(percent)
                # arcpy.AddWarning(sp_aar_bayesian[-1])
                # arcpy.AddWarning(sample_percentile(col_sum(sp_age_group), [0.5, 0.025, 0.975]))
        
        sp_aar_bayesian = col_divide(sp_aar_bayesian,0,nyear, True)
        sp_aar_bayesian = col_divide(sp_aar_bayesian,1,nyear, True)
        sp_aar_bayesian = col_divide(sp_aar_bayesian,2,nyear, True)
        age_adj_rate = c_merge(age_adj_rate, sp_aar_bayesian)
        

    ###
    ### For non-spatial Bayesian
    ###
    age_adj_rate = c_merge(age_adj_rate, aar_bayesian)

    avg_rate = sum(vector_multi(vector_divide(a0, n0), percent[0]))/nyear * 100000

    pop_seq = col_erase(result[1:], sequence(-1, ncol, -1))
    pop_sum = row_sum(pop_seq)
    #arcpy.AddMessage(len(pop_sum))
    #arcpy.AddMessage(len(aar_bayesian))
    i = 1
    while i < len(aar_bayesian):
        row = pop_sum[i-1]
        if float(aar_bayesian[i][0]) < float(aar_bayesian[i][2])-float(aar_bayesian[i][1]):
            if state_shp != "" or ngbh_dict_loc != "":
                if float(sp_aar_bayesian[i][0]) < float(sp_aar_bayesian[i][2])-float(sp_aar_bayesian[i][1]):
                    row.append("Alert:Unreliable Estimate!!!!")
                    row.append(1)
                    row.append(1)
                else:
                    row.append("Alert:Unreliable non-Spatial Bayesian Estimate!!!!")
                    row.append(1)
                    row.append(0)
            else:
                row.append("Alert:Unreliable non-Spatial Bayesian Estimate!!!!")
                row.append(1)
        elif state_shp != "" or ngbh_dict_loc != "":
            if float(sp_aar_bayesian[i][0]) < float(sp_aar_bayesian[i][2])-float(sp_aar_bayesian[i][1]):
                row.append("Alert:Unreliable Spatial Bayesian Estimate!!!!")
                row.append(0)
                row.append(1)
            else: 
                row.append("-")
                row.append(0)
                row.append(0)
        else:
            row.append("-")
            row.append(0)
            
        i += 1
    pop_name = [["Population", "Alert", "NSpUnreli"]]
    if state_shp != "" or ngbh_dict_loc != "":
        pop_name[0].append("SpUnreli")
    pop_name.extend(pop_sum)
    ### Bayesian ends here


    output = c_merge(age_adj_rate, r_note_col)
    output = c_merge(output, unsmooth_pctl_ns)
    if ngbh_dict_loc!="":
        output = c_merge(output, unsmooth_pctl_sp)
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

    # Clean Schema.ini to remove the entry with same table name
    cleaned_content = us.clean_exist_schema(outputfolder + "\\" + "schema.ini", ["age_adjust_"+ filename + ".csv"])
    
    # Write Schema.ini file
    f = open(outputfolder + "\\" + "schema.ini", "w")
    f.write(cleaned_content)
    f.writelines("[age_adjust_" + filename + ".csv]\n")
    f.writelines("Format=CSVDelimited\n")
    f.writelines("ColNameHeader=True\n")
    i = 1
    for col in headerline:
        #arcpy.AddMessage(col)
        if col in ["state", "county", "tract", "GEOID"]:
            f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 80\n")
        elif col in ["Alert", "NAME"]:
            f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 200\n")
        elif col in ["Population", "NSpUnreli", "SpUnreli"]:
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
        
    arcpy.AddMessage("The average rate for the area is " + str(avg_rate) + ' cases per 100,000')
    return (outputfolder + "\\" + "age_adjust_" + filename + ".csv")



