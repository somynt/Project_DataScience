# -*- coding: utf-8 -*-
"""Project_Part_1_dataset.ipynb

Original file is located at
    https://colab.research.google.com/drive/1xYQCvfeD54difa6MDnakhj-SyB0cONCK

Introduction:

This script generates simulated student data, including ADHD status,academic marks, and behavioral assessments.

It includes functions to create truncated normal distributions, add label noise, generate student data, and plot the results. The data can be saved to an Excel
file for further analysis.



•	random: Provides random number generation functions.

•	pandas as pd: Importing pandas library for data manipulation and analysis, aliased as pd.

•	numpy as np: Importing numpy library for numerical operations, aliased as np.

•	from scipy.stats import truncnorm, skew, kurtosis: Importing specific statistical functions from the SciPy library.

•	truncnorm: Truncated normal distribution.

•	skew: Function to calculate skewness.

•	kurtosis: Function to calculate kurtosis.

•	import matplotlib.pyplot as plt: Importing Matplotlib for plotting, aliased as plt.

•	import seaborn as sns: Importing Seaborn for statistical data visualisation.
"""

import random
import pandas as pd
import numpy as np
from scipy.stats import truncnorm, skew, kurtosis
import matplotlib.pyplot as plt
import seaborn as sns

"""•	This function returns a truncated normal distribution object.

•	mean: Mean of the distribution.

•	stddev: Standard deviation of the distribution.

•	low: Lower bound of the distribution (default is 0).

•	upp: Upper bound of the distribution (default is 100).

•	The distribution is truncated to be within the range [low, upp].

"""

def get_truncated_normal(mean, stddev, low=0, upp=100):
    """
    Create a truncated normal distribution.

    Parameters:
        mean (float): Mean of the distribution.
        stddev (float): Standard deviation of the distribution.
        low (float): Lower bound of the distribution.
        upp (float): Upper bound of the distribution.

    Returns:
        scipy.stats._distn_infrastructure.rv_frozen: Truncated normal distribution.
    """
    return truncnorm((low - mean) / stddev, (upp - mean) / stddev,
                     loc=mean, scale=stddev)

"""Function to Add Noise To the data

•	data: List of dictionaries representing student data.

•	noise_percentage: Percentage of labels to flip (default is 2%).

•	num_flips: Number of labels to flip.

•	flip_indices: Randomly chosen indices to flip the labels.

•	The function flips the is_adhd status for randomly chosen students.

"""

def add_label_noise(data, noise_percentage=0.02):
    """
    Add label noise to ADHD status.

    Parameters:
        data (list of dict): List of student data dictionaries.
        noise_percentage (float): Percentage of labels to flip.

    Returns:
        list of dict: Updated list of student data dictionaries.
    """
    num_flips = int(len(data) * noise_percentage)
    flip_indices = random.sample(range(len(data)), num_flips)
    for idx in flip_indices:
        data[idx]["is_adhd"] = not data[idx]["is_adhd"]
    return data

"""Function To Generate Student Data

Generates data for num_students students.

adhd_percentage: Percentage of students with ADHD (default is 10%).

noise_percentage: Percentage of noise to add to labels (default is 2%).

Calls various functions to generate responses and marks.

Combines the generated data into a dictionary for each student.

Adds label noise and converts the data to a DataFrame.
Shuffles the DataFrame and returns it.
"""

def generate_student_data(num_students, adhd_percentage=0.10,
                          noise_percentage=0.02):
    """
    Generate student data.

    Parameters:
        num_students (int): Number of students to generate data for.
        adhd_percentage (float): Percentage of students with ADHD.
        noise_percentage (float): Percentage of label noise.

    Returns:
        pd.DataFrame: DataFrame containing generated student data.
    """
    data = []
    for i in range(num_students):
        is_adhd = random.random() < adhd_percentage
        parent_responses = generate_vanderbilt_parent_responses(is_adhd)
        teacher_responses = generate_vanderbilt_teacher_responses(is_adhd)
        reading_marks = generate_reading_marks(is_adhd)
        math_marks = generate_math_marks(is_adhd)

        combined_data = {
            "student_id": i + 1,
            "is_adhd": is_adhd,
            **parent_responses,
            **teacher_responses,
            **reading_marks,
            **math_marks
        }

        combined_data.update(calculate_individual_stats(reading_marks,
                                                        math_marks))

        data.append(combined_data)

    data = add_label_noise(data, noise_percentage)
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True)
    return df

