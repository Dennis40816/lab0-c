import matplotlib.pyplot as plt
import matplotlib.patches as patches


def interactive_legend():
    """
    @brief Enable interactive legend toggling.
    """
    leg = plt.gca().get_legend()
    if leg is None:
        return
    lines = plt.gca().get_lines()
    for legline in leg.get_lines():
        legline.set_picker(5)

    def on_pick(event):
        legline = event.artist
        orig_lines = plt.gca().get_lines()
        try:
            index = leg.get_lines().index(legline)
        except ValueError:
            return
        orig_line = orig_lines[index]
        vis = not orig_line.get_visible()
        orig_line.set_visible(vis)
        legline.set_alpha(1.0 if vis else 0.2)
        plt.gcf().canvas.draw()
    plt.gcf().canvas.mpl_connect('pick_event', on_pick)


def plot_fixed_error_graph(fixed_counts, section_size, possibility_list):
    """
    @brief Plot fixed-position error graph using fixed counts.
    @param fixed_counts: List of dictionaries for each section mapping keyword to fixed count.
    @param section_size: Number of shuffles per section.
    @param possibility_list: List of keywords.
    """
    num_sections = len(fixed_counts)
    section_indices = list(range(1, num_sections + 1))
    plt.figure(figsize=(10, 6))
    for key in possibility_list:
        values = [section[key] for section in fixed_counts]
        plt.plot(section_indices, values, marker='o', label=key)
    expected = section_size / len(possibility_list)
    plt.axhline(expected, color='gray', linestyle='--', label="Expected")
    plt.xlabel(f"Section Index (each section = {section_size} shuffles)")
    plt.ylabel("Fixed Position Count")
    plt.title("Fixed-Point Error Plot (Absolute Values)")
    plt.legend()
    interactive_legend()
    plt.grid(True)
    plt.show()


def plot_distribution_error_metrics(metrics):
    """
    @brief Plot full distribution error metrics as a bar chart.
    @param metrics: Dictionary mapping keyword to error metrics.
    """
    elements = list(metrics.keys())
    mean_errors = [metrics[key]["mean"] for key in elements]
    std_errors = [metrics[key]["std"] for key in elements]
    max_errors = [metrics[key]["max"] for key in elements]
    min_errors = [metrics[key]["min"] for key in elements]

    plt.figure(figsize=(10, 6))
    x_positions = list(range(len(elements)))
    plt.bar(x_positions, mean_errors, yerr=std_errors, capsize=5,
            label="Mean Error", color='lightblue', edgecolor='black')
    for i, key in enumerate(elements):
        plt.text(x_positions[i], mean_errors[i] + std_errors[i] + 0.1,
                 f"max:{max_errors[i]:.2f}", ha='center', va='bottom', fontsize=8)
        plt.text(x_positions[i], mean_errors[i] - std_errors[i] - 0.1,
                 f"min:{min_errors[i]:.2f}", ha='center', va='top', fontsize=8)
    plt.axhline(0, color='gray', linestyle='--', label="0 error")
    plt.xticks(x_positions, elements)
    plt.xlabel("Element")
    plt.ylabel("Error (Observed - Expected) [Absolute Difference]")
    plt.title("Full Distribution Error Metrics (Absolute Errors)")
    plt.legend()
    interactive_legend()
    plt.grid(True)
    plt.show()


