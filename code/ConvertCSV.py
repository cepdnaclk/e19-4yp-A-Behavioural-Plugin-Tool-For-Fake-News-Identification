import csv

# File paths
tsv_file = 'all_validate.tsv'
csv_file = 'all_validate.csv'

# Open the TSV file and read it
with open(tsv_file, 'r', newline='', encoding='utf-8') as infile, \
     open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
    
    tsv_reader = csv.reader(infile, delimiter='\t')
    csv_writer = csv.writer(outfile, delimiter=',')

    for row in tsv_reader:
        csv_writer.writerow(row)

print("Conversion complete: TSV → CSV")
