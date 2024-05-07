from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv,  os

###################################
# Global Configs
file_path = './project_scraped_dataset.csv'
storage = []

def ProjectsSerializer(project_details):
    order = ['Project Name', 'Project Id', 'Project URL', "Project Lead", 'Number of Issues']
    res = []
    for i in order:
      res.append(project_details.get(i,"Not Found"))
    return res

def AddToCSV():
  global file_path, storage

  # Create a csv file along with heading if not exists
  file_path = './webScrapped.csv'
  if not os.path.isfile(file_path):
    with open(file_path, 'w', newline='') as f:
      writer = csv.writer(f)
      if file_path == './project_scrapped_dataset.csv':
        writer.writerow(['Project Name', 'Project Id', 'Project URL', "Project Lead", 'Number of Issues'])
      else:
        # Elaborate the issue details
        writer.writerow(['Project Name', 'Project Id', 'Project URL', "Project Category", "Project Lead", 'Issue Id', 'Issue Heading', 'Issue Details'])

  # append the entries to the csv file
  with open( file_path,'a+' ) as f:
    csv.writer(f).writerows( storage )
  
  storage = []

def getProjectDetails(page):
  """ Extracts the useful insights from the projects page """
  result_list = []
  soup = BeautifulSoup(page, "html.parser")
  rows = soup.find_all("tr", {"data-project-id": True})
  for row in rows:
      res = {}
      res['Project Name'] = row.find("a", {"href": True}).text
      res['Project Id'] = row.find("td", {"class": "cell-type-key"}).text
      res['Project URL'] = row.find("td", {"class": "cell-type-url"}).text
      res['Project Category'] = row.find("td", {"class": "cell-type-category"}).text
      res['Project Lead'] = row.find("td", {"class": "cell-type-user"}).text
      result_list.append(res)
  return result_list

def getProjects():
  """ Returns project details """
  res = []
  url = "https://issues.apache.org/jira/projects"
  # Load the html page
  driver = webdriver.Chrome()  
  driver.get(url)
  wait = WebDriverWait(driver, 5)
  projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
  
  # Get the project ids in that page.
  res.extend( getProjectDetails(driver.page_source))

  # Simulate the click (Until next is enabled)
  while True:
      link = driver.find_element(By.CSS_SELECTOR, "li.aui-nav-next > a")
      if link is None or link.get_attribute("aria-disabled") == "true":
        break
      link.click()
      # Wait till the data gets loaded then get the current html page
      projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
      # Get the project ids in that page.
      res.extend( getProjectDetails(driver.page_source) )
  print('Extraction of project details copmleted')
  driver.quit()
  # print(res) # all 668 rows
  return res

def getIssuesNumber(project_details):
  """ Returns the number of issues in a single project """
  global storage
  url = f"https://issues.apache.org/jira/projects/{project_details['Project Id']}/issues/"
  driver = webdriver.Chrome()  
  driver.get(url)
  wait = WebDriverWait(driver, 5)
  projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-content")))
  # Get the count of the issues
  project_details['Number of Issues'] = driver.find_element(By.CSS_SELECTOR, "div.pagination").get_attribute("data-displayable-total") 
  driver.quit()
  return ProjectsSerializer(project_details)

def ProjectScraper():
  """ Returns project details with number of issues """
  projects = getProjects()
  global storage

  # Deploy multiple threads.
  print('Multi Threading Activated')
  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(getIssuesNumber, project) for project in projects]
    # Retrieve results from each thread
    storage = [future.result() for future in futures]
  print('Multi threading completed')
  # Write the data to csv file
  AddToCSV()
  print('Data Successfully Added to CSV')


def getIssuesDetails( project_id ):
  """ returns the details of all issues of a project """
  pass

def IssuesScraper( project_details ):
  """ Uses Multi Threading and returns Issue details """
  pass

def ProjectSpecificIssuesScraper( project_ids ):
  """ Gets the project details and issue details for a specific project """
  pass

def ScraperOptions():
  print("***************************************")
  print("* 1. Project Scrapper                 *")
  print("* 2. Issues Scrapper                  *")
  print("* 3. Project Specific Issues Scrapper *")
  print("* 4. exit                             *")
  print("***************************************")  
  ask = input("Select your Option: ").lower()

  if ask in ("1","project scrapper"):
    ProjectScraper()
  elif ask in ("2","issues scrapper"):
    IssuesScraper( getProjects() )
  elif ask in ("3","project specific issues"):
    ask = input("Enter Project IDs With [#SEP#] as Seperator:")
    ProjectSpecificIssuesScraper( ask.split("[#SEP#]") )
  elif ask in ("4","exit"):
    return
  else:
    print("Invalid Choice")
    ScraperOptions()
 

ScraperOptions()
