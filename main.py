import getopt
import sys
import os
import shutil
import time
import logging

# Constants
DEFAULT_INTERVAL = 10

def setup_logging(log_path):
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def print_usage():
    print("""
    Incorrect usage.
    source_path, replica_path and log_path are required arguments.
    Usage: 
    python main.py 
    [-s | --source_path]  <"source_path"> 
    [-r | --replica_path] <"replica_path"> 
    [-i | --interval]     <interval> 
    [-l | --log_path]     <"log_path">
    
    Use [-h | --help] for more detailed information.
    """)

def print_help():
    print("""
    This program synchronizes two folders: a source directory with a replica directory.
    Program synchronizes it with provided interval. 
    Default interval value - 10 seconds.
    
    Usage: python main.py [OPTIONS]
    
    Options:
        -s, --source_path    <"path">   Path to the source directory
        -r, --replica_path   <"path">   Path to the replica directory
        -i, --interval       <time>    Time interval (in seconds)
        -l, --log_path       <"path">   Path to the log file
        -h, --help                    Display this help message and exit

    Example usage:
        python main.py -p /path/to/source -r /path/to/replica -i 60 -l /path/to/log
    """)

def parse_arguments(arguments_list):
    # Arguments options
    short_options = "s:r:i:l:h"
    long_options = ["source_path=", "replica_path=", "interval=", "log_path=", "help"]

    # Default values
    source_path = None
    replica_path = None
    interval = DEFAULT_INTERVAL
    log_path = None

    try:
        opts, _ = getopt.getopt(arguments_list, short_options, long_options)
    except getopt.GetoptError as e:
        print(f"Error: {str(e)}")
        print_usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif opt in ('-s', '--source_path'):
            source_path = arg
        elif opt in ('-r', '--replica_path'):
            replica_path = arg
        elif opt in ('-i', '--interval'):
            try:
                interval = int(arg)
                if interval <= 0:
                    raise ValueError
            except ValueError:
                print("Error: Interval must be a positive integer.")
                sys.exit(2)
        elif opt in ('-l', '--log_path'):
            log_path = arg
        else:
            print(f"Unknown argument: {opt}")
            print_usage()
            sys.exit(1)

    # Required arguments check 
    missing_arguments = []

    if not source_path:
        missing_arguments.append("source_path")
    if not replica_path:
        missing_arguments.append("replica_path")
    if not log_path:
        missing_arguments.append("log_path")

    if missing_arguments:
        print("Error: Missing required arguments:", ", ".join(missing_arguments))
        print_usage()
        sys.exit(1)

    return source_path, replica_path, interval, log_path


def sync(source_path, replica_path):
    
    for item in os.listdir(source_path):
        source_path_current = os.path.join(source_path, item)
        replica_path_current = os.path.join(replica_path, item)
        
        if os.path.isdir(source_path_current):
            if not os.path.exists(replica_path_current):
                shutil.copytree(source_path_current, replica_path_current)
                logging.info(f"Created directory: {replica_path_current}")

            else:
                sync(source_path_current, replica_path_current)
        else:
            
            if not os.path.exists(replica_path_current):
                shutil.copy2(source_path_current, replica_path_current)
                logging.info(f"Copied new file: {source_path_current} to {replica_path_current}")
            else:
                source_modified_time = os.path.getmtime(source_path_current)
                replica_modified_time = os.path.getmtime(replica_path_current)
                
                if source_modified_time > replica_modified_time:
                    shutil.copy2(source_path_current, replica_path_current)
                    logging.info(f"Updated file: {replica_path_current}")


def delete_replica(source_path, replica_path):
    
    source_items = set(os.listdir(source_path))
        
    for item in os.listdir(replica_path):
        replica_path_current = os.path.join(replica_path, item)
        
        if item not in source_items:
            if os.path.isdir(replica_path_current):
                shutil.rmtree(replica_path_current)
                logging.info(f"Removed directory: {replica_path_current}")
            else:
                os.remove(replica_path_current)
                logging.info(f"Removed file: {replica_path_current}")
        else:
            if os.path.isdir(replica_path_current):
                 delete_replica(os.path.join(source_path, item), replica_path_current)
        
        
def folders_sync(source_path, replica_path):
    
    # Replica check
    if not os.path.exists(replica_path):
        os.makedirs(replica_path)
        logging.info(f"Created replica directory: {replica_path}")
    
    # Main synchronize's logic
    sync(source_path, replica_path)
    
    # Delete all files/dirs which are not in source 
    delete_replica(source_path, replica_path)


def main(arguments_list):
    
    # Arguments Parsing
    try:
        source_path, replica_path, interval, log_path = parse_arguments(arguments_list)
        setup_logging(log_path)
        
        while True:
            folders_sync(source_path, replica_path)
            time.sleep(interval)    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(3)
            

    
    
if __name__ == "__main__":
    arguments_list = sys.argv[1:]
    main(arguments_list)

