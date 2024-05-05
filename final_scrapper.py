# Serilaizer
'''
Scrapes the projects and returns their id's
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pprint, time


##############################################
# Issues Extraction
##############################################
# Issue Content (Issue Id, Issue Heading, Issue Details)
def getIssueDetails(content):
    """ Uses Beautiful soup and returns the details for current html page"""
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all('li', class_='item')

    ans = {}
    for r in rows:
        # Find the detail title
        head = r.find('div',class_='wrap').strong
        if head == None:    head = 'Not found'
        elif head.label == None:    head = head.text.strip()
        else:       head = head.label.text.strip()

        # Find teh detail value
        val = r.find('div',class_='wrap').find('span', class_='value')
        if val == None:
            val = r.find('div',class_='wrap').find('span', class_='labels-wrap value')
        if val == None:     val = 'Not Found'
        else:               val = val.text.strip()

        ans[head] = val
    return ans

def getIssues(url):
    """ Loads each and every issue details of a project """
    res = []

    # Load the html page
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))

    # Simulate next click (until next is not found)
    pg = 0
    while True:
        # Go by Each issue in a single page.
        for li in driver.find_elements(By.CSS_SELECTOR, "ol.issue-list > li"):
            # Simulate click on the <a> tag within the <li> element
            link = li.find_element(By.CSS_SELECTOR, "a.splitview-issue-link")
            if link is None:  break
            link.click()
            # Wait till the click request gets the data
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading")))
            res.append( getIssueDetails(driver.page_source) )
                

        # Simluate the next click
        try:
            link = driver.find_element(By.CSS_SELECTOR, "a.nav-next")
        except:
            print("Finished Scrapping for this project.")
            break
        if link is None:   break
        link.click()

        # Wait till the data gets loaded then get the current html page
        wait.until(EC.staleness_of(projects_table))
        projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))
        # print(f'Issues of page {pg} extracted')
        pg += 1
    return res


##############################################
# Projects Extraction
##############################################
# Project Details (for serializer)
def getProjectIds(content):
    """ Uses Beautiful soup and returns the project ids for current html page"""
    res = []
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr", {"data-project-id": True})
    for row in rows:
        res.append(row.find("td", {"class": "cell-type-key"}).text)
    return res

def getProjects(url):
    """ Loads the page via selenium and returns the Project Ids """
    res = []

    # Load the html page
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
    
    # Get the project ids in that page.
    res.extend( getProjectIds(driver.page_source) )

    # Simluate the click (Until next is enabled)
    pg = 1
    while True:
        link = driver.find_element(By.CSS_SELECTOR, "li.aui-nav-next > a")
        if link is None or link.get_attribute("aria-disabled") == "true":
            break
        else:
            link.click()

        # Wait till the data gets loaded then get the current html page
        projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
        print(f'Extraction completed for page {pg}')
        # Get the project ids in that page.
        res.extend( getProjectIds(driver.page_source) )
        pg += 1

    driver.quit()
    return res


##############################################
# Multi Threading
##############################################
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

ans = {}
# Execel Sheet file handling code
def get_project_issues(project_key):
    """Scrapes the issues for a given project and returns the results"""
    url = f"https://issues.apache.org/jira/projects/{project_key}/issues/"
    return project_key, getIssues(url)

def scrape_projects(url, threads = 10):
    """Scrapes project IDs from the given URL"""
    res = getProjects(url)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_project = {executor.submit(get_project_issues, project_key): project_key for project_key in res}
        for future in concurrent.futures.as_completed(future_to_project):
            project_key = future_to_project[future]
            try:
                ans[project_key] = future.result()
            except Exception as e:
                print(f"Error occurred for project {project_key}: {e}")

url = "https://issues.apache.org/jira/projects"
ans = {}
threads = 10
scrape_projects( url,threads )
print(ans)


##############################################
# Serialization
##############################################
# Single Function()
def serializeData(data: list):
    pass

##############################################
# Writing data to excel sheet
##############################################
def addToExcel(data):
    res = serializeData(data)
    pass


# url = "https://issues.apache.org/jira/projects"
# res = getProjects( url )
# print( res[:4],res[-4:] )

# url = "https://issues.apache.org/jira/projects/AAR/issues/"
# res = getIssues( url )
# print( res[:4],res[-4:] )
# pprint.pprint( res[-2:] )

# ans = {}
# for key in res:
#     url = f"https://issues.apache.org/jira/projects/{key}/issues/"
#     ans[key] = getIssues( url )

# print(ans.items()[-1])
