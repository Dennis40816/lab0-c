#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_fixed_alloc(logfile="alloc_test_fixed.log"):
    df = pd.read_csv(logfile)
    plt.figure(figsize=(8, 6))
    plt.plot(df["Iteration"], df["Average-Cycles-Per-Allocation"], marker="o", linestyle="-")
    plt.xlabel("Iteration")
    plt.ylabel("Average Cycles per Allocation")
    plt.title("Fixed Allocations: Average Cycles Over Iterations")
    plt.grid(True)
    plt.savefig("picture/alloc_test_fixed_plot.png")
    plt.show()

def analyze_random_allocations(logfile="alloc_test_random.log"):
    # Read the CSV log file
    # Expected header: Iteration, Random-Count, Single-Alloc1-Cycles, Group-Alloc-Cycles, Single-Alloc2-Cycles
    df = pd.read_csv(logfile)

    # 1. Print descriptive statistics for Single-Alloc1-Cycles and Single-Alloc2-Cycles
    print("Single-Alloc1-Cycles Statistics:")
    print(df["Single-Alloc1-Cycles"].describe())
    print("\nSingle-Alloc2-Cycles Statistics:")
    print(df["Single-Alloc2-Cycles"].describe())

    # Calculate skewness for both Single-Alloc1-Cycles and Single-Alloc2-Cycles
    skew1 = df["Single-Alloc1-Cycles"].skew()
    skew2 = df["Single-Alloc2-Cycles"].skew()
    print("\nSkewness for Single-Alloc1-Cycles: {:.4f}".format(skew1))
    print("Skewness for Single-Alloc2-Cycles: {:.4f}".format(skew2))
    if skew1 > 0:
        print("Single-Alloc1-Cycles is positively skewed.")
    elif skew1 < 0:
        print("Single-Alloc1-Cycles is negatively skewed.")
    else:
        print("Single-Alloc1-Cycles is symmetric.")

    if skew2 > 0:
        print("Single-Alloc2-Cycles is positively skewed.")
    elif skew2 < 0:
        print("Single-Alloc2-Cycles is negatively skewed.")
    else:
        print("Single-Alloc2-Cycles is symmetric.")

    # 2. Plot dual KDE for Single-Alloc1-Cycles and Single-Alloc2-Cycles on the same figure
    plt.figure(figsize=(8, 6))
    sns.kdeplot(data=df, x="Single-Alloc1-Cycles", fill=True, alpha=0.3, label="Single-Alloc1-Cycles KDE")
    sns.kdeplot(data=df, x="Single-Alloc2-Cycles", fill=True, alpha=0.3, label="Single-Alloc2-Cycles KDE")
    plt.xlabel("Cycles")
    plt.ylabel("Density")
    plt.title("Dual KDE: Single-Alloc1-Cycles vs. Single-Alloc2-Cycles")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("picture/alloc_test_random_dual_kde.png")
    plt.show()

    # 3. Compute correlation between Single-Alloc1-Cycles and Single-Alloc2-Cycles
    corr_single = df["Single-Alloc1-Cycles"].corr(df["Single-Alloc2-Cycles"])
    print("\nCorrelation between Single-Alloc1-Cycles and Single-Alloc2-Cycles: {:.4f}".format(corr_single))

    # 4. Scatter plot: Single-Alloc1-Cycles vs. Single-Alloc2-Cycles
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="Single-Alloc1-Cycles", y="Single-Alloc2-Cycles", data=df, alpha=0.6)
    sns.regplot(x="Single-Alloc1-Cycles", y="Single-Alloc2-Cycles", data=df, scatter=False, color="red", ci=None)
    plt.xlabel("Single-Alloc1-Cycles")
    plt.ylabel("Single-Alloc2-Cycles")
    plt.title(f"Scatter Plot: SingleAlloc1 vs. SingleAlloc2 (corr={corr_single:.4f})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("picture/alloc_test_random_scatter_single.png")
    plt.show()

    # 5. Compute correlation between Single-Alloc2-Cycles and Random-Count (preload quantity)
    corr_preload = df["Single-Alloc2-Cycles"].corr(df["Random-Count"])
    print("\nCorrelation between Single-Alloc2-Cycles and Random-Count: {:.4f}".format(corr_preload))

    # 6. Scatter plot: Single-Alloc2-Cycles (x-axis) vs. Random-Count (y-axis)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="Single-Alloc2-Cycles", y="Random-Count", data=df, alpha=0.6)
    sns.regplot(x="Single-Alloc2-Cycles", y="Random-Count", data=df, scatter=False, color="red", ci=None)
    plt.xlabel("Single-Alloc2-Cycles")
    plt.ylabel("Random-Count (Preload Allocations)")
    plt.title(f"Scatter Plot: Preload Quantity vs. Single-Alloc2-Cycles (corr={corr_preload:.4f})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("picture/alloc_test_random_scatter_preload.png")
    plt.show()

if __name__ == '__main__':
    # make sure ./picture directory existed
    os.makedirs('picture', exist_ok=True)
    plot_fixed_alloc()
    analyze_random_allocations()
