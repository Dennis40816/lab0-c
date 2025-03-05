import statistics
from scipy.stats import chisquare


def compute_fixed_counts(sections, possibility_list):
    """
    @brief Compute fixed counts from parsed section data.
    @param sections: List of sections (each section is a dict mapping keyword to list of counts per position).
    @param possibility_list: List of keywords.
    @return List of dictionaries for each section mapping keyword to fixed count.
             Fixed count for a keyword is defined as the count at the position corresponding to its index.
             (i.e. fixed_count = section["key_word"][index_of(key_word) ])
    """
    fixed_counts = []
    for section in sections:
        fixed = {}
        for i, key in enumerate(possibility_list):
            fixed[key] = section[key][i]
        fixed_counts.append(fixed)
    return fixed_counts


def compute_distribution_error_metrics(sections, section_size, possibility_list):
    """
    @brief Compute error metrics for each keyword based on full distribution data by calculating 
           statistics separately for each position and then selecting the worst-case values.

    For each keyword, this function iterates over each position (from 0 to n-1) and collects errors 
    from all sections at that position. The error is defined as:
         error = observed count - expected_per_cell
    where expected_per_cell = section_size / n (n is the length of possibility_list).

    Then, for each keyword, it calculates the max, min, mean, and standard deviation of errors for 
    each position. Finally, the overall metric for the keyword is chosen as:
        - overall_max: maximum error among positions
        - overall_min: minimum error among positions
        - overall_mean: the mean error (selected as the one with the highest absolute value among positions)
        - overall_std: maximum standard deviation among positions

    @param sections: List of sections. Each section is a dictionary mapping a keyword to a list of counts per position.
                     For example, section["keyword"][k] gives the count for the keyword at position k in that section.
    @param section_size: Number of shuffles per section.
    @param possibility_list: List of keywords.
    @return Dictionary mapping each keyword to a dictionary of error metrics: {"max": overall_max, "min": overall_min, 
             "mean": overall_mean, "std": overall_std}.
    """
    metrics = {}
    n = len(possibility_list)
    # Expected count per cell (for each position)
    expected_per_cell = section_size / n

    # Process each keyword separately.
    for key in possibility_list:
        max_by_pos = []   # Maximum error per position
        min_by_pos = []   # Minimum error per position
        mean_by_pos = []  # Mean error per position
        std_by_pos = []   # Standard deviation per position

        # Process each position index
        for pos in range(n):
            # Collect errors for the current position across all sections
            errors_pos = [section[key][pos] -
                          expected_per_cell for section in sections]
            if errors_pos:
                max_by_pos.append(max(errors_pos))
                min_by_pos.append(min(errors_pos))
                mean_by_pos.append(statistics.mean(errors_pos))
                std_by_pos.append(statistics.stdev(errors_pos)
                                  if len(errors_pos) > 1 else 0)
            else:
                max_by_pos.append(0)
                min_by_pos.append(0)
                mean_by_pos.append(0)
                std_by_pos.append(0)

        # Choose the worst-case statistics among positions.
        overall_max = max(max_by_pos) if max_by_pos else 0
        overall_min = min(min_by_pos) if min_by_pos else 0
        # For mean, select the mean error from the position that has the maximum absolute mean error.
        overall_mean = max(mean_by_pos, key=lambda x: abs(x)
                           ) if mean_by_pos else 0
        overall_std = max(std_by_pos) if std_by_pos else 0

        metrics[key] = {"max": overall_max, "min": overall_min,
                        "mean": overall_mean, "std": overall_std}
    return metrics


def compute_chi_square(sections, section_size, possibility_list):
    """
    @brief Compute chi-square test for each keyword based on aggregated full distribution data.
    @param sections: List of sections with distribution counts.
    @param section_size: Number of shuffles per section.
    @param possibility_list: List of keywords.
    @return Dictionary mapping each keyword to chi-square statistic and p-value.
    """
    chi_results = {}
    n = len(possibility_list)
    expected_per_cell = section_size / n
    for key in possibility_list:
        aggregated = []
        for section in sections:
            aggregated.extend(section[key])
        expected = [expected_per_cell] * len(aggregated)
        chi2, p_value = chisquare(f_obs=aggregated, f_exp=expected)
        chi_results[key] = {"chi2": chi2, "p_value": p_value}
    return chi_results


if __name__ == "__main__":
    # Dummy test if needed
    pass