"""Function to Generate Reading Marks

•	Generates reading marks based on ADHD status.

•	Different means and standard deviations for students with and without ADHD.

•	Generates marks for different difficulty levels of reading topics.

•	Returns a dictionary of marks.


"""

def generate_reading_marks(is_adhd):
    """
    Generate reading marks.

    Parameters:
        is_adhd (bool): Whether the student has ADHD.

    Returns:
        dict: Dictionary of reading marks for different topics.
    """
    marks = {}
    if is_adhd:
        high_difficulty_mean, high_difficulty_stddev = 25, 20
        moderate_difficulty_mean, moderate_difficulty_stddev = 35, 20
        low_moderate_difficulty_mean, low_moderate_difficulty_stddev = 45, 20
        low_difficulty_mean, low_difficulty_stddev = 55, 20
    else:
        high_difficulty_mean, high_difficulty_stddev = 65, 20
        moderate_difficulty_mean, moderate_difficulty_stddev = 75, 20
        low_moderate_difficulty_mean, low_moderate_difficulty_stddev = 85, 20
        low_difficulty_mean, low_difficulty_stddev = 95, 20

    high_difficulty = ["Eng_read_comp", "Eng_vocab_dev"]
    moderate_difficulty = ["Eng_fluency", "Eng_decoding", "Eng_fig_lang",
                           "Eng_read_detail", "Eng_narr_struct"]
    low_moderate_difficulty = ["Eng_draw_concl"]
    low_difficulty = ["Eng_read_aloud", "Eng_expr"]

    for topic in high_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            high_difficulty_mean, high_difficulty_stddev).rvs()))
    for topic in moderate_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            moderate_difficulty_mean, moderate_difficulty_stddev).rvs()))
    for topic in low_moderate_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            low_moderate_difficulty_mean, low_moderate_difficulty_stddev).rvs()))
    for topic in low_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            low_difficulty_mean, low_difficulty_stddev).rvs()))

    return marks

"""Function to Generate Maths Marks

•	Similar to generate_reading_marks, but for math marks.

•	Generates math marks based on ADHD status and difficulty levels.

•	Returns a dictionary of marks.

"""

def generate_math_marks(is_adhd):
    """
    Generate math marks.

    Parameters:
        is_adhd (bool): Whether the student has ADHD.

    Returns:
        dict: Dictionary of math marks for different topics.
    """
    marks = {}
    if is_adhd:
        high_difficulty_mean, high_difficulty_stddev = 25, 20
        moderate_difficulty_mean, moderate_difficulty_stddev = 35, 20
        low_difficulty_mean, low_difficulty_stddev = 45, 20
    else:
        high_difficulty_mean, high_difficulty_stddev = 65, 20
        moderate_difficulty_mean, moderate_difficulty_stddev = 75, 20
        low_difficulty_mean, low_difficulty_stddev = 85, 20

    high_difficulty = ["Math_mult_div", "Math_fractions", "Math_decimals"]
    moderate_difficulty = ["Math_time", "Math_place_val", "Math_measure",
                           "Math_geometry"]
    low_difficulty = ["Math_add_sub", "Math_word_prob"]

    for topic in high_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            high_difficulty_mean, high_difficulty_stddev).rvs()))
    for topic in moderate_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            moderate_difficulty_mean, moderate_difficulty_stddev).rvs()))
    for topic in low_difficulty:
        marks[topic] = round(max(10, get_truncated_normal(
            low_difficulty_mean, low_difficulty_stddev).rvs()))

    return marks

