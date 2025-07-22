from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.hybrid import hybrid_property

from app.models import CommonBase, Job


class JobScraped(Job):
    pass


class JobEmails(CommonBase):
    email_id = Column(String, primary_key=True, nullable=False)  # Gmail message ID
    subject = Column(String)
    sender = Column(String)
    date_received = Column(String)
    platform = Column(String)
    job_ids = Column(JSON)

    @hybrid_property
    def job_count(self):
        """Get count of job IDs"""
        return len(self.job_ids) if self.job_ids else 0

    def add_job_id(self, job_id: str):
        """Add a job ID to the list"""
        if self.job_ids is None:
            self.job_ids = []
        if job_id not in self.job_ids:
            self.job_ids.append(job_id)
