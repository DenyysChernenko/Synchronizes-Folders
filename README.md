# Synchronizes-Folders

This is a Python-based folder synchronization program that ensures the **replica** folder is a full, identical copy of the **source** folder. The tool performs one-way synchronization, where any changes in the source folder are replicated in the replica folder at specified intervals. It supports logging for file/folder creation, updates, and deletions, both in a log file and on the console.


### Installation

1. Clone the repository or download the script files.
2. Open a terminal (or command prompt) and navigate to the directory where the script is located.


### Arguments

  Options:
        ```-s, --source_path    <"path">   ``` 
        Path to the source directory (required)
        ``` -r, --replica_path   <"path">   ```   
        Path to the replica directory (optional, default: './replica')
        ``` -i, --interval      <time> ```   
        Time interval (in seconds)
        ``` -l, --log_path       <"path"> ```  
        Path to the log file (optional, default: './sync.log')
        ``` -h, --help    ```                
        Display this help message and exit


### Usage
```
    Example usage:
        python main.py [OPTIONS]
        python main.py -s /path/to/source
        python main.py -s /path/to/source -r /path/to/replica -i 5 -l /path/to/log
        
    Note: Ensure that the source path exists before running the program.
          Provide path to folder in quotes ('path'|"path")
```