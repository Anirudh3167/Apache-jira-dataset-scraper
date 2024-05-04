from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd


data_list = []

def get_projects(url, limit = 25):
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all("tr", {"data-project-id": True})

    for row in rows:
        if limit > 0:
            limit -= 1
        else:
            break
        project_id = row["data-project-id"]
        project_key = row.find("td", {"class": "cell-type-key"}).text
        project_name = row.find("a", {"href": True}).text
        project_lead = row.find("td", {"class": "cell-type-user"}).text
        project_category = row.find("td", {"class": "cell-type-category"}).text
        project_url = row.find("a", {"href": True})["href"]
        project_direct_url = row.find("td", {"class": "cell-type-url"}).text
        
        # get_issues(url + '/' + project_key)

        print(f"Project ID: {project_id}")
        print(f"Project Key: {project_key}")
        print(f"Project Name: {project_name}")
        print(f"Project Lead: {project_lead}")
        print(f"Project Category: {project_category}")
        print(f"Project URL: {project_url}")
        print(f"Project Direct URL: {project_direct_url}")
        print("-------------------------")

        data_list.append([project_id, project_key, project_name, project_lead,project_category,project_url,project_direct_url])
    driver.quit()

    

base_url = "https://issues.apache.org/jira/projects"

try:
    for page_num in range(1, 28):  # Iterate from page 1 to 27
        url = f"{base_url}?selectedCategory=all&selectedProjectType=all&sortColumn=name&sortOrder=ascending&s=view_projects&page={page_num}"
        get_projects(url)

except Exception as e: 
    pass

# print(data_list)
# Create a DataFrame from the collected data
df = pd.DataFrame(data_list, columns=["Project ID", "Project Key", "Project Name", "Project Lead", "Project Category", "Project URL", "Project Direct URL"])

# # Save the DataFrame to an Excel file
df.to_excel("projects_data.xlsx", index=False)