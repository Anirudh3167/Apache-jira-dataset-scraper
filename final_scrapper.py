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
import pandas as pd

##############################################
# Serialization
##############################################
def addExcelRow(project_name, project_id, project_lead, project_category, project_URL, issue_id, issue_heading, issue_type, issue_status, issue_priority, issue_resolution, issue_labels, issue_external_issue_url, issue_language, issue_environment):
    res_dict = {}
    res_dict["Project Name"] = project_name if project_name else "Not Found"
    res_dict["Project Id"] = project_id if project_id else "Not Found"
    res_dict["Project Lead"] = project_lead if project_lead else "Not Found"
    res_dict["Project Category"] = project_category if project_category else "Not Found"
    res_dict["Project URL"] = project_URL if project_URL else "Not Found"
    res_dict["Issue Id"] = issue_id if issue_id else "Not Found"
    res_dict["Issue Heading"] = issue_heading if issue_heading else "Not Found"
    res_dict["Issue Type"] = issue_type if issue_type else "Not Found"
    res_dict["Issue Status"] = issue_status if issue_status else "Not Found"
    res_dict["Issue Priority"] = issue_priority if issue_priority else "Not Found"
    res_dict["Issue Resolution"] = issue_resolution if issue_resolution else "Not Found"
    res_dict["Issue Labels"] = issue_labels if issue_labels else "Not Found"
    res_dict["Issue External Issue URL"] = issue_external_issue_url if issue_external_issue_url else "Not Found"
    res_dict["Issue Language"] = issue_language if issue_language else "Not Found"
    res_dict["Issue Environment"] = issue_environment if issue_environment else "Not Found"
    return res_dict


##############################################
# Issues Extraction
##############################################
def getIssueDetails(content):
    """ Uses Beautiful soup and returns the details for current html page"""
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all('li', class_='item')
    issue_title = soup.find('h1', {"id": "summary-val"}).text
    issue_id = soup.find('a', {"id": "key-val"}).text
    ans = {}
    ans['Id'] = issue_id
    ans['Title'] = issue_title
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
    # print(ans)
    # {'Id': 'AAR-51816', 'Title': 'Balloons in Dubai - delivery on the same day | Online Helium balloon Store for party, birthday', 'Type:': 'Bug', 'Status:': 'Open', 'Priority:': 'Major', 'Resolution:': 'Unresolved', 'Labels:': 'Not Found', 'External issue URL:': 'Not Found'}
    return ans

def getIssues(url) -> list[dict]:
    """ Loads each and every issue details of a project """
    res = [] # list of dicts

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
def getProjectIds(content) -> list[dict]:
    """ Uses Beautiful soup and returns the project ids for current html page"""
    result_list = []
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr", {"data-project-id": True})
    for row in rows:
        # res.append(row.find("td", {"class": "cell-type-key"}).text)
        res = {}
        res['project_id'] = row.find("td", {"class": "cell-type-key"}).text
        res['project_name'] = row.find("a", {"href": True}).text
        res['project_lead'] = row.find("td", {"class": "cell-type-user"}).text
        res['project_category'] = row.find("td", {"class": "cell-type-category"}).text
        res['project_url'] = row.find("td", {"class": "cell-type-url"}).text
        result_list.append(res)
        
    return result_list

