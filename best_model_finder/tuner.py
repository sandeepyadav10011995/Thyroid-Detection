from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd


class ModelFinder:
    """
                This class shall  be used to find the model with best accuracy and AUC score.
    """

    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object
        self.clf = RandomForestClassifier()
        self.knn = KNeighborsClassifier()

    def getBestParamsForRandomForest(self, train_x, train_y):
        """
                        Method Name: getBestParamsForRandomForest
                        Description: get the parameters for Random Forest Algorithm which give the best accuracy.
                                     Use Hyper Parameter Tuning.
                        Output: The model with the best parameters
                        On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object,
                               'Entered the get_best_params_for_random_forest method of the Model_Finder class')
        try:
            # Initializing with different combination of parameters
            self.param_grid = {"n_estimators": [10, 50, 100, 130], "criterion": ['gini', 'entropy'],
                               "max_depth": range(2, 4, 1), "max_features": ['auto', 'log2']}

            # Creating an object of the Grid Search class
            self.grid = GridSearchCV(estimator=self.clf, param_grid=self.param_grid, cv=5,  verbose=3)
            # Finding the best parameters
            self.grid.fit(train_x, train_y)

            # Extracting the best parameters
            self.criterion = self.grid.best_params_['criterion']
            self.max_depth = self.grid.best_params_['max_depth']
            self.max_features = self.grid.best_params_['max_features']
            self.n_estimators = self.grid.best_params_['n_estimators']

            # Creating a new model with the best parameters
            self.clf = RandomForestClassifier(n_estimators=self.n_estimators, criterion=self.criterion,
                                              max_depth=self.max_depth, max_features=self.max_features)
            # Training the mew model
            self.clf.fit(train_x, train_y)
            self.logger_object.log(self.file_object, 'Random Forest best params: ' + str(self.grid.best_params_) +
                                   '. Exited the get_best_params_for_random_forest method of the Model_Finder class')

            return self.clf
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occured in get_best_params_for_random_forest method of the Model_Finder class. Exception message:  ' + str(
                                       e))
            self.logger_object.log(self.file_object,
                                   'Random Forest Parameter tuning  failed. Exited the get_best_params_for_random_forest method of the Model_Finder class')
            raise Exception()

    def getBestParamsForKNN(self, train_x, train_y):
        """
                    Method Name: getBestParamsForKNN
                    Description: get the parameters for KNN Algorithm which give the best accuracy.
                                 Use Hyper Parameter Tuning.
                    Output: The model with the best parameters
                    On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object,
                               'Entered the get_best_params_for_Ensembled_KNN method of the Model_Finder class')
        try:
            # Initializing with different combination of parameters
            self.param_grid_knn = {
                'algorithm': ['ball_tree', 'kd_tree', 'brute'],
                'leaf_size': [10, 17, 24, 28, 30, 35],
                'n_neighbors': [4, 5, 8, 10, 11],
                'p': [1, 2]
            }

            # Creating an object of the Grid Search class
            self.grid = GridSearchCV(self.knn, self.param_grid_knn, verbose=3,
                                     cv=5)
            # Finding the best parameters
            self.grid.fit(train_x, train_y)

            # Extracting the best parameters
            self.algorithm = self.grid.best_params_['algorithm']
            self.leaf_size = self.grid.best_params_['leaf_size']
            self.n_neighbors = self.grid.best_params_['n_neighbors']
            self.p = self.grid.best_params_['p']

            # Creating a new model with the best parameters
            self.knn = KNeighborsClassifier(algorithm=self.algorithm, leaf_size=self.leaf_size,
                                            n_neighbors=self.n_neighbors, p=self.p, n_jobs=-1)
            # Training the mew model
            self.knn.fit(train_x, train_y)
            self.logger_object.log(self.file_object, 'KNN best params: ' + str(self.grid.best_params_) +
                                   '. Exited the KNN method of the Model_Finder class')
            return self.knn
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occured in knn method of the Model_Finder class. Exception message:  ' + str(
                                       e))
            self.logger_object.log(self.file_object,
                                   'knn Parameter tuning  failed. Exited the knn method of the Model_Finder class')
            raise Exception()

    def getBestModel(self, train_x, train_y, test_x, test_y):
        """
                    Method Name: getBestModel
                    Description: Find out the Model which has the best AUC score.
                    Output: The best model name and the model object
                    On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object,
                               'Entered the get_best_model method of the Model_Finder class')
        # Create best model for KNN
        try:
            self.knn = self.getBestParamsForKNN(train_x, train_y)
            # Predictions using the KNN Model
            self.prediction_knn = self.knn.predict_proba(test_x)

            # If there is only one label in y, then roc_auc_score returns error. We will use accuracy in that case
            if len(test_y.unique()) == 1:
                self.knn_score = accuracy_score(test_y, self.prediction_knn)
                # Log AUC
                self.logger_object.log(self.file_object, 'Accuracy for knn:' + str(self.knn_score))
            else:
                # AUC for KNN
                self.knn_score = roc_auc_score(test_y, self.prediction_knn, multi_class='ovr')
                # Log AUC
                self.logger_object.log(self.file_object, 'AUC for knn:' + str(self.knn_score))

            # Create best model for Random Forest
            self.random_forest = self.getBestParamsForRandomForest(train_x, train_y)
            # Prediction using the Random Forest Algorithm
            self.prediction_random_forest = self.random_forest.predict_proba(test_x)

            # If there is only one label in y, then roc_auc_score returns error. We will use accuracy in that case
            if len(test_y.unique()) == 1:
                self.random_forest_score = accuracy_score((test_y), self.prediction_random_forest)
                self.logger_object.log(self.file_object, 'Accuracy for RF:' + str(self.random_forest_score))
            else:
                self.random_forest_score = roc_auc_score((test_y), self.prediction_random_forest, multi_class='ovr')
                # AUC for Random Forest
                self.logger_object.log(self.file_object, 'AUC for RF:' + str(self.random_forest_score))

            # Comparing the two models
            if self.random_forest_score < self.knn_score:
                return 'KNN', self.knn
            else:
                return 'RandomForest', self.random_forest

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occured in get_best_model method of the Model_Finder class. Exception message:  ' + str(
                                       e))
            self.logger_object.log(self.file_object,
                                   'Model Selection Failed. Exited the get_best_model method of the Model_Finder class')
            raise Exception()
