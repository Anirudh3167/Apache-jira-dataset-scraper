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
import json

MAX_ISSUES_PER_PROJECT = 0

# Maximum number for PROJECT_COUNT is 663 
PROJECT_COUNT = 663

url = "https://issues.apache.org/jira/projects"
threads = 10
s, l = 0, 20

PROJECTS_ONLY = False

df = pd.DataFrame(columns=["Project Name", "Project Id", "Project Lead", "Project Category", "Project URL", "Project Issue Count", "Issue Id", "Issue Heading", "Issue Type", "Issue Status", "Issue Priority", "Issue Resolution", "Issue Labels", "Issue External Issue URL", "Issue Language", "Issue Environment"])
df_projects_only = pd.DataFrame(columns=["Project Name", "Project Id", "Project Lead", "Project Category", "Project URL", "Issue Count"])

def scrapeIssuesPagination(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # Find the number of issues.
    issue_count = int(soup.find('div', class_='pagination').get('data-displayable-total',0))
    # print(f'The project contains {issue_count} number of issues')
    return issue_count
    
def getIssueIdNumber(url):
    # Load the html page
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))
    content = driver.page_source
    driver.quit()
    return scrapeIssuesPagination(content)
    

##############################################
# Serialization
##############################################
def addExcelRow(project_name, project_id, project_lead, project_category, project_URL,project_issue_count, issue_id, issue_heading, issue_type, issue_status, issue_priority, issue_resolution, issue_labels, issue_external_issue_url, issue_language, issue_environment):
    res_dict = {}
    res_dict["Project Name"] = project_name
    res_dict["Project Id"] = project_id
    res_dict["Project Lead"] = project_lead
    res_dict["Project Category"] = project_category
    res_dict["Project URL"] = project_URL
    res_dict["Project Issue Count"] = project_issue_count
    res_dict["Issue Id"] = issue_id
    res_dict["Issue Heading"] = issue_heading
    res_dict["Issue Type"] = issue_type 
    res_dict["Issue Status"] = issue_status
    res_dict["Issue Priority"] = issue_priority
    res_dict["Issue Resolution"] = issue_resolution 
    res_dict["Issue Labels"] = issue_labels
    res_dict["Issue External Issue URL"] = issue_external_issue_url
    res_dict["Issue Language"] = issue_language
    res_dict["Issue Environment"] = issue_environment
    return res_dict


##############################################
# Writing data to excel sheet
##############################################
def addToExcel(df, list_of_rows):
    df = pd.concat([df, pd.DataFrame(list_of_rows)], ignore_index=True)
    return df

def add_element_to_dict(input_dict, key, value):
    input_dict["Project Name"] = input_dict.pop("project_name")
    input_dict["Project Id"] = input_dict.pop("project_id")
    input_dict["Project Lead"] = input_dict.pop("project_lead")
    input_dict["Project Category"] = input_dict.pop("project_category")
    input_dict["Project URL"] = input_dict.pop("project_URL")
    input_dict[key] = value
    return input_dict

##############################################
# Issues Extraction
##############################################
def getIssueDetails(content):
    """ Uses Beautiful soup and returns the details for current html page"""
    soup = BeautifulSoup(content, "html.parser")
    ans = {}
    try:
        rows = soup.find_all('li', class_='item')
        issue_title = soup.find('h1', {"id": "summary-val"}).text
        issue_id = soup.find('a', {"id": "key-val"}).text
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

            ans[head[:-1]] = val
        # print(ans)
        # {'Id': 'AAR-51816', 'Title': 'Balloons in Dubai - delivery on the same day | Online Helium balloon Store for party, birthday', 'Type:': 'Bug', 'Status:': 'Open', 'Priority:': 'Major', 'Resolution:': 'Unresolved', 'Labels:': 'Not Found', 'External issue URL:': 'Not Found'}
    except Exception as e:
        print("Error found in getIssueDetails : ", e)
    return ans

def getIssues(url) -> list[dict]:
    """ Loads each and every issue details of a project """
    res = [] # list of dicts

    # Load the html page
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 2)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))

    # Simulate next click (until next is not found)
    pg = 0
    issue_count = 0
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

            # TODO:  REMOVE this when pushing to production
            if issue_count >= MAX_ISSUES_PER_PROJECT:
                return res
            issue_count += 1
            
            
        # Simulate the next click
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
    driver.quit()
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
        res = {}
        res['project_id'] = row.find("td", {"class": "cell-type-key"}).text
        res['project_name'] = row.find("a", {"href": True}).text
        res['project_lead'] = row.find("td", {"class": "cell-type-user"}).text
        res['project_category'] = row.find("td", {"class": "cell-type-category"}).text
        res['project_URL'] = row.find("td", {"class": "cell-type-url"}).text
        result_list.append(res)
    return result_list

