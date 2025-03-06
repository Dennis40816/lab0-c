import re
import statistics
import argparse
import matplotlib.pyplot as plt

def parse_entropy_from_line(line):
    """
    parse entropy values from a log line that contains a list of strings.
    :param line: input log line
    :return: list of entropy values as float
    """
    pattern = re.compile(r'\(([\d\.]+)%\)')
    return [float(match) for match in pattern.findall(line)]

def preprocess_log_file(file_path):
    """
    read the log file, filter out invalid lines and extract all entropy values.
    :param file_path: path to the log file
    :return: list of entropy values as float
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    
    all_entropies = []
    for line in lines:
        line = line.strip()
        # filter out lines that are "l = []" or "l = NULL"
        if line in ["l = []", "l = NULL"]:
            continue
        # process only lines that contain '(' indicating valid data
        if '(' in line:
            entropies = parse_entropy_from_line(line)
            all_entropies.extend(entropies)
    return all_entropies

def plot_entropy_distribution(entropies, avg, std):
    """
    plot histogram of entropy values and mark standard deviation lines.
    :param entropies: list of entropy values
    :param avg: average entropy value
    :param std: standard deviation of entropy values
    """
    plt.figure(figsize=(10, 6))
    # plot histogram with 50 bins
    plt.hist(entropies, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    # mark average with a red dashed vertical line
    plt.axvline(avg, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {avg:.2f}%')
    # mark boundaries for standard deviation with green dotted vertical lines
    plt.axvline(avg - std, color='green', linestyle='dotted', linewidth=2, label=f'Mean - STD: {avg - std:.2f}%')
    plt.axvline(avg + std, color='green', linestyle='dotted', linewidth=2, label=f'Mean + STD: {avg + std:.2f}%')
    plt.xlabel('Entropy (%)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Entropy (%)')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Analyze entropy values from a log file and plot their distribution.")
    parser.add_argument("-f", "--file", required=True, help="Path to the log file")
    args = parser.parse_args()

    # preprocess the log file to extract entropy values
    all_entropies = preprocess_log_file(args.file)
    
    # calculate and print summary statistics if entropy data exists
    if all_entropies:
        avg_entropy = statistics.mean(all_entropies)
        min_entropy = min(all_entropies)
        max_entropy = max(all_entropies)
        std_entropy = statistics.stdev(all_entropies)
        
        print(f"Number of samples: {len(all_entropies)}")
        print(f"Average Entropy: {avg_entropy:.2f}%")
        print(f"Minimum Entropy: {min_entropy:.2f}%")
        print(f"Maximum Entropy: {max_entropy:.2f}%")
        print(f"Standard Deviation: {std_entropy:.2f}%")
        
        # plot the distribution of entropy values with marked standard deviation lines
        plot_entropy_distribution(all_entropies, avg_entropy, std_entropy)
    else:
        print("No valid entropy data found.")

if __name__ == '__main__':
    main()
