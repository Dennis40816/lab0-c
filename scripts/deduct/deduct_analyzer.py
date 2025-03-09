#!/usr/bin/env python3
"""
This script parses the deduct.log file and plots the combined CDF, histogram,
and KDE of the execution time distribution for each test type.

Each test block in the log is separated by a header line like:
    TestType: insert_tail, TestNum: 0
Following header lines are data lines in CSV format (without header row):
    12345,0
    12346,1
    ...

The script will merge data from the same test type and produce one set of plots per type.
Plots will be limited to the execution time range [0, 1000] with bins of width 100,
and for the CDF plot the data will be overlaid for class 0 and class 1.
Output images are saved in the "picture/" folder.
"""

import re
import os
import numpy as np
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns  # For KDE plotting

# Set region and bins
X_MIN = 0
X_MAX = 1000
BIN_WIDTH = 100
BINS = np.arange(X_MIN, X_MAX + BIN_WIDTH, BIN_WIDTH)  # Bin edges

def parse_log(file_path):
    """
    Parse the log file into a dictionary.
    Each key is a test_type (e.g., "insert_head") and the value is a list of
    DataFrames, each containing columns 'ExecutionTime' and 'Class'.
    """
    tests = {}  # dictionary: test_type -> list of DataFrame
    current_test = None
    data_lines = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Detect header line starting with "TestType:"
            if line.startswith("TestType:"):
                # If previous test block exists, save its data
                if current_test is not None and data_lines:
                    df = pd.read_csv(StringIO("\n".join(data_lines)),
                                     header=None,
                                     names=['ExecutionTime', 'Class'])
                    tests.setdefault(current_test['test_type'], []).append(df)
                    data_lines = []
                # Parse header, e.g., "TestType: insert_head, TestNum: 0"
                m = re.match(r"TestType:\s*(\S+),\s*TestNum:\s*(\d+)", line)
                if m:
                    test_type = m.group(1)
                    test_num = int(m.group(2))
                    current_test = {'test_type': test_type, 'test_num': test_num}
            elif line.startswith("ExecutionTime"):
                # Skip the column header line from the log
                continue
            elif line == "":
                # Blank line indicates end of current test block.
                continue
            else:
                # Data row
                data_lines.append(line)
        # Save the last test block if exists
        if current_test is not None and data_lines:
            df = pd.read_csv(StringIO("\n".join(data_lines)),
                             header=None,
                             names=['ExecutionTime', 'Class'])
            tests.setdefault(current_test['test_type'], []).append(df)
    return tests