def plot_distribution_error_metrics_filled(metrics, expected):
    """
    @brief Plot full distribution error metrics as a 'box-style' chart with filled rectangles for std, and whiskers for min/max.

    This function displays each keyword's error as a percentage of the expected value. It assumes the mean is centered at 0,
    i.e., mean error has been subtracted out. The rectangle spans from -std% to +std%, and horizontal whiskers mark min% and max%.

    @param metrics: dictionary mapping each keyword to {'min': float, 'max': float, 'mean': float, 'std': float}, all in absolute units.
                    Example: metrics[key]["mean"] is the mean absolute error for 'key' (before any percentage conversion).
    @param expected: the expected count per cell, used to convert absolute errors to percentage.
    """
    elements = list(metrics.keys())
    # set up figure
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # prepare x positions
    x_positions = range(len(elements))

    # we'll create a rectangle for the ±std range, and whiskers for the min/max
    box_width = 0.6  # the width of the rectangle

    # compute the percentage for min, max, mean, and std (relative to mean)
    # if we consider "center" = mean, then the rectangle covers [mean - std, mean + std].
    # but since we want 0 to represent 'mean', we define:
    # min%  = (min - mean)/expected * 100
    # max%  = (max - mean)/expected * 100
    # -std% = - (std/expected)*100  and +std% likewise.

    for i, key in enumerate(elements):
        m_abs = metrics[key]["mean"]  # mean in absolute value
        mi_abs = metrics[key]["min"]  # min  in absolute value
        ma_abs = metrics[key]["max"]  # max  in absolute value
        s_abs = metrics[key]["std"]   # std  in absolute value

        # convert all to "relative to mean" (so 'mean' -> 0)
        # delta_min = (mi_abs - m_abs), delta_max = (ma_abs - m_abs)
        delta_min = mi_abs - m_abs
        delta_max = ma_abs - m_abs
        # for std we have ±s_abs relative to mean
        low_std = -s_abs
        high_std = s_abs

        # now convert to percentage of expected
        min_pct = (delta_min / expected) * 100.0
        max_pct = (delta_max / expected) * 100.0
        low_std_pct = (low_std / expected) * 100.0
        high_std_pct = (high_std / expected) * 100.0

        # draw the filled rectangle for ±std
        # rectangle from low_std_pct to high_std_pct at x = i
        # we'll shift the rectangle so it's centered on i, with width box_width
        rect_x_left = i - box_width / 2
        rect_height = high_std_pct - low_std_pct
        rect_y_bottom = low_std_pct

        rect = patches.Rectangle(
            (rect_x_left, rect_y_bottom),  # (x, y)
            box_width,                     # width
            rect_height,                   # height
            facecolor='cornflowerblue',
            alpha=0.3,
            edgecolor='blue',
            label="±Std" if i == 0 else None
        )
        ax.add_patch(rect)

        # draw horizontal whiskers at min_pct and max_pct
        # we place them at y = min_pct and y = max_pct
        # and a vertical line from min_pct to max_pct at x = i
        ax.vlines(
            x=i, ymin=min_pct, ymax=max_pct,
            colors='gray', linestyles='dashed',
            label="Range" if i == 0 else None
        )
        # add small horizontal lines to highlight min / max if desired
        whisker_width = 0.2
        ax.hlines(
            y=min_pct, xmin=i - whisker_width, xmax=i + whisker_width,
            colors='gray'
        )
        ax.hlines(
            y=max_pct, xmin=i - whisker_width, xmax=i + whisker_width,
            colors='gray'
        )

        # plot a marker at 0 to indicate the mean
        ax.plot(i, 0, 'o', color='blue' if i == 0 else 'tab:blue',
                label="Mean=0" if i == 0 else None)

    # set x-axis ticks
    plt.xticks(list(x_positions), elements)
    plt.xlabel("Element")
    plt.ylabel("Error Percentage (%)")
    plt.title("Full Distribution Error Metrics (Box-Style, Center=Mean=0)")

    # auto scale the y range to fit data + small margin
    y_values = []
    for key in elements:
        m_abs = metrics[key]["mean"]
        mi_abs = metrics[key]["min"]
        ma_abs = metrics[key]["max"]
        # extremes in percent
        min_pct = (mi_abs - m_abs) / expected * 100
        max_pct = (ma_abs - m_abs) / expected * 100
        y_values.extend([min_pct, max_pct])
    if y_values:
        bottom = min(y_values)
        top = max(y_values)
        margin = 3.0
        plt.ylim(bottom - margin, top + margin)

    plt.grid(True)
    plt.legend()
    plt.show()


def set_plot_font_sizes(font_size=14):
    """
    @brief Set global font sizes for matplotlib figures.
    @param font_size: the base font size to be applied to various plot elements.
    """
    plt.rcParams.update({
        'font.size': font_size,          # overall font size
        'axes.labelsize': font_size,     # x/y label size
        'axes.titlesize': font_size + 2,  # axes title size
        'legend.fontsize': font_size,    # legend font size
        'xtick.labelsize': font_size,    # x-axis tick label size
        'ytick.labelsize': font_size     # y-axis tick label size
    })
