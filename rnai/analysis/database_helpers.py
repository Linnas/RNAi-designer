import subprocess
import time
import datetime
import os
import logging
import shutil
import platform
from types import *


def all_dbs(db_location):
    """Get a dictionary of all Bowtie DBs created so far by the user."""
    all_databases = os.listdir(db_location)
    database_dict = {'text': [], 'size': [], 'time': [], 'type':[]}
    avaiable_databases = filter(lambda x:x.endswith('.ebwt') or x.endswith('.bt2'), all_databases)
    for db_file in avaiable_databases:
        file_date, file_size = get_size_date_of_file(os.path.join(db_location, db_file))
        #print file_date, file_size
        if db_file.split('.')[0] not in database_dict['text']:
            database_dict['text'].append(db_file.split('.')[0])
            database_dict['time'].append(file_date)
            database_dict['size'].append(int((file_size/1000000)*3))
            database_dict['type'].append((db_file.split('.')[2]))
    return database_dict


def get_size_date_of_file(db_file):
    """Gets file size and date."""
    tm = datetime.datetime.fromtimestamp(os.path.getctime(db_file))
    file_date =  str(tm.month) + '/' + str(tm.day) + '/' + str(tm.year) + ' ' + str(tm.hour) + ':' + str(tm.minute)
    file_size = os.stat(db_file).st_size
    #print db_file, file_date, int(file_size)/1000000
    return file_date, int(file_size)


def create_bowtie_database(db_name, database_file_location, bowtie_location):
    """Creates a Bowtie DB."""

    os.chdir(bowtie_location)
    process = subprocess.Popen(["bowtie-build", database_file_location, str(db_name)])
    process.wait()

    fpath = os.path.join(bowtie_location, str(db_name) + '.rev.1.ebwt')

    if os.path.exists(fpath):
        fdate, fsize = get_size_date_of_file(fpath)
        return "Database successfully created!", True, fdate, int(fsize*3/1e6)
    else:
        logging.debug(time.strftime("%d.%m.%Y um %H:%M:%S Uhr"))
        logging.debug(str(platform.system()+platform.release()))
        logging.exception('Got exception on main handler')
        return "Error, database could not be created!", False, None, None

    
def delete_databases(db_name, db_location):
    """Deletes all selected databases."""
    bowtie_endings = [".1.ebwt", ".2.ebwt", ".3.ebwt", ".4.ebwt", ".rev.1.ebwt", ".rev.2.ebwt"]
    bowtie_was_deleted = False
    os.chdir(db_location)
    try:
        for extension in bowtie_endings:
            del_path = os.path.join(db_location, str(db_name) + extension)
            os.remove(del_path)
            if not os.path.exists(del_path):
                bowtie_was_deleted = True
            else:
                bowtie_was_deleted = False
        
    except (IOError, OSError, WindowsError):
        pass
    
    if bowtie_was_deleted:
        return "Database successfully deleted!", True
    else:
        return "Could not delete database!", False

def share_database(db_name, out_dir, bowtie_location):
    """share your database with others"""
    dest_dir = os.path.join(out_dir, db_name)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    for ext in [".1.ebwt", ".2.ebwt", ".3.ebwt", ".4.ebwt", ".rev.1.ebwt", ".rev.2.ebwt"]:
        src_file = os.path.join(bowtie_location, str(db_name) + ext)
        shutil.copy(src_file, dest_dir)

    if os.path.exists(os.path.join(dest_dir, str(db_name) + '.1.ebwt')):
        shutil.make_archive(dest_dir, 'gztar')
    shutil.rmtree(dest)
    if os.path.exists(dest_dir +'.tar.gz'):
        return True
    else:
        return False