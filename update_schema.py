import arcpy, os, json

# function to get rid of spaces in front
def remove_leading_space(l):
    if(type(l) is not str):
        arcpy.AddError("Please make sure the input line is a string!!!")
        sys.exit(0)
    i = 0
    first_char = l[i]
    while first_char == " ":
        i += 1
        if i >= len(l):
            return("")
        first_char = l[i]
    result = l[i:]
    return(l[i:])

# function to determin whether a file exist in schema.ini
def clean_exist_schema(schema_loc, list_csv):
    if type(list_csv) is not list:
        arcpy.AddError("Please make sure the csv file name(s) is in a list!!!")
        sys.exit(0)
    if not os.path.exists(schema_loc):
        return("")
        
    result = ""
    existing = False
    f = open(schema_loc, "r")
    row = f.readline()
    while row:
        clean_row = remove_leading_space(row)
        is_title_row = (clean_row[0] == '[')
        if is_title_row:
            title = clean_row.replace("[", "").replace("]","").replace("\n","").replace("\r","")
            in_list = title in list_csv
            if not in_list:
                existing = False
            else:
                existing = True
        
        if not existing:
            result += clean_row   
            
        row = f.readline()
    
    f.close()
    return(result)