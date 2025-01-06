# -*- coding: utf-8 -*-
"""Project_part_3_ADHDPredictionApp.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vXTim9PVjB-LyzCYc7MlFrusrxg4xd4V
"""

!pip install flask torch pandas scikit-learn pyngrok

import torch
import torch.nn as nn
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from flask import Flask, request, jsonify, render_template_string
from pyngrok import ngrok
import joblib

# Define the RBM class
class RBM(nn.Module):
    def __init__(self, n_visible, n_hidden):
        super(RBM, self).__init__()
        self.W = nn.Parameter(torch.randn(n_visible, n_hidden) * 0.01)
        self.v_bias = nn.Parameter(torch.zeros(n_visible))
        self.h_bias = nn.Parameter(torch.zeros(n_hidden))

    def sample_h_given_v(self, v):
        activation = torch.matmul(v, self.W) + self.h_bias
        prob_h_given_v = torch.sigmoid(activation)
        sample_h = torch.bernoulli(prob_h_given_v)
        return sample_h

    def sample_v_given_h(self, h):
        activation = torch.matmul(h, self.W.t()) + self.v_bias
        prob_v_given_h = torch.sigmoid(activation)
        sample_v = torch.bernoulli(prob_v_given_h)
        return sample_v

    def gibbs_step(self, v):
        h_prob = self.sample_h_given_v(v)
        v_prob = self.sample_v_given_h(h_prob)
        h_prob = self.sample_h_given_v(v_prob)
        return v_prob

    def train_step(self, v_data):
        v_pos = v_data
        h_pos = self.sample_h_given_v(v_pos)
        v_neg = self.gibbs_step(v_pos)

        positive_hidden = torch.matmul(v_pos.t(), h_pos)
        negative_hidden = torch.matmul(v_neg.t(), self.sample_h_given_v(v_neg))

        positive_visible = torch.mean(v_pos, dim=0)
        negative_visible = torch.mean(v_neg, dim=0)

        positive_hidden_bias = torch.mean(h_pos, dim=0)
        negative_hidden_bias = torch.mean(self.sample_h_given_v(v_neg), dim=0)

        batch_size = v_data.size(0)
        self.W.data += (positive_hidden - negative_hidden) / batch_size
        self.v_bias.data += positive_visible - negative_visible
        self.h_bias.data += positive_hidden_bias - negative_hidden_bias

    def train(self, v_data, epochs=10, learning_rate=0.1, batch_size=10):
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            for i in range(0, len(v_data), batch_size):
                batch = v_data[i:i+batch_size]
                self.train_step(batch)

