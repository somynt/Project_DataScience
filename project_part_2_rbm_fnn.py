# -*- coding: utf-8 -*-
"""Project_Part_2_RBM_FNN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NpbdJF5MsgzV4s-iyC3g7r2O1Ny1xyE3

Explanation for Each Section

Data Loading and Preprocessing:

The dataset is loaded from an Excel file and features (X) and the target variable (y) are separated.
The data is split into training and test sets using train_test_split.
Numerical features are normalised using StandardScaler.

RBM Class:

The RBM class is defined to implement the Restricted Boltzmann Machine for feature extraction.
The class includes methods for sampling hidden units given visible units, sampling visible units given hidden units, performing Gibbs sampling, and training the RBM.

FNN Class:

The FNN class is defined to implement a Feedforward Neural Network for classification.
The class includes methods for initializing the network and performing the forward pass.
Training Functions:

The train_fnn function trains the FNN model using the provided DataLoader.
The prepare_dataloader function prepares data for PyTorch DataLoader.

Grid Search and Cross-Validation:

A grid search over different n_hidden values is performed using K-Fold Cross-Validation.
The average validation accuracies for each n_hidden value are calculated and plotted.

Final Training and Evaluation:

The RBM and FNN are trained on the full training set using the optimal n_hidden value.
The trained models and scaler are saved.
The FNN is evaluated on the test set, and various performance metrics are calculated and displayed.
The ROC curve and confusion matrix are plotted.
Comparison with Original Features:

The FNN is also trained and evaluated on the original scaled features.

The performance of models using RBM features is compared with models using original features to determine if RBM improves performance.
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, roc_curve,
                             confusion_matrix, ConfusionMatrixDisplay)
import joblib

# Load the dataset
data = pd.read_excel('/content/drive/MyDrive/Project_ADHD/'
                     'student_data_ADHD.xlsx')

# Separate features and target variable
X = data.drop('is_adhd', axis=1)  # Features
y = data['is_adhd']  # Target variable

# Initial train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Normalize numerical features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


class RBM(nn.Module):
    """
    Restricted Boltzmann Machine (RBM) class for feature extraction.
    """

    def __init__(self, n_visible, n_hidden):
        """
        Initialize the RBM model with visible and hidden units.

        Parameters:
        n_visible (int): Number of visible units.
        n_hidden (int): Number of hidden units.
        """
        super(RBM, self).__init__()
        self.W = nn.Parameter(torch.randn(n_visible, n_hidden) * 0.01)
        self.v_bias = nn.Parameter(torch.zeros(n_visible))
        self.h_bias = nn.Parameter(torch.zeros(n_hidden))

    def sample_h_given_v(self, v):
        """
        Sample hidden units given visible units.

        Parameters:
        v (torch.Tensor): Visible units.

        Returns:
        torch.Tensor: Sampled hidden units.
        """
        activation = torch.matmul(v, self.W) + self.h_bias
        prob_h_given_v = torch.sigmoid(activation)
        sample_h = torch.bernoulli(prob_h_given_v)
        return sample_h

    def sample_v_given_h(self, h):
        """
        Sample visible units given hidden units.

        Parameters:
        h (torch.Tensor): Hidden units.

        Returns:
        torch.Tensor: Sampled visible units.
        """
        activation = torch.matmul(h, self.W.t()) + self.v_bias
        prob_v_given_h = torch.sigmoid(activation)
        sample_v = torch.bernoulli(prob_v_given_h)
        return sample_v

    def gibbs_step(self, v):
        """
        Perform one step of Gibbs sampling.

        Parameters:
        v (torch.Tensor): Visible units.

        Returns:
        torch.Tensor: Updated visible units after Gibbs sampling.
        """
        h_prob = self.sample_h_given_v(v)
        v_prob = self.sample_v_given_h(h_prob)
        h_prob = self.sample_h_given_v(v_prob)
        return v_prob

    def train_step(self, v_data):
        """
        Perform one training step.

        Parameters:
        v_data (torch.Tensor): Visible data.
        """
        v_pos = v_data
        h_pos = self.sample_h_given_v(v_pos)
        v_neg = self.gibbs_step(v_pos)

        positive_hidden = torch.matmul(v_pos.t(), h_pos)
        negative_hidden = torch.matmul(v_neg.t(),
                                       self.sample_h_given_v(v_neg))

        positive_visible = torch.mean(v_pos, dim=0)
        negative_visible = torch.mean(v_neg, dim=0)

        positive_hidden_bias = torch.mean(h_pos, dim=0)
        negative_hidden_bias = torch.mean(
            self.sample_h_given_v(v_neg), dim=0)

        batch_size = v_data.size(0)
        self.W.data += (positive_hidden - negative_hidden) / batch_size
        self.v_bias.data += positive_visible - negative_visible
        self.h_bias.data += positive_hidden_bias - negative_hidden_bias

    def train(self, v_data, epochs=10, learning_rate=0.1, batch_size=10):
        """
        Train the RBM model.

        Parameters:
        v_data (torch.Tensor): Visible data.
        epochs (int): Number of training epochs.
        learning_rate (float): Learning rate.
        batch_size (int): Batch size.
        """
        optimizer = optim.SGD(self.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            for i in range(0, len(v_data), batch_size):
                batch = v_data[i:i+batch_size]
                self.train_step(batch)


def extract_features(v_data, rbm):
    """
    Extract features using the trained RBM.

    Parameters:
    v_data (np.array): Visible data.
    rbm (RBM): Trained RBM model.

    Returns:
    np.array: Extracted features.
    """
    h_prob = rbm.sample_h_given_v(torch.from_numpy(v_data).float())
    return h_prob.detach().numpy()


class FNN(nn.Module):
    """
    Feedforward Neural Network (FNN) class for classification.
    """

    def __init__(self, input_dim):
        """
        Initialize the FNN model.

        Parameters:
        input_dim (int): Input dimension.
        """
        super(FNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        """
        Forward pass of the FNN model.

        Parameters:
        x (torch.Tensor): Input data.

        Returns:
        torch.Tensor: Output data.
        """
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x


def train_fnn(model, criterion, optimizer, dataloader, num_epochs=10):
    """
    Train the FNN model.

    Parameters:
    model (FNN): FNN model.
    criterion (nn.Module): Loss function.
    optimizer (optim.Optimizer): Optimizer.
    dataloader (torch.utils.data.DataLoader): DataLoader for training data.
    num_epochs (int): Number of training epochs.
    """
    model.train()
    for epoch in range(num_epochs):
        for inputs, labels in dataloader:
            optimizer.zero_grad()  # Clear gradients
            outputs = model(inputs)  # Forward pass
            loss = criterion(outputs.squeeze(), labels.float())  # Compute loss
            loss.backward()  # Backward pass (compute gradients)
            optimizer.step()  # Update weights
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')


def prepare_dataloader(X, y, batch_size=32):
    """
    Prepare data for PyTorch DataLoader.

    Parameters:
    X (np.array): Feature data.
    y (np.array or pd.Series): Target data.
    batch_size (int): Batch size.

    Returns:
    torch.utils.data.DataLoader: DataLoader for the data.
    """
    # Convert pandas Series to numpy array if necessary
    if isinstance(y, pd.Series):
        y = y.values
    dataset = torch.utils.data.TensorDataset(torch.from_numpy(X).float(),
                                             torch.from_numpy(y).float())
    return torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                       shuffle=True)

# Grid search over different n_hidden values with K-Fold Cross-Validation
n_hidden_values = [32, 64, 128, 256, 512]
kf = KFold(n_splits=5, shuffle=True, random_state=42)
val_accuracies = {n_hidden: [] for n_hidden in n_hidden_values}

# Perform K-Fold Cross-Validation
for n_hidden in n_hidden_values:
    for train_index, val_index in kf.split(X_train_scaled, y_train):
        X_train_fold = X_train_scaled[train_index]
        X_val_fold = X_train_scaled[val_index]
        y_train_fold = y_train.iloc[train_index]
        y_val_fold = y_train.iloc[val_index]

        rbm = RBM(n_visible=X_train_scaled.shape[1], n_hidden=n_hidden)
        rbm.train(torch.from_numpy(X_train_fold).float(), epochs=10)

        X_train_rbm = extract_features(X_train_fold, rbm)
        X_val_rbm = extract_features(X_val_fold, rbm)

        train_loader_rbm = prepare_dataloader(X_train_rbm, y_train_fold)
        val_loader_rbm = prepare_dataloader(X_val_rbm, y_val_fold)

        fnn = FNN(input_dim=n_hidden)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(fnn.parameters(), lr=0.001)

        train_fnn(fnn, criterion, optimizer, train_loader_rbm, num_epochs=10)

        # Evaluate on validation set
        fnn.eval()
        val_preds = []
        val_labels = []
        with torch.no_grad():
            for inputs, labels in val_loader_rbm:
                outputs = fnn(inputs)
                preds = outputs.squeeze().round()
                val_preds.extend(preds.numpy())
                val_labels.extend(labels.numpy())

        val_acc = accuracy_score(val_labels, val_preds)
        val_accuracies[n_hidden].append(val_acc)
        print(f'n_hidden = {n_hidden}, Fold Validation Accuracy: {val_acc:.4f}')

# Average validation accuracies for each n_hidden value
avg_val_accuracies = {n_hidden: np.mean(accs) for n_hidden, accs in
                      val_accuracies.items()}

# Plotting the results
n_hidden_list = list(avg_val_accuracies.keys())
avg_val_acc_list = list(avg_val_accuracies.values())

plt.plot(n_hidden_list, avg_val_acc_list, marker='o')
plt.xlabel('Number of Hidden Units (n_hidden)')
plt.ylabel('Average Validation Accuracy')
plt.title('Average Validation Accuracy vs. Number of Hidden Units in RBM')
plt.grid(True)
plt.show()

# Find the optimal n_hidden value
optimal_n_hidden = max(avg_val_accuracies, key=avg_val_accuracies.get)
print(f'Optimal n_hidden value: {optimal_n_hidden}')

# Final training on the full training set with the optimal n_hidden
rbm = RBM(n_visible=X_train_scaled.shape[1], n_hidden=optimal_n_hidden)
rbm.train(torch.from_numpy(X_train_scaled).float(), epochs=10)

X_train_rbm = extract_features(X_train_scaled, rbm)
X_test_rbm = extract_features(X_test_scaled, rbm)

train_loader_rbm = prepare_dataloader(X_train_rbm, y_train)
test_loader_rbm = prepare_dataloader(X_test_rbm, y_test)

fnn = FNN(input_dim=optimal_n_hidden)
criterion = nn.BCELoss()
optimizer = optim.Adam(fnn.parameters(), lr=0.001)

train_fnn(fnn, criterion, optimizer, train_loader_rbm, num_epochs=10)

# Save the trained models and scaler
torch.save(rbm.state_dict(), '/content/drive/MyDrive/Project_ADHD/'
                             'rbm_model.pth')
torch.save(fnn.state_dict(), '/content/drive/MyDrive/Project_ADHD/'
                             'fnn_model.pth')
joblib.dump(scaler, '/content/drive/MyDrive/Project_ADHD/scaler.pkl')

print("Models and scaler saved successfully!")

# Evaluate on the test set
fnn.eval()
test_preds = []
test_labels = []
test_probs = []  # For AUC calculation
with torch.no_grad():
    for inputs, labels in test_loader_rbm:
        outputs = fnn(inputs)
        preds = outputs.squeeze().round()
        probs = outputs.squeeze()  # For AUC calculation
        test_preds.extend(preds.numpy())
        test_labels.extend(labels.numpy())
        test_probs.extend(probs.numpy())

test_acc = accuracy_score(test_labels, test_preds)
test_precision = precision_score(test_labels, test_preds)
test_recall = recall_score(test_labels, test_preds)
test_f1 = f1_score(test_labels, test_preds)
test_auc = roc_auc_score(test_labels, test_probs)

print(f"\nTest Results with Optimal n_hidden = {optimal_n_hidden}:")
print(f"Accuracy: {test_acc:.2f}")
print(f"Precision: {test_precision:.2f}")
print(f"Recall: {test_recall:.2f}")
print(f"F1-score: {test_f1:.2f}")
print(f"AUC: {test_auc:.2f}")

# Plot ROC curve
fpr, tpr, _ = roc_curve(test_labels, test_probs)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2,
         label='ROC curve (area = %0.2f)' % test_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Plot confusion matrix
cm = confusion_matrix(test_labels, test_preds)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap=plt.cm.Blues)
plt.title('Confusion Matrix')
plt.show()

# Compare the performance of models with RBM features and original features
print("\nEvaluating on original features for comparison:")

# Prepare original data for PyTorch
train_loader_orig = prepare_dataloader(X_train_scaled, y_train)
test_loader_orig = prepare_dataloader(X_test_scaled, y_test)

# Train FNN on original features
fnn_orig = FNN(input_dim=X_train_scaled.shape[1])
criterion = nn.BCELoss()
optimizer = optim.Adam(fnn_orig.parameters(), lr=0.001)

train_fnn(fnn_orig, criterion, optimizer, train_loader_orig, num_epochs=10)

# Evaluate on the test set with original features
fnn_orig.eval()
test_preds_orig = []
test_labels_orig = []
test_probs_orig = []  # For AUC calculation
with torch.no_grad():
    for inputs, labels in test_loader_orig:
        outputs = fnn_orig(inputs)
        preds = outputs.squeeze().round()
        probs = outputs.squeeze()  # For AUC calculation
        test_preds_orig.extend(preds.numpy())
        test_labels_orig.extend(labels.numpy())
        test_probs_orig.extend(probs.numpy())

test_acc_orig = accuracy_score(test_labels_orig, test_preds_orig)
test_precision_orig = precision_score(test_labels_orig, test_preds_orig)
test_recall_orig = recall_score(test_labels_orig, test_preds_orig)
test_f1_orig = f1_score(test_labels_orig, test_preds_orig)
test_auc_orig = roc_auc_score(test_labels_orig, test_probs_orig)

print(f"\nTest Results with Original Features:")
print(f"Accuracy: {test_acc_orig:.2f}")
print(f"Precision: {test_precision_orig:.2f}")
print(f"Recall: {test_recall_orig:.2f}")
print(f"F1-score: {test_f1_orig:.2f}")
print(f"AUC: {test_auc_orig:.2f}")

# Compare the performance of models with RBM features and original features
if test_acc > test_acc_orig:
    print("RBM generated features improve the performance of the model.")
else:
    print("RBM generated features do not improve the performance of the model.")