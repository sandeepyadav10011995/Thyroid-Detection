import pickle
import os
import shutil


class FileOperation:
    """
                This class shall be used to save the model after training and load the saved model for prediction.
    """
    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object
        self.model_directory = 'models/'

    def saveModel(self, model, filename):
        """
            Method Name: saveModel
            Description: Save the model file to directory
            Outcome: File gets saved
            On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object, 'Entered the save_model method of the File_Operation class')
        try:
            # Create separate directory for each cluster
            path = os.path.join(self.model_directory, filename)
            # Remove previously existing models for each clusters
            if os.path.isdir(path):
                shutil.rmtree(self.model_directory)
                os.makedirs(path)
            else:
                os.makedirs(path)
            with open(path + '/' + filename+'.sav', 'wb') as f:
                # Save the model to file
                pickle.dump(model, f)
            self.logger_object.log(self.file_object, 'Model File ' + filename +
                                   ' saved. Exited the save_model method of the Model_Finder class')

            return 'success'
        except Exception as e:
            self.logger_object.log(
                self.file_object,
                'Exception occured in save_model method of the Model_Finder class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object, 'Model File ' + filename +
                                   ' could not be saved. Exited the save_model method of the Model_Finder class')
            raise Exception()

    def loadModel(self, filename):
        """
                    Method Name: loadModel
                    Description: load the model file to memory
                    Output: The Model file loaded in memory
                    On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object, 'Entered the load_model method of the File_Operation class')
        try:
            with open(self.model_directory + filename + '/' + filename + '.sav',
                      'rb') as f:
                self.logger_object.log(self.file_object,
                                       'Model File ' + filename + ' loaded. Exited the load_model method of the Model_Finder class')
                return pickle.load(f)
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occured in load_model method of the Model_Finder class. Exception message:  ' + str(
                                       e))
            self.logger_object.log(self.file_object, 'Model File ' + filename +
                                   ' could not be saved. Exited the load_model method of the Model_Finder class')
            raise Exception()

    def findCorrectModelFile(self, cluster_number):
        """
                            Method Name: findCorrectModelFile
                            Description: Select the correct model based on cluster number
                            Output: The Model file
                            On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object,
                               'Entered the find_correct_model_file method of the File_Operation class')
        try:
            self.cluster_number = cluster_number
            self.folder_name = self.model_directory
            self.list_of_model_files = []
            self.list_of_files = os.listdir(self.folder_name)
            for self.file in self.list_of_files:
                try:
                    if self.file.index(str(self.cluster_number))!=-1:
                        self.model_name=self.file
                except:
                    continue
            self.model_name = self.model_name.split('.')[0]
            self.logger_object.log(self.file_object,
                                   'Exited the find_correct_model_file method of the Model_Finder class.')
            return self.model_name
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occured in find_correct_model_file method of the Model_Finder class. Exception message:  ' + str(
                                       e))
            self.logger_object.log(self.file_object,
                                   'Exited the find_correct_model_file method of the Model_Finder class with Failure')
            raise Exception()