def plot_combined_cdf_and_histogram(test_type, df_list):
    """
    Combine multiple DataFrames (from different test iterations) into one,
    and then plot the CDF and histogram of the 'ExecutionTime' column.
    The plots are limited to the execution time range [0, 1000] and are separated by class.
    """
    # Concatenate all DataFrames for the same test_type
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Ensure the column names are as expected
    if 'ExecutionTime' not in combined_df.columns:
        combined_df.columns = [col.strip() for col in combined_df.columns]
    if 'ExecutionTime' not in combined_df.columns:
        raise KeyError("Column 'ExecutionTime' not found in the data.")

    # Convert columns to numeric
    combined_df['ExecutionTime'] = pd.to_numeric(combined_df['ExecutionTime'], errors='coerce')
    combined_df['Class'] = pd.to_numeric(combined_df['Class'], errors='coerce')

    # Filter data to the specified range [X_MIN, X_MAX]
    combined_df = combined_df[(combined_df['ExecutionTime'] >= X_MIN) & (combined_df['ExecutionTime'] <= X_MAX)]

    # Create output folder if not exists
    out_dir = "picture"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Separate data by class: Class 0 and Class 1
    df_class0 = combined_df[combined_df['Class'] == 0]
    df_class1 = combined_df[combined_df['Class'] == 1]

    # -----------------------------
    # Plot Histogram
    # -----------------------------
    plt.figure()
    plt.hist(df_class0['ExecutionTime'], bins=BINS, alpha=0.5, label='Class 0', edgecolor='black')
    plt.hist(df_class1['ExecutionTime'], bins=BINS, alpha=0.5, label='Class 1', edgecolor='black')
    plt.xlabel("Execution Time")
    plt.ylabel("Frequency")
    plt.title(f"Execution Time Distribution of {test_type}")
    plt.legend()
    plt.grid(True)
    plt.xlim(X_MIN, X_MAX)
    plt.savefig(os.path.join(out_dir, f"hist_{test_type}.png"))
    plt.close()

    # -----------------------------
    # Plot CDF
    # -----------------------------
    plt.figure()
    # Calculate CDF for each class
    for class_val, df_class in zip([0, 1], [df_class0, df_class1]):
        exec_times = np.sort(df_class['ExecutionTime'].values)
        if len(exec_times) == 0:
            continue  # Skip if no data for this class
        cdf = np.arange(1, len(exec_times) + 1) / len(exec_times)
        plt.plot(exec_times, cdf, marker='.', linestyle='none', label=f'Class {class_val}')
    plt.xlabel("Execution Time")
    plt.ylabel("CDF")
    plt.title(f"CDF of {test_type}")
    plt.legend()
    plt.grid(True)
    plt.xlim(X_MIN, X_MAX)
    plt.savefig(os.path.join(out_dir, f"cdf_{test_type}.png"))
    plt.close()

def plot_combined_kde(test_type, df_list):
    """
    Combine multiple DataFrames (from different test iterations) into one,
    and then plot the KDE curves for the 'ExecutionTime' distribution.
    The KDE curves are plotted for Class 0 and Class 1 with a filled area
    and an alpha value of 0.3. The plot is limited to the execution time range [0, 1000].
    """
    # Concatenate all DataFrames for the same test_type
    combined_df = pd.concat(df_list, ignore_index=True)

    # Convert columns to numeric
    combined_df['ExecutionTime'] = pd.to_numeric(combined_df['ExecutionTime'], errors='coerce')
    combined_df['Class'] = pd.to_numeric(combined_df['Class'], errors='coerce')

    # Filter data to the specified range [X_MIN, X_MAX]
    combined_df = combined_df[(combined_df['ExecutionTime'] >= X_MIN) & (combined_df['ExecutionTime'] <= X_MAX)]

    # Separate data by class: Class 0 and Class 1
    df_class0 = combined_df[combined_df['Class'] == 0]
    df_class1 = combined_df[combined_df['Class'] == 1]

    # Create output folder if not exists
    out_dir = "picture"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Plot KDE curves for Class 0 and Class 1 using seaborn
    plt.figure()
    sns.kdeplot(data=df_class0, x='ExecutionTime', fill=True, alpha=0.3, label='Class 0', clip=(X_MIN, X_MAX))
    sns.kdeplot(data=df_class1, x='ExecutionTime', fill=True, alpha=0.3, label='Class 1', clip=(X_MIN, X_MAX))
    plt.xlabel("Execution Time")
    plt.ylabel("Density")
    plt.title(f"KDE of Execution Time for {test_type}")
    plt.legend()
    plt.grid(True)
    plt.xlim(X_MIN, X_MAX)
    plt.savefig(os.path.join(out_dir, f"kde_{test_type}.png"))
    plt.close()

def main():
    log_file = "deduct.log"
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found.")
        return

    tests = parse_log(log_file)
    for test_type, df_list in tests.items():
        total_meas = sum(len(df) for df in df_list)
        print(f"Plotting {test_type}: total measurements = {total_meas}")
        plot_combined_cdf_and_histogram(test_type, df_list)
        # Plot the KDE curves in addition to the histogram and CDF plots.
        plot_combined_kde(test_type, df_list)

if __name__ == '__main__':
    main()
