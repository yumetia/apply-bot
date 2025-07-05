import csv

def read_csv(csv_file):
    """
    Reads the CSV, skipping any lines before the actual header (starting with 'Entreprise;').
    Returns a list of dictionaries for each row.
    """
    with open(csv_file, newline='', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the actual header row
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("entreprise;"):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("Could not find header line starting with 'Entreprise;'.")

    data_lines = lines[header_idx:]
    reader = csv.DictReader(data_lines, delimiter=';')
    return list(reader)


def save_csv(csv_file, data):
    """
    Rewrites the entire CSV with updated data using the same columns.
    """
    if not data:
        print("No data to save.")
        return
    fields = data[0].keys()
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=';')
        writer.writeheader()
        writer.writerows(data)