# iterates over the 27 sections to get projects of all
def getProjects(url) -> list[dict]:
    """ Loads the page via selenium and returns the Project Ids """
    res = []

    # Load the html page
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
    
    # Get the project ids in that page.
    # remaining_project_ids = [project['project_id'] for project in getProjectIds(driver.page_source)]
    res.extend( getProjectIds(driver.page_source))

    # Simulate the click (Until next is enabled)
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
        res.extend( getProjectIds(driver.page_source))
        pg += 1

    driver.quit()
    
    # print(res) # all 668 rows
    # [{'project_id': 'AAR', 'project_name': 'aardvark', 'project_lead': 'Gavin McDonald', 'project_category': 'No category', 'project_url': 'No URL'}, {'project_id': 'ABDERA', 'project_name': 'Abdera', 'project_lead': 'Garrett Rooney', 'project_category': 'Abdera', 'project_url': 'http://abdera.apache.org'}, {'project_id': 'ACCUMULO', 'project_name': 'Accumulo', 'project_lead': 'Ed Coleman', 'project_category': 'Accumulo', 'project_url': 'https://accumulo.apache.org/'}, {'project_id': 'ACE', 'project_name': 'ACE', 'project_lead': 'Marcel Offermans', 'project_category': 'Ace', 'project_url': 'http://ace.apache.org/'}] [{'project_id': 'YOKO', 'project_name': 'Yoko - CORBA Server', 'project_lead': 'Matt Richard Hogstrom', 'project_category': 'Geronimo', 'project_url': 'http://geronimo.apache.org/yoko/'}, {'project_id': 'ZEPPELIN', 'project_name': 'Zeppelin', 'project_lead': 'Jongyoul Lee', 'project_category': 'Zeppelin', 'project_url': 'https://zeppelin.apache.org'}, {'project_id': 'ZETACOMP', 'project_name': 'Zeta Components', 'project_lead': 'Julien Vermillard', 'project_category': 'Incubator', 'project_url': 'http://incubator.apache.org/projects/zetacomponents.html'}, {'project_id': 'ZOOKEEPER', 'project_name': 'ZooKeeper', 'project_lead': 'Patrick D. Hunt', 'project_category': 'ZooKeeper', 'project_url': 'http://zookeeper.apache.org'}]
    return res


##############################################
# Multi Threading
##############################################
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# Excel Sheet file handling code
def get_project_issues(project : dict) -> list[dict]:
    """Scrapes the issues for a given project and returns the results"""
    url = f"https://issues.apache.org/jira/projects/{project['project_id']}/issues/"
    # toReturn = (project, getIssues(url))
    all_issues = getIssues(url)
    res = []
    for issue in all_issues:
        res.append(addExcelRow(project_id=project["project_id"], 
                    project_name=project["project_name"],
                    project_lead=project["project_lead"],
                    project_category=project["project_category"],
                    project_URL=project["project_URL"],
                    issue_id=issue.get("Id"),
                    issue_heading=issue.get("Title"),
                    issue_type=issue.get("Type"),
                    issue_priority=issue.get("Priority"),
                    issue_status=issue.get("Status"),
                    issue_resolution=issue.get("Resolution"),
                    issue_labels=issue.get("Labels"),
                    issue_external_issue_url=issue.get("External issue URL"),
                    issue_language=issue.get("Language"),
                    issue_environment=issue.get("Environment")))
    return res

ans = []
def scrape_projects(url, threads = 10) -> list[dict]:
    """Scrapes project IDs from the given URL"""
    global ans
    
    res = getProjects(url)
    with open("projects.txt", 'w') as f:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_project = {executor.submit(get_project_issues, project): project for project in res}
            for future in concurrent.futures.as_completed(future_to_project):
                project_key = future_to_project[future]
                try:
                    answer = future.result()
                    f.write(answer)
                    ans.extend(answer)
                except Exception as e:
                    print(f"Error occurred for project {project_key}: {e}")
    return ans

url = "https://issues.apache.org/jira/projects"

threads = 4
ans = scrape_projects( url,threads )
# print(ans)


##############################################
# Writing data to excel sheet
##############################################
def addToExcel(df, list_of_rows):
    df = pd.concat([df, pd.DataFrame(list_of_rows)], ignore_index=True)
    return df

df = pd.DataFrame(columns=["Project Name", "Project Id", "Project Lead", "Project Category", "Project URL", "Issue Id", "Issue Heading", "Issue Type", "Issue Status", "Issue Priority", "Issue Resolution", "Issue Labels", "Issue External Issue URL", "Issue Language", "Issue Environment"])
df = addToExcel(df, ans)
df.to_excel("result.xlsx", index=False)

# url = "https://issues.apache.org/jira/projects"
# res = getProjects( url )
# print( res[:4],res[-4:] )

# url = "https://issues.apache.org/jira/projects/AAR/issues/"
# res = getIssues( url )
# print( ans )
# pprint.pprint( res[-2:] )

# ans = {}
# for key in res:
#     url = f"https://issues.apache.org/jira/projects/{key}/issues/"
#     ans[key] = getIssues( url )

# print(ans.items()[-1])



# Single Function()
# demo = {"Title": "Demo", "Description": "ASDF"}
# demon = {"Title": "demon"}
# # print(demo["Pasta"])
# # print(demo)
# def serializeData(data: list[dict]):
#     res = []
#     for k,v in data.iteritems():
#         print(k,v)
