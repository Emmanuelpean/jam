import dashboardCustomisationGif from "../assets/demo_gifs/dashboard_customisation.gif";

export default `<h4>Version 1.3.0</h4>

<h5>Customisable Dashboard</h5>
<ul>
    <li>The dashboard is now fully customisable. You can add, remove, resize, and rearrange widgets to suit your workflow.</li>
    <li>To enter edit mode, click the pencil icon on the right side of the dashboard. Once in edit mode, widgets can be dragged by their handle and resized from any corner.</li>
    <li>New widgets can be added via the widget picker, which organises available widgets into five categories: Metric, Table, Timeline, Graph, and Map.</li>
    <li><strong>Metric widgets</strong> display a single key number such as Total Jobs, Active Applications, Interview Rate, or Average Response Time.</li>
    <li><strong>Table widgets</strong> show data lists such as Follow-up Required, Upcoming Deadlines, Job Alerts, Favourite Job Alerts, Favourite Jobs, and Failed Jobs.</li>
    <li><strong>Timeline widgets</strong> display activity feeds and schedules, including Recent Activity, Upcoming Interviews, Past Interviews, Status Updates, and Upcoming Deadlines.</li>
    <li><strong>Graph widgets</strong> provide chart visualisations of your data. Choose from featured presets or build a custom graph by selecting the data source, field, chart type (line, bar, or pie), and time granularity.</li>
    <li><strong>Map widgets</strong> show a geographic view of your jobs, with options to display job count, average salary, or top keywords by location.</li>
    <li>Your layout is saved automatically when you click the save button. You can reset the dashboard to its default layout at any time.</li>
</ul>
<img src="${dashboardCustomisationGif}" alt="Customisable dashboard" width="100%" style="padding: 0 5rem;" />

<h5>Customisable Tables & Advanced Filtering</h5>
<ul>
    <li>All data tables now support column customisation. Click the settings icon in the table toolbar to show or hide individual columns — your preferences are saved per table.</li>
    <li>Table data can now be filtered using the filter sidebar. Access it via the filter icon in the table toolbar to narrow results by any available field. For example, on the Scraped Jobs table you can filter by AI rating to show only jobs with rating higher than 8.</li>
    <li>Scraped jobs now support multi-select. Use the checkboxes to select multiple jobs at once and perform bulk actions such as deleting them or deleting expired jobs.</li>
</ul>

<h5>Favourite Filters for Scraped Jobs</h5>
<ul>
    <li>You can now save favourite filter configurations on the Job Alerts page. Saved filter sets can be applied with a single click, making it faster to switch between different views of your scraped jobs.</li>
    <li>A dedicated <strong>Favourite Job Alerts</strong> dashboard widget displays jobs that match your saved favourite filters at a glance.</li>
</ul>

<h5>CV & Cover Letter Attachments</h5>
<ul>
    <li>You can now attach a CV and cover letter directly to a job application. Files can be uploaded by clicking the upload area or dragging and dropping them in.</li>
    <li>PDFs and images can be previewed inline without leaving the modal. Other file types such as Word documents can be downloaded directly.</li>
    <li>Cover letters stored as plain text can be written and edited directly in the modal using the built-in text editor.</li>
</ul>

<h5>Command Palette</h5>
<ul>
    <li>A command palette is now available to quickly navigate to any page or trigger actions without leaving the keyboard. Open it with <strong>Ctrl+K</strong> (or <strong>⌘K</strong> on Mac), type to filter, and press Enter to execute.</li>
</ul>

<h5>Guided Tour</h5>
<ul>
    <li>A guided tour is now available to help you get familiar with JAM. Start it from the sidebar under <strong>Take a Tour</strong>. The tour walks you through the key features step by step and can be paused and resumed at any time.</li>
</ul>

<h5>Quality of Life Improvements</h5>
<ul>
    <li>Hovering over an option in a company, location, contact, or aggregator dropdown now shows a floating preview card with key details, so you can identify the right entry without opening it.</li>
    <li>Locations are now stored as plain text instead of being linked to a separate location record. This simplifies data entry and removes the need to manage a separate locations table.</li>
    <li>The Jobs table now has a <strong>Hide rejected / withdrawn</strong> toggle inside the application status filter, letting you quickly exclude closed applications from view.</li>
    <li>The Premium settings page now shows a warning when job rating is active but your qualification profile is incomplete, with a direct link to fill in the missing fields.</li>
</ul>
`;
