<h1 align="center"> Apache-jira-dataset-scraper </h1>
This is just a research purpose dataset scraper for the apache jira

# How it works?
- Run the web scrapper.
- This will create multiple threads.
- Each thread simulates a browser action.
- Thus it will first gather all the project issue links.
- Then extract the data for each issue link.

# Current Progress
## Pre scraping Research
- [ ] Multi Threading (Max threads to be deployed)
- [ ] Page load strategy (eager, Normal)
- [ ] Headless in header (to reduce the checks)
- [ ] Cracking common patterns (like issue number is auto increment int field)
- [ ] Distributed Facility (like three page limiting for the extraction)
- [ ] Strategies to be considered for the efficient concurrency

## Post scraping Rsearch
- [ ] Dataset file
- [ ] Various graph plottings
