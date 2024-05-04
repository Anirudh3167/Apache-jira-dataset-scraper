import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define the base URL and initialize an empty list to store data
base_url = "https://issues.apache.org/jira/projects"
data_list = []

# Iterate through pages 1 to 27
for page_num in range(1, 2):
    # Construct the URL for each page
    url = f"{base_url}?selectedCategory=all&selectedProjectType=all&sortColumn=name&sortOrder=ascending&s=view_projects&page={page_num}"
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract the data you need from the page
        # Here, we assume you want to extract project names
        data_list.append(soup.find("div", {"class": "p-list"}))

    else:
        print(f"Failed to fetch data from page {page_num}")


# Open/create a text file in write mode
file_path = 'data.txt'
with open(file_path, 'w') as file:
    # Write data to the file
    for data in data_list:
        file.write(str(data))

# File is automatically closed after the 'with' block
print("Data saved to", file_path)

# Create a DataFrame from the collected data
# df = pd.DataFrame(data_list, columns=["Project Names"])

# Save the DataFrame to an Excel file
# df.to_excel("projects_data.xlsx", index=False)
