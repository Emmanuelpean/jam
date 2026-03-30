import dashboardPng from "../assets/screenshots/dashboard.png";

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
<img src="${dashboardPng}" alt="Customisable dashboard" width="100%" style="padding: 0 5rem;" />

<h5>Customisable Table Columns</h5>
<ul>
    <li>All data tables now support column customisation. You can show or hide individual columns to focus on the information that matters most to you.</li>
    <li>Column configuration is accessible via the settings icon in the table toolbar. Your column preferences are saved per table.</li>
</ul>

<h5>Favourite Filters for Scraped Jobs</h5>
<ul>
    <li>You can now save favourite filter configurations on the Job Alerts page. Saved filter sets can be applied with a single click, making it faster to switch between different views of your scraped jobs.</li>
    <li>A dedicated <strong>Favourite Job Alerts</strong> dashboard widget displays jobs that match your saved favourite filters at a glance.</li>
</ul>

<h5>Quality of Life Improvements</h5>
<ul>
    <li>Hovering over an option in a company, location, contact, or aggregator dropdown now shows a floating preview card with key details, so you can identify the right entry without opening it.</li>
</ul>
`;
