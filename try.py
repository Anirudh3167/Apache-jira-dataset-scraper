import requests
from bs4 import BeautifulSoup

base_url = "https://issues.apache.org/jira/projects"
element_class = "projects-list"
data = []

try:
    for page_num in range(1, 3):  # Iterate from page 1 to 27
        url = f"{base_url}?selectedCategory=all&selectedProjectType=all&sortColumn=name&sortOrder=ascending&s=view_projects&page={page_num}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find_all("tr", {"data-project-id": True})
        for row in rows:
            project_id = row["data-project-id"]
            project_key = row.find("td", {"class": "cell-type-key"}).text
            project_name = row.find("a", {"href": True}).text
            project_url = row.find("a", {"href": True})["href"]
            

            print(f"Project ID: {project_id}")
            print(f"Project Key: {project_key}")
            print(f"Project Name: {project_name}")
            print(f"Project URL: {project_url}")
            print("-------------------------")
        print(page_num)
except Exception as e:
    pass
print(data)

# Now 'data' contains the tables with class 'jira-sortable-table' from all pages
