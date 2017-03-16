import time, datetime
def log_error(method,err): 
#trace the error and write it to a txt
    timestamp = datetime.datetime.now()
    record = str(timestamp) + ','  + method + ',' + str(err) +  '\n'
    record += '\n'
    with open('error.txt','a') as infile:
    	infile.write(record)

