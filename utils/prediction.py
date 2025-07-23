import joblib

def predict(data):
    model = joblib.load('models/linear_model.pkl')
    prediction = model.predict(data)
    return prediction