"""Function To Generate Vanderbilt Parent Scale Responses

•	Generates Vanderbilt Parent Assessment Scale responses based on ADHD status.

•	Different questions: Inattention, Hyperactivity, Oppositional Defiant Disorder (ODD), Conduct Disorder (CD), Anxiety, School Performance, and Social Function.

•	Returns a dictionary of responses.

"""

def generate_vanderbilt_parent_responses(is_adhd):
    """
    Generate Vanderbilt Parent Assessment Scale responses.

    Parameters:
        is_adhd (bool): Whether the student has ADHD.

    Returns:
        dict: Dictionary of parent assessment responses.
    """
    responses = {}
    normal_dist = get_truncated_normal(mean=1.5, stddev=0.5, low=0, upp=3)
    for i in range(9):
        responses[f"parent_inatt_q{i + 1}"] = round(normal_dist.rvs() +
                                                    (1 if is_adhd else 0))
    for i in range(9):
        responses[f"parent_hyper_q{i + 1}"] = round(normal_dist.rvs() +
                                                    (1 if is_adhd else 0))
    for i in range(8):
        responses[f"parent_odd_q{i + 1}"] = round(normal_dist.rvs())
    for i in range(14):
        responses[f"parent_cd_q{i + 1}"] = round(normal_dist.rvs())
    for i in range(7):
        responses[f"parent_anx_q{i + 1}"] = round(normal_dist.rvs())
    for i in range(3):
        responses[f"parent_sch_perf_q{i + 1}"] = round(normal_dist.rvs() +
                                                       (2 if is_adhd else 0))
    for i in range(3):
        responses[f"parent_soc_func_q{i + 1}"] = round(normal_dist.rvs() +
                                                       (2 if is_adhd else 0))
    return responses

"""Function To Generate Vanderbilt Teacher Scale Responses

• Generates Vanderbilt Teacher Assessment Scale responses based on ADHD status.

• Different questions: Inattention, Hyperactivity, Oppositional Defiant Disorder (ODD), Conduct Disorder (CD), Anxiety, School Performance, and Social Function.

• Returns a dictionary of responses.
"""

def generate_vanderbilt_teacher_responses(is_adhd):
    """
    Generate Vanderbilt Teacher Assessment Scale responses.

    Parameters:
        is_adhd (bool): Whether the student has ADHD.

    Returns:
        dict: Dictionary of teacher assessment responses.
    """
    responses = {}
    normal_dist = get_truncated_normal(mean=1.5, stddev=0.5, low=0, upp=3)
    for i in range(9):
        responses[f"teacher_inatt_q{i + 1}"] = round(normal_dist.rvs() +
                                                     (1 if is_adhd else 0))
    for i in range(9):
        responses[f"teacher_hyper_q{i + 1}"] = round(normal_dist.rvs() +
                                                     (1 if is_adhd else 0))
    for i in range(8):
        responses[f"teacher_odd_q{i + 1}"] = round(normal_dist.rvs())
    for i in range(14):
        responses[f"teacher_cd_q{i + 1}"] = round(normal_dist.rvs())
    for i in range(7):
        responses[f"teacher_anx_q{i + 1}"] = round(normal_dist.rvs())
    for i in range(3):
        responses[f"teacher_sch_perf_q{i + 1}"] = round(normal_dist.rvs() +
                                                        (2 if is_adhd else 0))
    for i in range(3):
        responses[f"teacher_soc_func_q{i + 1}"] = round(normal_dist.rvs() +
                                                        (2 if is_adhd else 0))
    return responses

"""Function to Calculate Individual Statistics for English and Math Scores

•	Calculates statistics (mean, standard deviation, skewness, kurtosis) for English and Math scores.

•	Returns a dictionary of calculated statistics.

"""

