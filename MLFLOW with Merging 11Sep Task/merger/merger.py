# Writing class for merging multiple files into one

import os
import pandas as pd
import shutil
from setup_log.setup_logger import setup_logger


class Merger():
    """
    Description: Adding new column and saving csv file and will create full data
    
    Parameters:
        raw_file_path: raw file path where the raw file folders are located.
        start_row_no: start row number of the csv file. for skiping the above cells to avoid unnecessary information.

    IMPROVEMENT NOTE_: This class assume the input folder will contain only necessary sub-data folders.
    It can break if uncecessary sub-data folder or file is present on the input path for the Merger class.
    """

    def __init__(self, raw_file_path, start_row_no = 0):
        self.log = setup_logger("merger_log", "logs/merger.log")
        self.raw_file_path = raw_file_path # Raw file path
        self.datafolder = "./datafolder" # Data folder for storing the raw files
        assert type(start_row_no) == int, "start_row_no must be an integer" # Validating start_row_no
        self.start_row_no = start_row_no # Start row number from where the row is starded to be read on the raw file

    def copy_raw_folder(self):
        """
        Description: Copying raw file to the datafolder.

        Input: None.
        Output: Will create new Folder named `datafolder` and will Copied raw file to the datafolder.
        
        On Error: Will raise exception. and log error.
        """
        try:
            
            self.log.info("Copying raw file to datafolder")
            # Copying raw file to the raw_file_path
            shutil.copytree(self.raw_file_path, self.datafolder)
            self.log.info("Copying raw file to datafolder is successful")
        
        except Exception as e:
            self.log.error("Copying raw file to datafolder is failed" + str(e))
            raise e

    
    def add_label_col(self):
        """
        Method: add_label_col
        Description: Reading each raw file and adding label column as per folder name.

        Input: None.
        Output: Add new column and saved csv file.

        On Error: Will raise exception. and log error.
        """
        try:
            self.log.info("Copy raw file to datafolder")
            self.copy_raw_folder() # Copying raw file to the datafolder
            self.log.info("Raw files moved to data folder.")

            # looping thorugh all the files in the datafolder
            self.log.info("Looping through all folder inside datafolder")
            for root, _, files in os.walk(self.datafolder):
                try:
                    if len(files) > 0: # skiping empty folder
                         label = root.split("\\")[1] # Getting the label from the folder name
                         self.log.info("Label: " + label)

                         # Looping through all the files in the folder
                         for file in files:
                             self.log.info("Reading file: " + file)
                             df = pd.read_csv(os.path.join(root, file), skiprows=self.start_row_no, error_bad_lines=False)
                             self.log.info("Adding label column" + label)
                             df["label"] = label # Adding label column
                             self.log.info("Saving file: " + file)
                             df.to_csv(os.path.join(root, file), index=False) # Saving the file
                             self.log.info("File saved successfully")

                         self.log.info("All files in the folder are processed for " + root)
                except Exception as e:
                    self.log.error("Error while processing the folder " + root + str(e))
                    raise e
        except Exception as e:  
            self.log.error("Error while adding label column " + str(e))
            raise e

    def all_file_list(self):
        """
        Method: all_file_list
        
        Description: Will Create a list of list containing all files path inside datafolder.
        
        Input: None.
        Output: list of list containing all files inside datafolder.

        On Error: Will raise exception. and log error.
        """
        try:
            self.log.info("Creating list of list for all files inside datafolder")
            all_files = list() # List of list containing all files inside datafolder
            for root, _, files in os.walk(self.datafolder):
                if len(files) > 0: # skiping empty folder
                    l = list()
                    for file in files:
                        l.append(os.path.join(root, file))
                    all_files.append(l) # Adding the list to the list of list
            self.log.info("List of list for all files inside datafolder is created")
            return all_files # Returning the list of list
        
        except Exception as e:
            self.log.error("Error while creating list of list for all files inside datafolder " + str(e))
            raise e
    
    def merge_csv(self, merged_folder, *paths):
        """
        Method: merge_csv
        
        Description: Merging all the csv files inside datafolder into one file for one label.
        
        Input: None.
        Output: Merged csv file.

        On Error: Will raise exception. and log error.
        """
        try:
            self.log.info("Merging all the csv files inside datafolder into one file")
            for ix, path in enumerate(paths):
                with open(path) as file:
                    if ix > 0:
                        next(file) # Skipping the header
                    merged_folder.writelines(file) # Writing the file to the merged_folder

            self.log.info("Merging all the csv files inside datafolder into one file is successful")
        except Exception as e:
            self.log.error("Error while merging all the csv files inside datafolder into one file " + str(e))
            raise e


    def merge_files(self):
        """
        Method: merge_files
        
        Description: Merging all the files inside datafolder into one file for individuals label.
        
        Input: None.
        Output: Merged csv file.

        On Error: Will raise exception. and log error.
        """
        try:
            if not os.path.isdir("./merged_folder"):
                os.mkdir("./merged_folder")
                self.log.info("Created merged folder")
            self.log.info("Merging all the files inside datafolder into one file")
            all_files = self.all_file_list() # Getting the list of list containing all the files inside datafolder
            for file in all_files:
                file_name = "merged_folder\merge_" + str(file[0].split("\\")[1]) + ".csv" # Creating the file name
                with open(file_name, "w") as merged_folder:
                    self.merge_csv(merged_folder, *file) # Merging the files
            self.log.info("Merging all the files inside datafolder into one file is successful")

        except Exception as e:
            self.log.error("Error while merging all the files inside datafolder into one file " + str(e))
            raise e

        
    def create_full_data(self):
        """
        Method: create_full_data
        
        Description: Merging all the files inside datafolder into one final csv file.
        
        Input: None.
        Output: Merged csv file will be saved on local PWD as named "full_data.csv"

        On Error: Will raise exception. and log error.
        """
        try:
            self.log.info("Creating full data")
            merged_files_list = list() # Creating the list of merged files
            for root, _, files in os.walk("./merged_folder"):
                for file in files:
                    merged_files_list.append(os.path.join(root, file)) # Adding the file to the list

            self.log.info("Merging all the files inside merged_folder into one file")
            with open("full_data.csv", "w") as full_data:
                self.merge_csv(full_data, *merged_files_list) # Merging the files
            self.log.info("Merging all the files inside merged_folder into one file is successful")
        except Exception as e:
            self.log.error("Error while creating full data " + str(e))
            raise e
        



        







































