import followupGif from "../assets/demo_gifs/followup_email.gif";
import speculativeApplicationGif from "../assets/demo_gifs/speculative_application.gif";
import scrapingFilterGif from "../assets/demo_gifs/scraping_filter.gif";
import scrapedJobsPng from "../assets/screenshots/scraped-jobs.png";

export default `<h4>Version 1.2.0</h4>

<h5>Job Scraping Filters</h5>
<ul>
    <li>Jobs that are scraped from job alert emails through TOAST can now be filtered out by creating custom filtering rules.</li>
    <li>Scraping filters can be easily managed in the Job Alerts table on your dashboard. Any job that matches one of your active filters will be automatically excluded from the table.</li>
    <li><strong>Filter Type:</strong> This determines which job parameter you want to filter by (for example, Company Name or Job Title).</li>
    <li><strong>Operator:</strong> This specifies how the filter should compare values (for example, Equals To for an exact match, or Contains for partial matches).</li>
    <li><strong>Value:</strong> This is the specific value that the job data should be compared against.</li>
    <li><strong>Example:</strong> If you do not want to see jobs from a company called XYZ, you can create a filter with the following parameters: Company Name → Equals To → XYZ.</li>
    <li>Filters can be temporarily deactivated or permanently deleted as needed. However, filters that have already been used to exclude specific jobs can only be deactivated rather than deleted. You can view the complete list of jobs that have been filtered out by each filter in the filter details section.</li>
</ul>
<img src="${scrapingFilterGif}" alt="Follow-up email demo" width="100%" style="padding: 0 5rem;" />

<h5>Speculative Applications</h5>
<ul>
    <li>A new dedicated page has been added specifically for tracking speculative and spontaneous job applications.</li>
    <li>Each application entry stores comprehensive details including the company name, the date and time of submission, the email address used to contact the company, a list of relevant contacts at the organisation, and any additional notes you wish to record.</li>
</ul>
<img src="${speculativeApplicationGif}" alt="Follow-up email demo" width="100%" style="padding: 0 5rem;" />

<h5>Follow-Up Email Generator</h5>
<ul>
    <li>Follow-up emails can now be generated automatically for any specific job application in your tracker.</li>
    <li>To use this feature, simply right-click on a job in the job table and select the "Follow-up Email" option from the context menu.</li>
    <li>You can then choose which person you would like to send the email to, and the system will automatically generate a personalised email for that individual.</li>
    <li>The job title is automatically pre-filled in the email content. If the contact you have selected is marked as a recruiter, the company name will also be included in the email.</li>
    <li>All generated emails are automatically signed using the first and last name stored in your user settings.</li>
</ul>
<img src="${followupGif}" alt="Follow-up email demo" width="100%" style="padding: 0 5rem;" />

<h5>TOAST</h5>
<ul>
    <li>TOAST (Turn Opportunity Alerts into Structured Tracking) is a premium feature that automates the extraction and organisation of job alert data from various platforms.</li>
    <li>By automatically forwarding or redirecting job alert emails to a designated address, TOAST parses the content to extract key details such as job title, company, location, and salary.</li>
    <li>The extracted data is then structured and presented in an easy-to-navigate table on the main dashboard.</li>
    <li>Furthermore, each job is rated by an LLM based on the user qualifications set on their user page.</li>
    <li>You can now subscribe to TOAST in your user settings under "Premium". New users can try TOAST for 14 days for free.</li>
</ul>
<img src="${scrapedJobsPng}" alt="TOAST demo" width="100%" style="padding: 0 5rem;" />

<h5>Quality of Life Improvements</h5>
<ul>
    <li>You can now update your first and last name directly in the user settings page.</li>
    <li>A new option has been added to the person details page, allowing you to mark individual contacts as recruiters.</li>
    <li>Badge data (e.g. company) can now be edited or deleted directly via right-click</li>
    <li>Data export in the user settings now exports speculative application data and scraped job data.</li>
    <li>The source of a job can now be specified as Recruiter, Recruitment Company, Aggregator, Aggregator Email or Other.</li>
    <li>Error message have been improved. Right clicking on error toast messages allows the user to send an email to JAM support.</li>
    <li>Dark mode has been added.</li>
    <li>The user settings have been reworked.</li>
    <li>The AI prompt used to rate scraped jobs is now displayed in the scraped job modal.</li>
    <li>User accounts can now be deleted in the user settings.</li>
    <li>Jobs with a Rejected, Offered, or Withdrawn application status are not shown in the Needs Chase table</li>
</ul>

<h4 style="margin-top: 3rem;">Version 1.2.1</h4>

<ul>
    <li>Added limits to scraped job description, title and company length for AI rating.</li>
    <li>Fixed a bug hidding the scraped job location in the demo user.</li>
    <li>Improved the feedback regarding job scraping and rating in the Scraped Job Modals</li>
</ul>
`;
