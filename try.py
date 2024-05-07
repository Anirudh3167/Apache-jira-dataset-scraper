import pandas as pd
import json

# Read the .txt file
file_path = "C:/Users/Lakshay Sharma/Downloads/projectsppp.txt"  # Update this with the actual file path


import pandas as pd

# Read the text file
with open(file_path, 'r') as file:
    text_data = file.read()

# Split the text data into individual records
records = eval(text_data)

# Convert the data into a pandas DataFrame
df = pd.DataFrame(records, columns=['Name', 'Code', 'URL', 'Author', 'Count'])

# Write the DataFrame to an Excel file
df.to_excel('output.xlsx', index=False)

