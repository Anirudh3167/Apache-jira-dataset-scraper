# Imports
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv,  os, pprint

###################################
# Global Configs
file_path = './project_scraped_dataset.csv'
storage = []
page_count = 0


###################################
# Serializer
def ProjectsSerializer(project_details):
    order = ['Project Name', 'Project Id', 'Project URL', "Project Lead", 'Number of Issues']
    res = []

    for i in order:
      res.append(project_details.get(i,"Not Found"))
    return res


###################################
# Add to CSV
def AddToCSV():
  global file_path, storage

  # Create a csv file along with heading if not exists
  if not os.path.isfile(file_path):
    with open(file_path, 'w', newline='') as f:
      writer = csv.writer(f)
      # Headings
      writer.writerow(['Project Name', 'Project Id', 'Project URL', "Project Lead", 'Number of Issues'])
      
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

def getProjects( url ):
  """ Returns project details """
  global page_count
  res = []
#   url = "https://issues.apache.org/jira/projects"
  # Load the html page
  driver = webdriver.Chrome()  
  driver.get(url)
  wait = WebDriverWait(driver, 1)
  projects_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
  
  # Get the project ids in that page.
  count = 0
  final_res = []
  project_res = getProjectDetails( driver.page_source )

  # Simulate the click of a project.
  count = 0
  while count < 25:
    try:
        link = driver.find_elements(By.CSS_SELECTOR,'td.cell-type-name > a')
        link[count].click()
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading")))
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "list-content")))
        project_res[count]['Number of Issues'] = driver.find_element(By.CSS_SELECTOR, "div.pagination").get_attribute("data-displayable-total") 
    except:
        project_res[count]['Number of Issues'] = '0'
    final_res.append( ProjectsSerializer(project_res[count]) )
    driver.back()
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading")))
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "projects-list")))
    count += 1
  print('Extraction of project details copmleted till ',page_count)
  page_count += 1
  driver.quit()
  # print(res) # all 668 rows
  return final_res

# final_res = getProjects()

# pprint.pprint( final_res )


def MultiThreading():
   
  page_urls = [f'https://issues.apache.org/jira/projects?selectedCategory=all&selectedProjectType=all&sortColumn=name&sortOrder=ascending&s=view_projects&page={i}' for i in range(1,28)]
  # Deploy multiple threads.
  print('Multi Threading Activated')
  with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(getProjects, url) for url in page_urls]
    # Retrieve results from each thread
    for future in futures:
       storage.extend(future.result())
  print('Multi threading completed')
  # Write the data to csv file
  AddToCSV()
  print('Data Successfully Added to CSV')

MultiThreading()