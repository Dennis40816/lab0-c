#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_fixed_alloc(logfile="alloc_test_fixed.log"):
    df = pd.read_csv(logfile)
    plt.figure(figsize=(8, 6))
    plt.plot(df["Iteration"], df["AverageCyclesPerAllocation"], marker="o", linestyle="-")
    plt.xlabel("Iteration")
    plt.ylabel("Average Cycles per Allocation")
    plt.title("Fixed Allocations: Average Cycles Over Iterations")
    plt.grid(True)
    plt.savefig("alloc_test_fixed_plot.png")
    plt.show()

def analyze_random_allocations(logfile="alloc_test_random.log"):
    # Read the CSV log file
    # Expected header: Iteration, RandomCount, SingleAlloc1Cycles, GroupAllocCycles, SingleAlloc2Cycles
    df = pd.read_csv(logfile)
    
    # 1. Print descriptive statistics for SingleAlloc1Cycles and SingleAlloc2Cycles
    print("SingleAlloc1Cycles Statistics:")
    print(df["SingleAlloc1Cycles"].describe())
    print("\nSingleAlloc2Cycles Statistics:")
    print(df["SingleAlloc2Cycles"].describe())
    
    # Calculate skewness for both SingleAlloc1Cycles and SingleAlloc2Cycles
    skew1 = df["SingleAlloc1Cycles"].skew()
    skew2 = df["SingleAlloc2Cycles"].skew()
    print("\nSkewness for SingleAlloc1Cycles: {:.4f}".format(skew1))
    print("Skewness for SingleAlloc2Cycles: {:.4f}".format(skew2))
    if skew1 > 0:
        print("SingleAlloc1Cycles is positively skewed.")
    elif skew1 < 0:
        print("SingleAlloc1Cycles is negatively skewed.")
    else:
        print("SingleAlloc1Cycles is symmetric.")
    
    if skew2 > 0:
        print("SingleAlloc2Cycles is positively skewed.")
    elif skew2 < 0:
        print("SingleAlloc2Cycles is negatively skewed.")
    else:
        print("SingleAlloc2Cycles is symmetric.")
    
    # 2. Plot dual KDE for SingleAlloc1Cycles and SingleAlloc2Cycles on the same figure
    plt.figure(figsize=(8, 6))
    sns.kdeplot(data=df, x="SingleAlloc1Cycles", fill=True, alpha=0.3, label="SingleAlloc1Cycles KDE")
    sns.kdeplot(data=df, x="SingleAlloc2Cycles", fill=True, alpha=0.3, label="SingleAlloc2Cycles KDE")
    plt.xlabel("Cycles")
    plt.ylabel("Density")
    plt.title("Dual KDE: SingleAlloc1Cycles vs. SingleAlloc2Cycles")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("alloc_test_random_dual_kde.png")
    plt.show()
    
    # 3. Compute correlation between SingleAlloc1Cycles and SingleAlloc2Cycles
    corr_single = df["SingleAlloc1Cycles"].corr(df["SingleAlloc2Cycles"])
    print("\nCorrelation between SingleAlloc1Cycles and SingleAlloc2Cycles: {:.4f}".format(corr_single))
    
    # 4. Scatter plot: SingleAlloc1Cycles vs. SingleAlloc2Cycles
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="SingleAlloc1Cycles", y="SingleAlloc2Cycles", data=df, alpha=0.6)
    sns.regplot(x="SingleAlloc1Cycles", y="SingleAlloc2Cycles", data=df, scatter=False, color="red", ci=None)
    plt.xlabel("SingleAlloc1Cycles")
    plt.ylabel("SingleAlloc2Cycles")
    plt.title(f"Scatter Plot: SingleAlloc1 vs. SingleAlloc2 (corr={corr_single:.4f})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("alloc_test_random_scatter_single.png")
    plt.show()
    
    # 5. Compute correlation between SingleAlloc2Cycles and RandomCount (preload quantity)
    corr_preload = df["SingleAlloc2Cycles"].corr(df["RandomCount"])
    print("\nCorrelation between SingleAlloc2Cycles and RandomCount: {:.4f}".format(corr_preload))
    
    # 6. Scatter plot: SingleAlloc2Cycles (x-axis) vs. RandomCount (y-axis)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="SingleAlloc2Cycles", y="RandomCount", data=df, alpha=0.6)
    sns.regplot(x="SingleAlloc2Cycles", y="RandomCount", data=df, scatter=False, color="red", ci=None)
    plt.xlabel("SingleAlloc2Cycles")
    plt.ylabel("RandomCount (Preload Allocations)")
    plt.title(f"Scatter Plot: Preload Quantity vs. SingleAlloc2Cycles (corr={corr_preload:.4f})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("alloc_test_random_scatter_preload.png")
    plt.show()

if __name__ == '__main__':
    plot_fixed_alloc()
    analyze_random_allocations()
