"""
Shared file locations for the project.

By default everything is read from and written to the folder this file is
in, so the project runs straight after cloning. To use another folder (for
example a Google Drive folder in Colab), set the environment variable
ADHD_PROJECT_DIR before running, e.g.

    import os
    os.environ["ADHD_PROJECT_DIR"] = "/content/drive/MyDrive/Project_ADHD"
"""

import os

PROJECT_DIR = os.environ.get(
    "ADHD_PROJECT_DIR", os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(PROJECT_DIR, "student_data_ADHD.xlsx")
RBM_MODEL_PATH = os.path.join(PROJECT_DIR, "rbm_model.pth")
FNN_MODEL_PATH = os.path.join(PROJECT_DIR, "fnn_model.pth")
SCALER_PATH = os.path.join(PROJECT_DIR, "scaler.pkl")
