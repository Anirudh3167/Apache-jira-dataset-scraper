import pandas as pd
import json

# Read the .txt file
file_path = "C:/Users/Lakshay Sharma/Downloads/projects.txt"  # Update this with the actual file path
with open(file_path, 'r') as file:
    file_content = file.read()

    # Split the content into individual JSON objects
    # json_data = json.loads(file_content)

    # Convert the JSON data to a pandas DataFrame
    df = pd.DataFrame(file_content)

    # Export the DataFrame to an Excel file
    excel_filename = 'projectsaaaa.xlsx'
    df.to_excel(excel_filename, index=False)

    print(f"Data exported to {excel_filename}")
