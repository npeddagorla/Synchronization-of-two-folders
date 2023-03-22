
import os
import shutil
import time
import argparse
import logging
import sys


class FolderSync:
    """
    A class that synchronizes source folder to replica folder at a given interval
    and logs all file creation/copying/removal operations to a log file and console output.
    """

    def __init__(self, src_folder, replica_folder, log_file_path, sync_interval):
        self.src_folder = src_folder
        self.replica_folder = replica_folder
        self.log_file_path = log_file_path
        self.sync_interval = sync_interval
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger('folder_sync')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # log to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # log to file
        fh = logging.FileHandler(self.log_file_path)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger

    def sync(self):
        """
        Synchronizes source folder to replica folder and logs all file creation/copying/removal
        operations to a log file and console output.
        """
        # create log file

        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w'):
                pass
        

        while True:
            try:
                # synchronize source folder to replica folder
                for root, dirs, files in os.walk(self.src_folder):
                    for dir in dirs:
                        src_root = os.path.join(root, dir)
                        replica_root = os.path.join(self.replica_folder, os.path.relpath(src_root, self.src_folder))
                        if not os.path.exists(replica_root):
                            os.makedirs(replica_root)
                            self.logger.info(f"Created Folder: {replica_root}")


                # synchronize source files to replica files 
                    for file in files:
                        src_root = os.path.join(root, file)
                        replica_root = os.path.join(self.replica_folder, os.path.relpath(src_root, self.src_folder))
                        if os.path.exists(replica_root) and os.path.getmtime(src_root) == os.path.getmtime(replica_root):
                            continue
                        shutil.copy2(src_root, replica_root)
                        self.logger.info(f"Copied file: {replica_root}")


                # delete the missing files in replica folder,files which are not present in source folder, files  
                    for rep_root, rep_dirs, rep_files in os.walk(self.replica_folder):
                        source_root = rep_root.replace(self.replica_folder, self.src_folder)
                        for directory in rep_dirs:
                            source_directory = os.path.join(source_root, directory)
                            if not os.path.exists(source_directory):
                                shutil.rmtree(os.path.join(rep_root, directory))
                                self.logger.info(f"Deleted folder: {source_directory}")
                        
                    # for replica_root, replica_dirs, replica_files in os.walk(self.replica_folder):    
                        for r_file in rep_files:
                            replica_path = os.path.join(rep_root, r_file)
                            src_root = os.path.join(self.src_folder, os.path.relpath(replica_path, self.replica_folder))
                            if not os.path.exists(src_root):
                                os.remove(replica_path)
                                self.logger.info(f"Deleted file: {replica_path}")
                                

                        
                # wait for next sync interval
                time.sleep(self.sync_interval)

            except Exception as e:
                self.logger.info(f"Exception Error: {str(e)}\n")
                sys.exit(0)
                
            

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('src_folder', type=str, help='Path to source folder')
    parser.add_argument('replica_folder', type=str, help='Path to replica folder')
    parser.add_argument('log_file_path', type=str, help='Path to log file')
    parser.add_argument('sync_interval', type=int, help='Sync interval in seconds')
    args = parser.parse_args()

    # create FolderSync object
    folder_sync = FolderSync(args.src_folder, args.replica_folder,args.log_file_path,args.sync_interval)
    folder_sync.sync()
