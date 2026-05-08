class Prediction:
    def __init__(self, data, result, confidence, raw_inputs):
        self.data = data
        self.result = result
        self.confidence = confidence
        self.raw_inputs = raw_inputs