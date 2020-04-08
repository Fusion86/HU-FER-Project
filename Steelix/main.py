import os
import cv2
import time
import numpy as np
import onnxruntime
import matplotlib.pyplot as plt


class FERModel:
    def __init__(self, model_path):
        self.dimensions = (64, 64)
        self.model_path = model_path
        self.session = onnxruntime.InferenceSession(model, None)

        self.output_name = ""
        self.input_data_name = ""
        self.input_emotion_name = ""
        self.emotion_table = [[0, 1, 2, 3, 4, 5, 6, 7]]

        for x in session.get_inputs():
            print("Input: {}".format(x))

        for x in session.get_outputs():
            print("Output: {}".format(x))

    def predict(self, file):
        image = cv2.imread(file)

        # Preprocess
        gray_start = time.time()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_end = time.time()

        resize_start = time.time()
        resized = cv2.resize(gray_image, self.dimensions,
                             interpolation=cv2.INTER_AREA)
        resize_end = time.time()

        # Transform data
        data = np.array(data, dtype=np.float32)
        input_data = np.array([data]).reshape(
            [1] + [1] + list(self.dimensions))

        model_start = time.time()
        res = self.session.run([self.output_name], {
            self.input_data_name: input_data, self.input_emotion_name: emotion_table})
        model_end = time.time()

        processed = self.postprocess(res[0])
        emotions = FERModel.emotion_map(processed)

        return {"result": emotions,
                "runtime": {
                    "grayscale": gray_end - gray_start,
                    "resize": resize_end - resize_start,
                    "model": model_end - model_start
                }}

    @staticmethod
    def softmax(x):
        """Compute softmax values (probabilities from 0 to 1) for each possible label."""
        x = x.reshape(-1)
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    @staticmethod
    def postprocess(scores):
        """This function takes the scores generated by the network and
        returns the class IDs in decreasing order of probability."""
        prob = softmax(scores)
        prob = np.squeeze(prob)
        classes = np.argsort(prob)[::-1]
        return classes

    @staticmethod
    def emotion_map(classes, N=1):
        """Take the most probable labels (output of postprocess) and returns the
        top N emotional labels that fit the picture."""

        emotion_table = {"neutral": 0, "happiness": 1, "surprise": 2, "sadness": 3,
                         "anger": 4, "disgust": 5, "fear": 6, "contempt": 7}

        emotion_keys = list(emotion_table.keys())
        emotions = []
        for i in range(N):
            emotions.append(emotion_keys[classes[i]])
        return emotions


if __name__ == "__main__":
    model = FERModel("model.onnx")

    for root, dirs, files in os.walk(os.path.abspath("./out")):
        for file in files:
            print(file)
            res = model.predict(os.path.join(root, file))
            print(res)