def calculate_individual_stats(reading_marks, math_marks):
    """
    Calculate individual statistics for English and Math scores.

    Parameters:
        reading_marks (dict): Dictionary of reading marks.
        math_marks (dict): Dictionary of math marks.

    Returns:
        dict: Dictionary of calculated statistics.
    """
    english_scores = list(reading_marks.values())
    math_scores = list(math_marks.values())

    stats = {
        "english_mean": np.mean(english_scores),
        "english_std": np.std(english_scores),
        "english_skew": skew(english_scores),
        "english_kurtosis": kurtosis(english_scores),
        "math_mean": np.mean(math_scores),
        "math_std": np.std(math_scores),
        "math_skew": skew(math_scores),
        "math_kurtosis": kurtosis(math_scores)
    }
    return stats

"""Function to plot Average Response Curve and Bar charts

•	Plots average response curves and bar charts for ADHD and Non-ADHD groups.

•	Uses Seaborn and Matplotlib for visualisation.

•	Adds labels to bars dynamically based on their width.

"""

def plot_average_response_and_distribution(df, columns, title, ax):
    """
    Plot average response curves and bar charts.

    Parameters:
        df (pd.DataFrame): DataFrame containing student data.
        columns (list): List of column names to plot.
        title (str): Title of the plot.
        ax (matplotlib.axes.Axes): Axes object to plot on.
    """
    sns.set(style="whitegrid")

    adhd_avg = df[df['is_adhd'] == True][columns].mean()
    non_adhd_avg = df[df['is_adhd'] == False][columns].mean()

    index = np.arange(len(columns))
    bar_width = 0.35

    bars1 = ax.barh(index, adhd_avg, bar_width, label='ADHD', color='blue',
                    alpha=0.6, edgecolor='black')
    bars2 = ax.barh(index + bar_width, non_adhd_avg, bar_width,
                    label='Non-ADHD', color='orange', alpha=0.6,
                    edgecolor='black')

    ax.set_title(title, fontsize=20)
    ax.set_xlabel("Average Score", fontsize=18)
    ax.set_yticks(index + bar_width / 2)
    ax.set_yticklabels(columns, fontsize=14)
    ax.legend(title="Group", loc='upper left', fontsize=14,
              bbox_to_anchor=(1, 1))
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    for bars in [bars1, bars2]:
        for bar in bars:
            label_position = bar.get_width() + 0.02 * max(adhd_avg.max(),
                                                          non_adhd_avg.max())
            ax.text(label_position, bar.get_y() + bar.get_height() / 2,
                    f'{bar.get_width():.1f}',
                    va='center', ha='left', fontsize=14, color='black')

"""



> Main Function - Produces data as an excel file, and Various Plots



"""

