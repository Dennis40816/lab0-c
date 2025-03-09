import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Set DUDECT_NUMBER_PERCENTILES to 100
N = 100

# Create indices 0 to 99 (we use i+1 as the percentile index)
indices = np.arange(N)

# Calculate the "kept" fraction using the formula:
# kept = 1 - 0.5^(10 * (i+1)/100)
kept_fraction = 1 - (0.5 ** (10 * (indices + 1) / N))

# The cropped fraction is the complement of the kept fraction:
cropped_fraction = 1 - kept_fraction

# Convert the fraction to percentage values
cropped_percentage = cropped_fraction * 100

# Plot the cropped percentage vs. the percentile index
plt.figure(figsize=(10, 7))
plt.plot(indices + 1, cropped_percentage, marker='o', linestyle='-')
plt.xlabel("Percentile Index (1 to 100)", fontsize=14)
plt.ylabel("Cropped Data Fraction (%)", fontsize=14)
plt.title("Cropped Data Fraction vs. Percentile Index", fontsize=16)
plt.grid(True)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Format y-axis ticks to display the percentage sign
ax = plt.gca()
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.show()
