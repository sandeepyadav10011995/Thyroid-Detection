from datetime import datetime
from os import listdir
from application_logging.logger import AppLogger
import pandas as pd


class DataTransform:
    """
          This class shall be used for transforming the Good Raw Training Data before loading it in Database!!.
     """

    def __init__(self):
        self.goodDataPath = "Training_Raw_files_validated/Good_Raw"
        self.logger = AppLogger()

    def addQuotesToStringValuesInColumn(self):

        """
                       Method Name: addQuotesToStringValuesInColumn
                       Description: This method converts all the columns with string datatype such that each value for
                                    that column is enclosed in quotes. This is done to avoid the error while
                                    inserting string values in table as varchar.
          """

        log_file = open("Training_Logs/addQuotesToStringValuesInColumn.txt", 'a+')
        try:
            onlyFiles = [f for f in listdir(self.goodDataPath)]
            for file in onlyFiles:
                data = pd.read_csv(self.goodDataPath + "/" + file)
                # list of columns with string datatype variables
                column = ['sex', 'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication', 'sick', 'pregnant',
                          'thyroid_surgery', 'I131_treatment', 'query_hypothyroid', 'query_hyperthyroid', 'lithium',
                          'goitre', 'tumor', 'hypopituitary', 'psych', 'TSH_measured', 'T3_measured', 'TT4_measured',
                          'T4U_measured', 'FTI_measured', 'TBG_measured', 'TBG', 'referral_source', 'Class']

                for col in data.columns:
                    if col in column:  # add quotes in string value
                        data[col] = data[col].apply(lambda x: "'" + str(x) + "'")
                    if col not in column:  # add quotes to '?' values in integer/float columns
                        data[col] = data[col].replace('?', "'?'")
                # csv.update("'"+ csv['Wafer'] +"'")
                # csv.update(csv['Wafer'].astype(str))
                # csv['Wafer'] = csv['Wafer'].str[6:]
                data.to_csv(self.goodDataPath + "/" + file, index=None, header=True)
                self.logger.log(log_file, " %s: Quotes added successfully!!" % file)
                # log_file.write("Current Date :: %s" %date +"\t" + "Current time:: %s" % current_time + "\t \t" +  + "\n")
        except Exception as e:
            self.logger.log(log_file, "Data Transformation failed because:: %s" % e)
            # log_file.write("Current Date :: %s" %date +"\t" +"Current time:: %s" % current_time + "\t \t" + "Data Transformation failed because:: %s" % e + "\n")
            log_file.close()
        log_file.close()
