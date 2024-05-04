"""
This focuses on getting all the issues of a project
----------------------
How it works?
In the bottom,
for records > 50 there will be a (<nav role="navigation"><div class="pagination"></div></nav>)
The "pagination" class contains data-displayable-total which gives the number of issues in a sepcific project
Now this can be further called as ,
https://issues.apache.org/jira/projects/AIRAVATA/issues?startIndex=50 (50 chunks)
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv, os, json

def getHTMLPage(url, class_name):
    """ Loads the page via selenium and returns the html page """
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    html_content = driver.page_source
    driver.quit()
    return html_content

def scrapeProjectsData(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
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

def scrapeIssuesPagination(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the number of issues.
    issue_count = int(soup.find('div', class_='pagination').get('data-displayable-total',0))
    print(f'The project contains {issue_count} number of issues')

    # Call Each page (page limit = 50) like
    # idx = 0
    # while (issue_count > idx):
    #    scrapeIssuePage(idx)
    #    idx += 50

def scrapeIssuePage(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Get the issues for each page.
    rows = soup.find('ol', class_='issue-list').find_all('li')
    d = []
    for r in rows:
        # print(r['data-key'])
        d.append(r['data-key'])
    print(f'The data contains {len(rows)} issues')
    return d

def simulateClick(url):
    """ Loads the page via selenium and returns the html page """
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))
    # Get the previous html page
    prev_html_content = driver.page_source
    print('Current 50 Extracted')
    # Simluate the click
    link = driver.find_element(By.CSS_SELECTOR, "a.nav-next")
    if link == None:
        return '', ''
    link.click()
    print('Click is simulated')
    # Wait till the data gets loaded then get the current html page
    wait.until(EC.staleness_of(projects_table))
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))
    curr_html_content = driver.page_source
    print('Next 50 extracted')
    driver.quit()
    return prev_html_content , curr_html_content

# url = "https://issues.apache.org/jira/projects"
# scrapeProjectsData( getHTMLPage(url, "projects-list") )
# url = "https://issues.apache.org/jira/projects/AIRAVATA/issues/AIRAVATA-3001?filter=allopenissues"
# scrapeIssuesPagination( getHTMLPage(url, "list-content") )
url = "https://issues.apache.org/jira/projects/AIRAVATA/issues"
prev, curr = simulateClick(url)
l1, l2 = scrapeIssuePage(prev), scrapeIssuePage(curr)
print(l1 == l2, len(l1), len(l2))
print(l1[:4], l2[:4])