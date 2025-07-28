# import atexit
# from datetime import datetime
#
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger
#
# from app.database import get_db
# from app.eis.emails import GmailScraper
# from app.eis.models import JobscraperSettings
# from app.utils import get_scheduler_logger, AppLogger
#
# logger = get_scheduler_logger()
#
#
# class EmailJobScheduler:
#     """Email job scheduler class"""
#
#     def __init__(self) -> None:
#         """Class constructor"""
#
#         self.scheduler = BackgroundScheduler()
#         self.gmail_scraper = None
#         logger.info("EmailJobScheduler initialised")
#
#     def init_scheduler(self) -> None:
#         """Initialize the scheduler with jobs"""
#
#         logger.info("Initialising scheduler")
#
#         # Get settings from database
#         session = next(get_db())
#         settings = session.query(JobscraperSettings).first()
#
#         if settings:
#             period_hours = settings.period
#             logger.info(f"Using database period setting: {period_hours} hours")
#         else:
#             period_hours = 12
#             logger.warning(f"No period settings found, using default: {period_hours} hours")
#
#         # Schedule the job scraping task
#         self.scheduler.add_job(
#             func=self.scrape_job_emails,
#             trigger=IntervalTrigger(hours=period_hours),
#             id='job_email_scraper',
#             name='Job Email Scraper',
#             replace_existing=True,
#             max_instances=1
#         )
#
#         self.scheduler.start()
#         logger.info(f"Scheduler started with {period_hours} hour interval")
#
#         # Shut down scheduler on exit
#         atexit.register(lambda: self.scheduler.shutdown())
#
#     def scrape_job_emails(self) -> None:
#         """Main job scraping function"""
#
#         start_time = datetime.now()
#         logger.info("Starting scheduled job email scraping")
#
#         try:
#             # Initialize Gmail scraper if needed
#             if not self.gmail_scraper:
#                 self.gmail_scraper = GmailScraper()
#                 logger.info("Gmail scraper initialised")
#
#             # Run the scraping workflow
#             stats = self.gmail_scraper.run()
#
#             # Log results
#             AppLogger.log_execution_time(logger, start_time, "Scheduled job scraping")
#             AppLogger.log_stats(logger, stats, "Scheduled Scraping Results")
#
#         except Exception as e:
#             logger.error(f"Error during scheduled job scraping: {e}")
#
#
# # Global scheduler instance
# email_scheduler = EmailJobScheduler()
