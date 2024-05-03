from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv, os, json

def addToCSV(project_name, issue_name, issue_stats):
    # Check if the CSV file exists, if not, create it and write the header
    file_path = './webScrapped.csv'
    if not os.path.isfile(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Project Name', 'Issue Name', 'Issue Stats'])
    
    # Append data to the CSV file
    json_issue_stats = json.dumps(issue_stats)
    with open(file_path, 'a+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([project_name, issue_name,json_issue_stats])


def get_issue_summary(url):
    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    issues_table = wait.until( EC.presence_of_element_located((By.ID, "issue-content")) )
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all('li', class_='item')

    ans = {}
    for r in rows:
        head = r.find('div',class_='wrap').strong
        if head == None:
            head = 'Not found'
        elif head.label == None:
            head = head.text.strip()
        else:
            head = head.label.text.strip()

        val = r.find('div',class_='wrap').find('span', class_='value')
        if val == None:
            val = r.find('div',class_='wrap').find('span', class_='labels-wrap value')
        if val == None:
            val = 'Not Found'
        else:
            val = val.text.strip()

        print(head,val)
        ans[head] = val
    driver.quit()
    return ans

def get_issues(url, limit = 4):
    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    issues_table = wait.until( EC.presence_of_element_located((By.CLASS_NAME, "list-content")) )
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find('ol', class_='issue-list').find_all('li')

    for r in rows:
        if limit > 0:
            limit -= 1
        else:
            break
        print(r['data-key'])
        ans = get_issue_summary(url + '/issues/' + r['data-key'])
        addToCSV(url.split('/')[-1],r['data-key'],ans)
    driver.quit()

def get_projects(url, limit = 3):
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
        project_url = row.find("a", {"href": True})["href"]
        
        get_issues(url + '/' + project_key)

        print(f"Project ID: {project_id}")
        print(f"Project Key: {project_key}")
        print(f"Project Name: {project_name}")
        print(f"Project URL: {project_url}")
        print("-------------------------")

    driver.quit()

url = "https://issues.apache.org/jira/projects"
get_projects(url)
