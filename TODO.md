## TODO

### Bugs
* [ ] Modals darken when a help bubble is displayed.
* [X] The theme shown in the user setting page is not updated when changed in the sidebar.
* [X] The content of job application update and interview modals are not updated after an edit when opened through the job modal.
* [ ] the sidebar is not expanding properly on small screens on the job page.
* [X] Source aggregator is sometimes not shown when editing a job
* [X] Move the logs to an absolute location
* [X] Improve rhe raspberry theme contrast
* [X] Incomplete job application updates are shown in the dashboard

### TOAST
* [X] Ensure that the parsed country matches the list of available countries
* [X] Add currency parsing
* [X] Add admin control and monitoring page
* [X] Add graphs showing the results of previous service logs
* [ ] Add frontend tests
* [X] Deleting/deactivating is not working
* [ ] If no currency is found, use the default currency
* [X] Load the currencies and countries from the backend instead of the frontend
* [X] Add search box
* [X] If the company/location match is not good enough, do not suggest it
* [X] Add the total number of scraped jobs
* [X] Display the most common failures
* [X] Display critical failures
* [ ] Add AI rating for the jobs
* [ ] Add the ability to filter out jobs (extract the job title when extracting the job ids). Mark the job as filtered
* [X] Add NHS job alert support
* [X] Add the ability to display the results for the selected platform only
* [X] Add new endpoint for admin only that allows to query specific job ids (as a list)
* [X] Add job alert name extraction

### Select Widgets Improvements
* [X] Sort options alphabetically
* [X] After adding an option, select it automatically
* [ ] Display the entry associated with the hovered option
* [X] Show the company name in job and person selects

### Job Modal Improvements
* [ ] Add option to select the source (recruiter, aggregator, other)
* [X] Add option for application on company website

### Spontaneous Applications
* [ ] Add spontaneous application table with the following columns:
  * [ ] Company
  * [ ] Date Sent
  * [ ] Notes
  * [ ] Email sent to

### Email Generation
* [ ] Add the ability to generate a follow-up email and select the contact to send it to

### Active Jobs Widget
* [ ] Add a "active jobs" log showing jobs with the most activity
* [ ] Add a "favourite" column to the job table

### Tables
* [ ] Move the scrollbar inside the tables so that the header is always visible
* [ ] Add the ability to filter by columns and hide rejected jobs

### Users
* [X] Add test user setting and prevent update of email and password
* [X] Make sure the user is reloaded properly when the settings are changed

### New Modals
* [X] Interview modals should show the edited value after being edited from the job modal
* [X] Multiple modals of the same type should be able to be opened at the same time 
