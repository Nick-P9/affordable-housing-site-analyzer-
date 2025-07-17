import pandas as pd

# Load the CSV file
input_file = 'Osceola County (59), 3.5to10.0 Acre.csv'  # Replace with your input CSV file name
output_file = 'osceola.csv'  # Replace with your desired output CSV file name

# Read the CSV file into a DataFrame
df = pd.read_csv(input_file)

# Define the allowed values for the DOR_UC column
allowed_values = [0, 10, 11, 17, 28, 40]

# Filter the DataFrame to only include rows where DOR_UC has allowed values
filtered_df = df[df['DOR_UC'].isin(allowed_values)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv(output_file, index=False)

print(f"Filtered rows saved to {output_file}")