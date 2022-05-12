def reverse_year_in_date(date_string:str):
    """From a date (str) format puts the 
    year in the day position. 
    e.g.: 31012021 
    to e.g.: 20220130"""
    return date_string[4:8] + date_string[2:4] + date_string[:2]


def modify_year_in_date(date_string):

    """Modifiy the string in format dd.mm.yy e.g. 00.01.2021
    to yyyy.mm.dd e.g. 20210100"""
    
    date_string = date_string[:5] + "20" + date_string[6:]
    date_string = date_string.replace(".", "")
    
    return date_string 