from tqdm import tqdm


def parse_shuffle_file(file_path, section_size):
    """
    @brief Parse the shuffle log file into a structured 2D array.

    The file is assumed to have a header line (before "# start shuffle") containing 
    the possibility list in the format: "l = [keyword1 keyword2 ... keywordN]". 
    After the header, lines starting with "l = [" represent each shuffle result.

    Each shuffle result is parsed and accumulated into a section. A section contains 
    'section_size' number of shuffles. For each section, the data is stored in a dictionary 
    mapping each keyword to a list of counts (length = number of keywords). The k-th index 
    in the list represents how many times the keyword appears in position k in that section.

    @param file_path: Path to the shuffle log file.
    @param section_size: Number of shuffles per section.
    @return tuple (possibility_list, sections)
             - possibility_list: List of keywords extracted from the file header.
             - sections: List of sections. Each section is a dictionary such that:
               section[n]["keyword"][k] gives the count for the keyword at position k.
    """
    possibility_list = []
    sections = []

    # Read all lines from file
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # --- Extract the possibility list from the header ---
    # The possibility list is expected to be on a line before "# start shuffle"
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # If a comment line with "start shuffle" is encountered, stop header parsing.
        if line.startswith("#"):
            if "start shuffle" in line:
                break
            continue
        # Look for a line starting with "l = ["
        if line.startswith("l = ["):
            # Find the content between '[' and ']'
            start_idx = line.find('[')
            end_idx = line.rfind(']')
            content = line[start_idx + 1:end_idx].strip()
            if content:
                possibility_list = content.split()
            break
    if not possibility_list:
        print("Warning: Possibility list not found in file header.")
        return possibility_list, sections

    n = len(possibility_list)

    # --- Prepare for processing shuffle results ---
    # Define a helper function to initialize an empty section.
    def new_section():
        # For each keyword, create a list of zeros with length equal to the number of keywords.
        return {key: [0] * n for key in possibility_list}

    current_section = new_section()
    current_count = 0  # Counter for the number of shuffles in the current section

    # --- Identify the starting index for shuffle results ---
    # Find the index where "# start shuffle" appears
    start_index = 0
    for idx, line in enumerate(lines):
        if "start shuffle" in line:
            start_index = idx + 1  # Data starts from the next line
            break

    # --- Process each shuffle result using a progress bar ---
    # Only process lines from start_index onward
    for line in tqdm(lines[start_index:], desc="Processing shuffle lines", total=len(lines) - start_index):
        line = line.strip()
        if not line:
            continue
        # Skip comment lines (if any)
        if line.startswith("#"):
            continue
        # Process only lines starting with "l = ["
        if line.startswith("l = ["):
            start_idx = line.find('[')
            end_idx = line.rfind(']')
            content = line[start_idx + 1:end_idx].strip()
            if not content:
                continue
            items = content.split()
            if len(items) != n:
                continue  # Skip if the number of items doesn't match the possibility list
            # For each position k, update the count for the keyword that appears at that position.
            for k in range(n):
                key = items[k]
                # Only update if key is valid (should be in possibility_list)
                if key in current_section:
                    current_section[key][k] += 1
            current_count += 1
            # When reaching the section size, save the current section and initialize a new one.
            if current_count == section_size:
                sections.append(current_section)
                current_section = new_section()
                current_count = 0
    # Append the final section if it has any data.
    if current_count > 0:
        sections.append(current_section)

    return possibility_list, sections


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Parse shuffle log file into a structured 2D array")
    parser.add_argument("--file", type=str, default="shuffle.log",
                        help="Path to the shuffle log file")
    parser.add_argument("--section_size", type=int,
                        default=100000, help="Number of shuffles per section")
    args = parser.parse_args()

    poss_list, sections = parse_shuffle_file(args.file, args.section_size)
    print("Possibility list:", poss_list)
    print("Number of sections parsed:", len(sections))
    if sections:
        print("First section data:", sections[0])
