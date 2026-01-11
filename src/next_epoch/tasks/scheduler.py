"""Scheduler for background tasks using APScheduler."""

from datetime import datetime

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from next_epoch.config import get_settings
from next_epoch.tasks.ingestion import run_ingestion
from next_epoch.schemas.enums import SourceType

logger = structlog.get_logger()
settings = get_settings()


class TaskScheduler:
    """Scheduler for background ingestion and processing tasks."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False

    def start(self):
        """Start the scheduler with configured jobs."""
        if self._is_running:
            logger.warning("Scheduler already running")
            return

        # Add arXiv ingestion job
        self.scheduler.add_job(
            self._run_arxiv_ingestion,
            trigger=IntervalTrigger(minutes=settings.ingestion_interval_minutes),
            id="arxiv_ingestion",
            name="arXiv Ingestion",
            replace_existing=True,
            next_run_time=datetime.utcnow(),  # Run immediately on start
        )

        # Add GitHub ingestion job
        self.scheduler.add_job(
            self._run_github_ingestion,
            trigger=IntervalTrigger(minutes=settings.ingestion_interval_minutes),
            id="github_ingestion",
            name="GitHub Trending Ingestion",
            replace_existing=True,
            next_run_time=datetime.utcnow(),  # Run immediately on start
        )

        self.scheduler.start()
        self._is_running = True

        logger.info(
            "Scheduler started",
            ingestion_interval=settings.ingestion_interval_minutes,
        )

    def stop(self):
        """Stop the scheduler."""
        if not self._is_running:
            return

        self.scheduler.shutdown(wait=True)
        self._is_running = False
        logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running

    def get_jobs(self) -> list[dict]:
        """Get list of scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs

    async def trigger_job(self, job_id: str) -> bool:
        """Manually trigger a job to run now."""
        job = self.scheduler.get_job(job_id)
        if not job:
            logger.warning("Job not found", job_id=job_id)
            return False

        # Run the job function directly
        await job.func()
        return True

    @staticmethod
    async def _run_arxiv_ingestion():
        """Run arXiv ingestion job."""
        logger.info("Running scheduled arXiv ingestion")
        try:
            await run_ingestion(SourceType.ARXIV)
        except Exception as e:
            logger.error("Scheduled arXiv ingestion failed", error=str(e))

    @staticmethod
    async def _run_github_ingestion():
        """Run GitHub ingestion job."""
        logger.info("Running scheduled GitHub ingestion")
        try:
            await run_ingestion(SourceType.GITHUB)
        except Exception as e:
            logger.error("Scheduled GitHub ingestion failed", error=str(e))


# Global scheduler instance
_scheduler: TaskScheduler | None = None


def get_scheduler() -> TaskScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