if __name__ == "__main__":
    num_students = 10000
    adhd_percentage = 0.10  # Increased ADHD percentage to 10%
    noise_percentage = 0.02  # Reduced noise percentage to 2%

    df = generate_student_data(num_students, adhd_percentage=adhd_percentage,
                               noise_percentage=noise_percentage)

    df.to_excel("student_data_non_normalized.xlsx", index=False)
    print("Student data generated and saved to student_data_non_normalized.xlsx")

    parent_columns = [f'parent_inatt_q{i + 1}' for i in range(9)] + \
                     [f'parent_hyper_q{i + 1}' for i in range(9)] + \
                     [f'parent_odd_q{i + 1}' for i in range(8)] + \
                     [f'parent_cd_q{i + 1}' for i in range(14)] + \
                     [f'parent_anx_q{i + 1}' for i in range(7)] + \
                     [f'parent_sch_perf_q{i + 1}' for i in range(3)] + \
                     [f'parent_soc_func_q{i + 1}' for i in range(3)]
    teacher_columns = [f'teacher_inatt_q{i + 1}' for i in range(9)] + \
                      [f'teacher_hyper_q{i + 1}' for i in range(9)] + \
                      [f'teacher_odd_q{i + 1}' for i in range(8)] + \
                      [f'teacher_cd_q{i + 1}' for i in range(14)] + \
                      [f'teacher_anx_q{i + 1}' for i in range(7)] + \
                      [f'teacher_sch_perf_q{i + 1}' for i in range(3)] + \
                      [f'teacher_soc_func_q{i + 1}' for i in range(3)]
    english_columns = ["Eng_read_comp", "Eng_vocab_dev", "Eng_fluency",
                       "Eng_decoding", "Eng_fig_lang", "Eng_read_detail",
                       "Eng_narr_struct", "Eng_draw_concl", "Eng_read_aloud",
                       "Eng_expr"]
    math_columns = ["Math_mult_div", "Math_fractions", "Math_decimals",
                    "Math_time", "Math_place_val", "Math_measure",
                    "Math_geometry", "Math_add_sub", "Math_word_prob"]

    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 24))
    fig2, ax2 = plt.subplots(1, 1, figsize=(18, 24))
    fig3, axs3 = plt.subplots(2, 1, figsize=(18, 24))

    plot_average_response_and_distribution(
        df, parent_columns,
        ("Average Parental Scores and Distribution for ADHD and "
         "Non-ADHD Students"), ax1)
    plot_average_response_and_distribution(
        df, teacher_columns,
        ("Average Teacher Scores and Distribution for ADHD and "
         "Non-ADHD Students"), ax2)
    plot_average_response_and_distribution(
        df, english_columns,
        ("Average English Scores and Distribution for ADHD and "
         "Non-ADHD Students"), axs3[0])
    plot_average_response_and_distribution(
        df, math_columns,
        ("Average Math Scores and Distribution for ADHD and "
         "Non-ADHD Students"), axs3[1])

    fig1.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()

    fig1.savefig('parent_bar_chart.png', dpi=300, bbox_inches='tight')
    fig2.savefig('teacher_bar_chart.png', dpi=300, bbox_inches='tight')
    fig3.savefig('english_math_bar_charts.png', dpi=300, bbox_inches='tight')

    plt.show()

    print("\nLabel Expansions:")
    print("Eng_read_comp: English Reading Comprehension")
    print("Eng_vocab_dev: English Vocabulary Development")
    print("Eng_fluency: English Fluency")
    print("Eng_decoding: English Decoding")
    print("Eng_fig_lang: English Figurative Language")
    print("Eng_read_detail: English Reading for Detail")
    print("Eng_narr_struct: English Understanding Narrative Structure")
    print("Eng_draw_concl: English Drawing Conclusions")
    print("Eng_read_aloud: English Reading Aloud")
    print("Eng_expr: English Expression")
    print("Math_mult_div: Maths Multiplication Division")
    print("Math_fractions: Maths Fractions")
    print("Math_decimals: Maths Decimals")
    print("Math_time: Maths Time")
    print("Math_place_val: Maths Place Value")
    print("Math_measure: Maths Measurement")
    print("Math_geometry: Maths Geometry")
    print("Math_add_sub: Maths Addition Subtraction")
    print("Math_word_prob: Maths Word Problems")
    print("parent_inatt_q: Parent Inattention Question")
    print("parent_hyper_q: Parent Hyperactivity Question")
    print("parent_odd_q: Parent Oppositional Defiant Disorder Question")
    print("parent_cd_q: Parent Conduct Disorder Question")
    print("parent_anx_q: Parent Anxiety Question")
    print("parent_sch_perf_q: Parent School Performance Question")
    print("parent_soc_func_q: Parent Social Function Question")
    print("teacher_inatt_q: Teacher Inattention Question")
    print("teacher_hyper_q: Teacher Hyperactivity Question")
    print("teacher_odd_q: Teacher Oppositional Defiant Disorder Question")
    print("teacher_cd_q: Teacher Conduct Disorder Question")
    print("teacher_anx_q: Teacher Anxiety Question")
    print("teacher_sch_perf_q: Teacher School Performance Question")
    print("teacher_soc_func_q: Teacher Social Function Question")
