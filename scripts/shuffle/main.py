import argparse
from parser import parse_shuffle_file
import stats
import plotter


def main():
    parser = argparse.ArgumentParser(
        description="Shuffle File Analyzer with 2D Array Parser, Chi-Square Test, and Interactive Plotting")
    parser.add_argument("--file", type=str, default="shuffle_xorshift1.log",
                        help="Path to the shuffle log file")
    parser.add_argument("--section_size", type=int,
                        default=100000, help="Number of shuffles per section")
    args = parser.parse_args()

    # Parse the file into a 2D array structure (per section)
    possibility_list, sections = parse_shuffle_file(
        args.file, args.section_size)
    if not possibility_list:
        print("No possibility list found. Exiting.")
        return
    print("Possibility list:", possibility_list)
    print("Number of sections parsed:", len(sections))

    # Compute fixed counts for each section
    fixed_counts = stats.compute_fixed_counts(sections, possibility_list)
    expected_fixed = args.section_size / len(possibility_list)
    print("Fixed-position expected count per section:", expected_fixed)
    print("Fixed-position counts per section:")
    for i, section in enumerate(fixed_counts, 1):
        print(f"Section {i}: {section}")

    # plot
    plotter.set_plot_font_sizes(16)
    plotter.plot_fixed_error_graph(
        fixed_counts, args.section_size, possibility_list)

    # Compute error metrics and chi-square test for full distribution data
    error_metrics = stats.compute_distribution_error_metrics(
        sections, args.section_size, possibility_list)
    chi_results = stats.compute_chi_square(
        sections, args.section_size, possibility_list)

    print("Full Distribution Error Metrics (Observed - Expected):")
    for key, met in error_metrics.items():
        print(
            f"{key}: max = {met['max']:.2f}, min = {met['min']:.2f}, mean = {met['mean']:.2f}, std = {met['std']:.2f}")
    print("Chi-Square Test Results:")
    for key, res in chi_results.items():
        print(
            f"{key}: chi2 = {res['chi2']:.2f}, p-value = {res['p_value']:.4f}")
    
    plotter.plot_distribution_error_metrics_filled(
        error_metrics, args.section_size / len(possibility_list))


if __name__ == "__main__":
    main()
