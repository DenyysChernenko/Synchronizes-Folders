import getopt
import sys
import os
import shutil
import time
import logging

# Constants
DEFAULT_INTERVAL = 10


def setup_logging(log_path):
    # Settup Logging Config
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup Logging Config for Stream (output in console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)


def print_usage():
    print("""
    Incorrect usage.
    source_path is required argument.
    Usage: 
    python main.py 
    [-s | --source_path]  <"source_path"> (required)
    [-r | --replica_path] <"replica_path"> (optional)
    [-i | --interval]     <interval> (default=10)
    [-l | --log_path]     <"log_path"> (optional)
    
    Use [-h | --help] for more detailed information.
    """)


def print_help():
    print("""
    This program synchronizes two folders: a source directory with a replica directory.
    It continuously checks for changes at the specified interval.
    Default interval value - 10 seconds.
    
    Usage: python main.py [OPTIONS]
    
    Options:
        -s, --source_path    <"path">   Path to the source directory (required)
        -r, --replica_path   <"path">   Path to the replica directory (optional, default: './replica')
        -i, --interval       <time>    Time interval (in seconds)
        -l, --log_path       <"path">   Path to the log file (optional, default: './sync.log')
        -h, --help                    Display this help message and exit

    Example usage:
        python main.py -s /path/to/source
        python main.py -p /path/to/source -r /path/to/replica -i 60 -l /path/to/log
        
    Note: Ensure that the source path exists before running the program.
          Provide path to folder in quotes ('path'|"path")
    """)


def parse_arguments(arguments_list):
    # Arguments options
    short_options = "s:r:i:l:h"
    long_options = ["source_path=", "replica_path=", "interval=", "log_path=", "help"]

    # Default values
    source_path = None
    replica_path = os.path.join(os.getcwd(), "replica")
    interval = DEFAULT_INTERVAL
    log_path = os.path.join(os.getcwd(), "sync.log")

    # Take arguments from command line
    try:
        opts, _ = getopt.getopt(arguments_list, short_options, long_options)
    except getopt.GetoptError as e:
        print(f"Error: {str(e)}")
        print_usage()
        sys.exit(1)

    # Assign arguments to variables
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

    # Required argument check 
    if not source_path:
        print("Error: Missing required argument: source_path")
        print_usage()
        sys.exit(1)

    return source_path, replica_path, interval, log_path


def sync(source_path, replica_path):
    
    for item in os.listdir(source_path):
        source_path_current = os.path.join(source_path, item)
        replica_path_current = os.path.join(replica_path, item)
        
        if os.path.isdir(source_path_current):
            # Add directory if not exists (with all subtrees)
            if not os.path.exists(replica_path_current):
                shutil.copytree(source_path_current, replica_path_current)
                logging.info(f"Created directory: {replica_path_current}")

            else:
                # Check all subtrees if directory exists
                sync(source_path_current, replica_path_current)
        else:
            # Add file if not exists
            if not os.path.exists(replica_path_current):
                shutil.copy2(source_path_current, replica_path_current)
                logging.info(f"Copied new file: {source_path_current} to {replica_path_current}")
            else:
                # Check modified time, and change if file was modified
                source_modified_time = os.path.getmtime(source_path_current)
                replica_modified_time = os.path.getmtime(replica_path_current)
                
                if source_modified_time > replica_modified_time:
                    shutil.copy2(source_path_current, replica_path_current)
                    logging.info(f"Updated file: {replica_path_current}")


def delete_replica(source_path, replica_path):
    
    # Take all files/dirs from source (current level)
    source_items = set(os.listdir(source_path))
    
    for item in os.listdir(replica_path):
        replica_path_current = os.path.join(replica_path, item)
        

        if item not in source_items:
            # Delete item if dir
            if os.path.isdir(replica_path_current):
                shutil.rmtree(replica_path_current)
                logging.info(f"Removed directory: {replica_path_current}")
            else:
                # Delete item if file
                os.remove(replica_path_current)
                logging.info(f"Removed file: {replica_path_current}")
        else:
            # Check if directory, also check all subtrees of this directory
            if os.path.isdir(replica_path_current):
                 delete_replica(os.path.join(source_path, item), replica_path_current)
        
        
def folders_sync(source_path, replica_path):
    
    
    if not os.path.exists(replica_path):
        os.makedirs(replica_path)
        logging.info(f"Created replica directory: {replica_path}")
    
    if not os.path.exists(source_path):
        print(f"Error: Source path '{source_path}' does not exist.")
        sys.exit(1)
        
    # Main synchronize's logic
    sync(source_path, replica_path)
    
    # Delete all files/dirs which are not in source 
    delete_replica(source_path, replica_path)


def main(arguments_list):
    
    try:
        # Arguments Parsing
        source_path, replica_path, interval, log_path = parse_arguments(arguments_list)
        setup_logging(log_path)
        
        # Start Sync
        while True:
            folders_sync(source_path, replica_path)
            time.sleep(interval)    
    except KeyboardInterrupt:
        print("\nSynchronization stopped by user.")
        sys.exit(0)  
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(3)
            

if __name__ == "__main__":
    arguments_list = sys.argv[1:]
    main(arguments_list)

