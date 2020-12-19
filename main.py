from flask import Flask, request, render_template
from flask import Response
import os
from flask_cors import CORS, cross_origin

from prediction_Validation_Insertion import PredictionValidation
from trainingModel import TrainModel
from training_Validation_Insertion import TrainValidation
# import flask_monitoringdashboard as dashboard
from predictFromModel import Prediction


os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
# dashboard.bind(app)
CORS(app)


@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRouteClient():
    try:
        if request.json is not None:
            path = request.json['filepath']
            # Object Initialization
            predict_val = PredictionValidation(path)
            # Calling the prediction_validation function
            predict_val.prediction_validation()
            # Object Initialization
            pred = Prediction(path)
            # Predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at %s!!!" % path)
        elif request.form is not None:
            path = request.form['filepath']
            # Object Initialization
            predict_val = PredictionValidation(path)
            # Calling the prediction_validation function
            predict_val.prediction_validation()
            # Object Initialization
            pred = Prediction(path)
            # Predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at %s!!!" % path)

    except ValueError:
        print("Error Occurred! " + str(ValueError))
        return Response("Error Occurred! %s" % str(ValueError))
    except KeyError:
        print("Error Occurred! " + str(KeyError))
        return Response("Error Occurred! %s" % KeyError)
    except Exception as e:
        print("Error Occurred! " + str(e))
        return Response("Error Occurred! %s" % e)


@app.route("/train", methods=['POST'])
@cross_origin()
def trainRouteClient():

    try:
        if request.json['folderPath'] is not None:
            path = request.json['folderPath']
            # Object Initialization
            train_valObj = TrainValidation(path)
            # Calling the training_validation function
            train_valObj.train_validation()
            # Object Initialization
            trainModelObj = TrainModel()
            # Training the Model for the files in the table
            trainModelObj.trainingModel()

    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    return Response("Training successful!!")


if __name__ == "__main__":
    app.run(debug=True)
