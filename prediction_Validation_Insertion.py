from datetime import datetime
from Prediction_Raw_Data_Validation.predictionDataValidation import PredictionDataValidation
from DataTypeValidation_Insertion_Prediction.DataTypeValidationPrediction import DBOperation
from DataTransformation_Prediction.DataTransformationPrediction import DataTransformPredict
from application_logging import logger


class PredictionValidation:
    def __init__(self, path):
        self.raw_data = PredictionDataValidation(path)
        self.data_transform = DataTransformPredict()
        self.db_operation = DBOperation()
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.AppLogger()

    def prediction_validation(self):

        try:

            self.log_writer.log(self.file_object, 'Start of Validation on files for prediction!!')
            # Extracting values from prediction schema
            length_of_date_stamp_in_file, length_of_time_stamp_in_file, column_names, no_columns = self.raw_data.valuesFromSchema()
            # Getting the regex defined to validate filename
            regex = self.raw_data.manualRegexCreation()
            # Validating filename of prediction files
            self.raw_data.validationFileNameRaw(regex, length_of_date_stamp_in_file, length_of_time_stamp_in_file)
            # Validating column length in the file
            self.raw_data.validateColumnLength(no_columns)
            # Validating if any column has all values missing
            self.raw_data.validateMissingValuesInWholeColumn()
            self.log_writer.log(self.file_object, "Raw Data Validation Complete!!")

            self.log_writer.log(self.file_object, "Starting Data Transformation!!")
            # Replacing blanks in the csv file with "Null" values to insert in table
            self.data_transform.addQuotesToStringValuesInColumn()

            self.log_writer.log(self.file_object, "DataTransformation Completed!!!")

            self.log_writer.log(self.file_object, "Creating Prediction_Database and tables on the basis of given schema!!!")
            # Create database with given name, if present open the connection! Create table with columns given in schema
            self.db_operation.createTableDb('Prediction', column_names)
            self.log_writer.log(self.file_object, "Table creation Completed!!")
            self.log_writer.log(self.file_object, "Insertion of Data into Table started!!!!")
            # Insert csv files in the table
            self.db_operation.insertIntoTableGoodData('Prediction')
            self.log_writer.log(self.file_object, "Insertion in Table completed!!!")
            self.log_writer.log(self.file_object, "Deleting Good Data Folder!!!")
            # Delete the good data folder after loading files in table
            self.raw_data.deleteExistingGoodDataTrainingFolder()
            self.log_writer.log(self.file_object, "Good_Data folder deleted!!!")
            self.log_writer.log(self.file_object, "Moving bad files to Archive and deleting Bad_Data folder!!!")
            # Move the bad files to archive folder
            self.raw_data.moveBadFilesToArchiveBad()
            self.log_writer.log(self.file_object, "Bad files moved to archive!! Bad folder Deleted!!")
            self.log_writer.log(self.file_object, "Validation Operation completed!!")
            self.log_writer.log(self.file_object, "Extracting csv file from table")
            # Export data in table to csv file
            self.db_operation.selectingDataFromTableIntoCSV('Prediction')

        except Exception as e:
            raise e
