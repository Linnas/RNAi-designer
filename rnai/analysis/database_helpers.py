import subprocess
import time
import os
import logging
import platform
from types import *


def all_dbs(db_location):
    """Get a dictionary of all Bowtie DBs created so far by the user."""
    all_databases = os.listdir(db_location)
    database_dict = {'Database name': [], 'Database size (MB)': [], 'Created': []}
    for db_file in all_databases:
        file_date, file_size = get_size_date_of_file(db_location + db_file)
        #print file_date, file_size
        if db_file.endswith('.ebwt'):
            if db_file.split('.')[0] not in database_dict['Database name']:
                database_dict['Database name'].append(db_file.split('.')[0])
                database_dict['Created'].append(file_date)
                database_dict['Database size (MB)'].append((file_size/1000000)*3)

    return database_dict


def get_size_date_of_file(db_file):
    """Gets file size and date."""
    file_date = time.ctime(os.path.getctime(db_file))
    file_date = file_date.split(' ')[2] + '.' + file_date.split(' ')[1] + '.' + file_date.split(' ')[4]
    file_size = os.stat(db_file).st_size
    final_size = 0
    #print db_file, file_date, int(file_size)/1000000
    return file_date, int(file_size)


def create_bowtie_database(db_name, database_file_location, bowtie_location):
    """Creates a Bowtie DB."""

    os.chdir(bowtie_location)
    print(os.getcwd())
    process = subprocess.Popen(["bowtie-build-s", database_file_location, str(db_name)])
    process.wait()

    if os.path.exists(bowtie_location + str(db_name) + ".rev.1.ebwt"):
        return "Database successfully created!", True
    else:
        logging.debug(time.strftime("%d.%m.%Y um %H:%M:%S Uhr"))
        logging.debug(str(platform.system()+platform.release()))
        logging.exception('Got exception on main handler')
        return "Error, database could not be created!", False

    
def delete_databases(db_list, db_location):
    """Deletes all selected databases."""
    bowtie_endings = [".1.ebwt", ".2.ebwt", ".3.ebwt", ".4.ebwt", ".rev.1.ebwt", ".rev.2.ebwt"]
    bowtie_was_deleted = False
    os.chdir(db_location)
    for db in db_list:
        try:
            for extension in bowtie_endings:
                os.remove(db_location + str(db) + extension)
                if not os.path.exists(db_location + str(db) + extension):
                    bowtie_was_deleted = True
                else:
                    bowtie_was_deleted = False
            
        except (IOError, OSError, WindowsError):
            pass
    
    if bowtie_was_deleted:
        return "Database successfully deleted!", True
    else:
        return "Could not delete database!", False
