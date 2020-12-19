import pandas
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader_prediction
from application_logging import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import PredictionDataValidation
import pickle


class Prediction:

    def __init__(self, path):
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.AppLogger()
        self.predict_data_val = PredictionDataValidation(path)

    def predictionFromModel(self):

        try:
            # Delete the existing prediction file from last run!
            self.predict_data_val.deletePredictionFile()
            self.log_writer.log(self.file_object, 'Start of Prediction')
            data_getter = data_loader_prediction.DataGetterPredict(self.file_object, self.log_writer)
            data = data_getter.get_data()

            # code change
            # wafer_names=data['Wafer']
            # data=data.drop(labels=['Wafer'],axis=1)

            preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
            data = preprocessor.dropUnnecessaryColumns(data,
                                                       ['TSH_measured', 'T3_measured', 'TT4_measured', 'T4U_measured',
                                                        'FTI_measured', 'TBG_measured', 'TBG', 'TSH'])

            # replacing '?' values with np.nan as discussed in the EDA part

            data = preprocessor.replaceInvalidValuesWithNull(data)

            # get encoded values for categorical data

            data = preprocessor.encodeCategoricalValuesPrediction(data)
            is_null_present = preprocessor.is_null_present(data)
            if is_null_present:
                data = preprocessor.impute_missing_values(data)

            # data=data.to_numpy()
            file_loader = file_methods.FileOperation(self.file_object, self.log_writer)
            kmeans = file_loader.loadModel('KMeans')

            # Code changed
            # pred_data = data.drop(['Wafer'],axis=1)
            # drops the first column for cluster prediction
            clusters = kmeans.predict(data)
            data['clusters'] = clusters
            clusters = data['clusters'].unique()
            # Initialize blank list for storing predictions
            result = []
            # Let's load the encoder pickle file to decode the values
            with open('EncoderPickle/enc.pickle', 'rb') as file:
                encoder = pickle.load(file)

            for i in clusters:
                cluster_data = data[data['clusters'] == i]
                cluster_data = cluster_data.drop(['clusters'], axis=1)
                model_name = file_loader.findCorrectModelFile(i)
                model = file_loader.loadModel(model_name)
                for val in (encoder.inverse_transform(model.predict(cluster_data))):
                    result.append(val)
            result = pandas.DataFrame(result, columns=['Predictions'])
            path = "Prediction_Output_File/Predictions.csv"
            # Append result to prediction file
            result.to_csv("Prediction_Output_File/Predictions.csv", header=True)
            self.log_writer.log(self.file_object, 'End of Prediction')
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occured while running the prediction!! Error:: %s' % ex)
            raise ex
        return path

        # old code
        # i = 0
        # for row in data:
        #     cluster_number = kmeans.predict([row])
        #     model_name=file_loader.find_correct_model_file(cluster_number[0])
        #
        #     model = file_loader.load_model(model_name)
        #     # row= sparse.csr_matrix(row)
        #     result=model.predict([row])
        #     if result[0] == -1:
        #         category='Bad'
        #     else:
        #         category='Good'
        #     self.predictions.write("Wafer-"+ str(wafer_names[i])+','+category+'\n')
        #     i=i+1
        #     self.log_writer.log(self.file_object, 'The Prediction is :' +str(result))
        # self.log_writer.log(self.file_object, 'End of Prediction')
        # print(result)