# iterates over the 27 sections to get projects of all
def getProjects(url) -> list[dict]:
    """ Loads the page via selenium and returns the Project Ids """
    res = []

    # Load the html page
    driver = webdriver.Chrome()  
    driver.get(url)
    wait = WebDriverWait(driver, 3)
    projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
    
    # Get the project ids in that page.
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



# v = []
# for u in res:
#     v.append( getIssueIdNumber(u[""]) )
                                

##############################################
# Multi Threading
##############################################
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# Excel Sheet file handling code
def get_project_issues(project : dict) -> list[dict]:
    """Scrapes the issues for a given project and returns the results"""
    url = f"https://issues.apache.org/jira/projects/{project['project_id']}/issues/"
    
    print("Getting issues for project " + project["project_name"])
    all_issues = getIssues(url)
    total_issue_count = getIssueIdNumber(url)
    # print("Found " + str(len(all_issues)) + " issues out of " + str(total_issue_count) + " for " + project["project_name"])
    
    project["issue_count"] = total_issue_count
    
    res = []
    # for issue in all_issues:
    #     add_element_to_dict(issue, "Issue Count", total_issue_count)
    
    for issue in all_issues:
        res.append(addExcelRow(project_id=project["project_id"], 
                    project_name=project["project_name"],
                    project_lead=project["project_lead"],
                    project_category=project["project_category"],
                    project_URL=project["project_URL"],
                    project_issue_count=project["issue_count"],
                    issue_id=issue.get("Id", "Not Found"),
                    issue_heading=issue.get("Title", "Not Found"),
                    issue_type=issue.get("Type", "Not Found"),
                    issue_priority=issue.get("Priority", "Not Found"),
                    issue_status=issue.get("Status", "Not Found"),
                    issue_resolution=issue.get("Resolution", "Not Found"),
                    issue_labels=issue.get("Labels", "Not Found"),
                    issue_external_issue_url=issue.get("External issue URL", "Not Found"),
                    issue_language=issue.get("Language", "Not Found"),
                    issue_environment=issue.get("Environment", "Not Found")))
    return res


#----------------------------------------------------------------
# Get all project data
res = getProjects(url)[:PROJECT_COUNT]

# Can be saved seperately
#----------------------------------------------------------------


def scrape_projects(url, threads = 10, start=0, limit = 10) -> list[dict]:
    """Scrapes project IDs from the given URL"""
    global res, df, df_projects_only 
    res1 = res[start:start + limit]
    ans = []
    if not PROJECTS_ONLY:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_project = {executor.submit(get_project_issues, project): project for project in res1}
            for future in concurrent.futures.as_completed(future_to_project):
                project_key = future_to_project[future]
                try:
                    answer = future.result()
                    with open("projects.txt", 'a') as f:
                        f.write(json.dumps(answer))
                        f.close()
                    print( "Saved project : ", project_key["project_name"])
                    ans.extend(answer)
                except Exception as e:
                    print(f"Error occurred for project {project_key['project_name']}: {e}")
                    
        df = addToExcel(df, ans)
    else:
        
        #######################################
        
        # MAKE ME MULTI-THREADED 
        # I want to get 663 projects in parallel
        
        #######################################
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_project = {executor.submit(add_element_to_dict, ["Issue Count", getIssueIdNumber(f"https://issues.apache.org/jira/projects/{project['project_id']}/issues/")]) : project for project in res1}
            for future in concurrent.futures.as_completed(future_to_project):
                project_key = future_to_project[future]
                try:
                    answer = future.result()
                    ans.extend(answer)
                except Exception as e:
                    pass
                
        # This will work serially
        # ans = [add_element_to_dict(project, "Issue Count", getIssueIdNumber(f"https://issues.apache.org/jira/projects/{project['project_id']}/issues/")) for project in res1]
    df_projects_only = addToExcel(df_projects_only, ans)

# for all 663 projects
while (s < len(res)):
    scrape_projects(url,threads, s, l)
    s += l
# print(ans)
if not df_projects_only.empty:
    df_projects_only.to_excel("projects_data.xlsx", index=False)
if not df.empty:
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
