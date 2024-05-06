import csv

def serializeEntry( entry, ref="project scrapper" ):
  """ Serializes the data and adds a Not Found if not found """
  res = []
  if ref == "project scrapper":
    order = ["project Name", "project Id", "project Url", "num_issues"]
  else:
    # The order of issues data + projects data
    pass
  for i in entry:
    res.append( entry.get(i,"Not Found") )
  return res


def AddToCSV( entry,fname="scraped_dataset.csv" ):
  with open( fname,'a+' ) as f:
    csv.writer(f).writerow( serializeEntry(entry) )

def ProjectScrapper():
  """ Returns project details with number of issues """
  pass

def getProjects():
  """ Returns project details """
  pass

def getIssuesDetails( project_id ):
  """ returns the details of all issues of a project """
  pass

def IssuesScraper( project_details ):
  """ Uses Multi Threading and returns Issue details """
  pass

def ProjectSpecificIssuesScrapper( project_ids ):
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
    ProjectScrapper()
  elif ask in ("2","issues scrapper"):
    IssuesScrapper( getProjects() )
  elif ask in ("3","project specific issues"):
    ask = input("Enter Project IDs With [#SEP#] as Seperator:")
    ProjectSpecificIssuesScrapper( ask.split("[#SEP#]") )
  elif ask in ("4","exit"):
    return
  else:
    print("Invalid Choice")
    ScraperOptions()
 
def __init___():
  ScraperOptions()
