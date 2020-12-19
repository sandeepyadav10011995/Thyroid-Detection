"""
This is the Entry point for Training the Machine Learning Model.
"""

# Doing the necessary imports
from sklearn.model_selection import train_test_split
from data_ingestion import data_loader
from data_preprocessing import preprocessing
from data_preprocessing import clustering
from best_model_finder import tuner
from file_operations import file_methods
from application_logging import logger


class TrainModel:

    def __init__(self):
        self.log_writer = logger.AppLogger()
        self.file_object = open("Training_Logs/ModelTrainingLog.txt", 'a+')

    def trainingModel(self):
        # Logging the start of Training
        self.log_writer.log(self.file_object, 'Start of Training')
        try:
            # Getting the data from the source
            data_getter = data_loader.DataGetter(self.file_object, self.log_writer)
            data = data_getter.get_data()

            """doing the data preprocessing"""

            preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
            # data=preprocessor.remove_columns(data,['Wafer'])
            # remove the unnamed column as it doesn't contribute to prediction.

            # removing unwanted columns as discussed in the EDA part in ipynb file
            data = preprocessor.dropUnnecessaryColumns(data,
                                                       ['TSH_measured', 'T3_measured', 'TT4_measured', 'T4U_measured',
                                                        'FTI_measured', 'TBG_measured', 'TBG', 'TSH'])

            # replacing '?' values with np.nan as discussed in the EDA part

            data = preprocessor.replaceInvalidValuesWithNull(data)

            # get encoded values for categorical data

            data = preprocessor.encodeCategoricalValues(data)

            # create separate features and labels
            X, Y = preprocessor.separate_label_feature(data, label_column_name='Class')

            # check if missing values are present in the dataset
            is_null_present = preprocessor.is_null_present(X)

            # if missing values are there, replace them appropriately.
            if is_null_present:
                X = preprocessor.impute_missing_values(X)  # missing value imputation

            X, Y = preprocessor.handleImbalanceDataset(X, Y)
            # check further which columns do not contribute to predictions
            # if the standard deviation for a column is zero, it means that the column has constant values
            # and they are giving the same output both for good and bad sensors
            # prepare the list of such columns to drop
            # cols_to_drop=preprocessor.get_columns_with_zero_std_deviation(X)
            # drop the columns obtained above
            # X=preprocessor.remove_columns(X,cols_to_drop)

            """ Applying the clustering approach"""
            # Object Initialization.
            k_means = clustering.KMeansClustering(self.file_object, self.log_writer)
            # Using the Elbow-Plot to find the number of optimum clusters
            number_of_clusters = k_means.elbowPlot(X)

            # Divide the data into clusters
            X = k_means.createClusters(X, number_of_clusters)
            # create a new column in the dataset consisting of the corresponding cluster assignments.
            X['Labels'] = Y
            # getting the unique clusters from our dataset
            list_of_clusters = X['Cluster'].unique()

            """parsing all the clusters and looking for the best ML algorithm to fit on individual cluster"""

            for i in list_of_clusters:
                # Filter the data for one cluster
                cluster_data = X[X['Cluster'] == i]
                # Prepare the feature and Label columns
                cluster_features = cluster_data.drop(['Labels', 'Cluster'], axis=1)
                cluster_label = cluster_data['Labels']

                # Splitting the data into training and test set for each cluster one by one
                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=1 / 3,
                                                                    random_state=355)
                # Object Initialization.
                model_finder = tuner.ModelFinder(self.file_object, self.log_writer)

                # Getting the best model for each of the clusters
                best_model_name, best_model = model_finder.getBestModel(x_train, y_train, x_test, y_test)

                # Saving the best model to the directory.
                file_op = file_methods.FileOperation(self.file_object, self.log_writer)
                save_model = file_op.saveModel(best_model, best_model_name + str(i))

            # Logging the successful Training
            self.log_writer.log(self.file_object, 'Successful End of Training')
            self.file_object.close()

        except Exception:
            # logging the unsuccessful Training
            self.log_writer.log(self.file_object, 'Unsuccessful End of Training')
            self.file_object.close()
            raise Exception