# Define the Feedforward Neural Network (FNN) class
class FNN(nn.Module):
    def __init__(self, input_dim):
        super(FNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

# Load the state dictionaries
rbm_state_dict = torch.load('/content/drive/MyDrive/Project_ADHD/rbm_model.pth', map_location=torch.device('cpu'))
fnn_state_dict = torch.load('/content/drive/MyDrive/Project_ADHD/fnn_model.pth', map_location=torch.device('cpu'))

# Extract the dimensions from the state dictionary
n_visible = rbm_state_dict['W'].size(0)
n_hidden = rbm_state_dict['W'].size(1)

input_dim = n_hidden

# Initialize the models with the correct sizes
rbm = RBM(n_visible, n_hidden)
fnn = FNN(input_dim)

# Load the state dictionaries into the models
rbm.load_state_dict(rbm_state_dict)
fnn.load_state_dict(fnn_state_dict)

# Load the scaler used during training
scaler = joblib.load('/content/drive/MyDrive/Project_ADHD/scaler.pkl')

# Define a function to extract features
def extract_features(v_data, rbm):
    h_prob = rbm.sample_h_given_v(torch.from_numpy(v_data).float())
    return h_prob.detach().numpy()

# Initialize Flask app
app = Flask(__name__)

# Load RBM, FNN models, and scaler
rbm = torch.load('/content/drive/MyDrive/Project_ADHD/rbm_model.pth')
fnn = torch.load('/content/drive/MyDrive/Project_ADHD/fnn_model.pth')
scaler = joblib.load('/content/drive/MyDrive/Project_ADHD/scaler.pkl')

# List of all features
FEATURES = [
    "parent_inatt_q1", "parent_inatt_q2", "parent_inatt_q3", "parent_inatt_q4", "parent_inatt_q5",
    "parent_inatt_q6", "parent_inatt_q7", "parent_inatt_q8", "parent_inatt_q9",
    "parent_hyper_q1", "parent_hyper_q2", "parent_hyper_q3", "parent_hyper_q4", "parent_hyper_q5",
    "parent_hyper_q6", "parent_hyper_q7", "parent_hyper_q8", "parent_hyper_q9",
    "parent_odd_q1", "parent_odd_q2", "parent_odd_q3", "parent_odd_q4", "parent_odd_q5",
    "parent_odd_q6", "parent_odd_q7", "parent_odd_q8",
    "parent_cd_q1", "parent_cd_q2", "parent_cd_q3", "parent_cd_q4", "parent_cd_q5",
    "parent_cd_q6", "parent_cd_q7", "parent_cd_q8", "parent_cd_q9", "parent_cd_q10",
    "parent_cd_q11", "parent_cd_q12", "parent_cd_q13", "parent_cd_q14",
    "parent_anx_q1", "parent_anx_q2", "parent_anx_q3", "parent_anx_q4", "parent_anx_q5",
    "parent_anx_q6", "parent_anx_q7",
    "parent_sch_perf_q1", "parent_sch_perf_q2", "parent_sch_perf_q3",
    "parent_soc_func_q1", "parent_soc_func_q2", "parent_soc_func_q3",
    "teacher_inatt_q1", "teacher_inatt_q2", "teacher_inatt_q3", "teacher_inatt_q4", "teacher_inatt_q5",
    "teacher_inatt_q6", "teacher_inatt_q7", "teacher_inatt_q8", "teacher_inatt_q9",
    "teacher_hyper_q1", "teacher_hyper_q2", "teacher_hyper_q3", "teacher_hyper_q4", "teacher_hyper_q5",
    "teacher_hyper_q6", "teacher_hyper_q7", "teacher_hyper_q8", "teacher_hyper_q9",
    "teacher_odd_q1", "teacher_odd_q2", "teacher_odd_q3", "teacher_odd_q4", "teacher_odd_q5",
    "teacher_odd_q6", "teacher_odd_q7", "teacher_odd_q8",
    "teacher_cd_q1", "teacher_cd_q2", "teacher_cd_q3", "teacher_cd_q4", "teacher_cd_q5",
    "teacher_cd_q6", "teacher_cd_q7", "teacher_cd_q8", "teacher_cd_q9", "teacher_cd_q10",
    "teacher_cd_q11", "teacher_cd_q12", "teacher_cd_q13", "teacher_cd_q14",
    "teacher_anx_q1", "teacher_anx_q2", "teacher_anx_q3", "teacher_anx_q4", "teacher_anx_q5",
    "teacher_anx_q6", "teacher_anx_q7",
    "teacher_sch_perf_q1", "teacher_sch_perf_q2", "teacher_sch_perf_q3",
    "teacher_soc_func_q1", "teacher_soc_func_q2", "teacher_soc_func_q3",
    "Eng_read_comp", "Eng_vocab_dev", "Eng_fluency", "Eng_decoding", "Eng_fig_lang", "Eng_read_detail",
    "Eng_narr_struct", "Eng_draw_concl", "Eng_read_aloud", "Eng_expr",
    "Math_mult_div", "Math_fractions", "Math_decimals", "Math_time", "Math_place_val",
    "Math_measure", "Math_geometry", "Math_add_sub", "Math_word_prob"
]

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ADHD Prediction</title>
        </head>
        <body>
            <h1>ADHD Prediction</h1>
            <form id="predictionForm">
                <!-- Dynamically generate all input fields -->
                {% for feature in FEATURES %}
                    <label for="{{ feature }}">{{ feature.replace('_', ' ') }}:</label>
                    <input type="number" id="{{ feature }}" name="{{ feature }}" required><br><br>
                {% endfor %}
                <button type="submit">Predict</button>
            </form>
            <h2 id="result"></h2>

            <script>
                document.getElementById('predictionForm').addEventListener('submit', function(event) {
                    event.preventDefault();
                    const formData = new FormData(event.target);
                    const data = {};
                    formData.forEach((value, key) => data[key] = parseFloat(value));

                    fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        const resultContainer = document.getElementById('result');
                        if (result.prediction === "ADHD") {
                            resultContainer.textContent = "Your child may have possible ADHD, please seek a GP appointment at the earliest convenience. This is not an official medical advice.";
                        } else {
                            resultContainer.textContent = "Your child is not detected with ADHD, however this is not an official medical advice, please seek GP appointment if you are still worried.";
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });
            </script>
        </body>
        </html>
    ''', FEATURES=FEATURES)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Ensure all features are present in the data
    for feature in FEATURES:
        if feature not in data:
            data[feature] = 0  # Default value for missing features

    # Convert to DataFrame
    student_data = pd.DataFrame([data])

    # Scale data
    student_data_scaled = scaler.transform(student_data)

    # Extract features using RBM
    student_features = extract_features(student_data_scaled, rbm)
    student_tensor = torch.from_numpy(student_features).float()

    # Predict using FNN
    fnn.eval()
    with torch.no_grad():
        prediction = fnn(student_tensor).item()

    # Determine ADHD status
    result = "ADHD" if prediction >= 0.5 else "No ADHD"
    return jsonify({'prediction': result})

# Authenticate ngrok with your token
ngrok.set_auth_token('2r9HqEPxylu1Ah6fPvv1nCAPFfc_47SPYpuiP3r7eB3HcpWNh')

# Start ngrok tunnel
public_url = ngrok.connect(5000)
print(f" * ngrok URL: {public_url}")

# Run the Flask app
app.run(debug=True, use_reloader=False)