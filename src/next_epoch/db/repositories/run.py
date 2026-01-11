"""Processing run repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.db.models import ProcessingRunModel
from next_epoch.db.repositories.base import BaseRepository
from next_epoch.schemas.enums import RunStatus, RunType, SourceType


class ProcessingRunRepository(BaseRepository[ProcessingRunModel]):
    """Repository for processing runs."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ProcessingRunModel)

    async def list_runs(
        self,
        *,
        run_type: RunType | None = None,
        status: RunStatus | None = None,
        source: SourceType | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ProcessingRunModel], int]:
        """List processing runs with filtering."""
        from sqlalchemy import func

        stmt = select(ProcessingRunModel)
        count_stmt = select(func.count()).select_from(ProcessingRunModel)

        if run_type:
            stmt = stmt.where(ProcessingRunModel.type == run_type.value)
            count_stmt = count_stmt.where(ProcessingRunModel.type == run_type.value)

        if status:
            stmt = stmt.where(ProcessingRunModel.status == status.value)
            count_stmt = count_stmt.where(ProcessingRunModel.status == status.value)

        if source:
            stmt = stmt.where(ProcessingRunModel.source == source.value)
            count_stmt = count_stmt.where(ProcessingRunModel.source == source.value)

        # Order by started_at desc
        stmt = stmt.order_by(ProcessingRunModel.started_at.desc())

        # Get count
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Paginate
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        runs = list(result.scalars().all())

        return runs, total

    async def start_run(
        self,
        run_type: RunType,
        source: SourceType | None = None,
    ) -> ProcessingRunModel:
        """Create a new processing run with RUNNING status."""
        run = ProcessingRunModel(
            id=self.generate_id(),
            type=run_type.value,
            status=RunStatus.RUNNING.value,
            source=source.value if source else None,
            started_at=datetime.utcnow(),
        )
        return await self.create(run)

    async def complete_run(
        self,
        run: ProcessingRunModel,
        *,
        stats: dict | None = None,
    ) -> ProcessingRunModel:
        """Mark a run as succeeded."""
        run.status = RunStatus.SUCCEEDED.value
        run.finished_at = datetime.utcnow()
        run.stats = stats
        return await self.update(run)

    async def fail_run(
        self,
        run: ProcessingRunModel,
        *,
        error: str,
        stats: dict | None = None,
    ) -> ProcessingRunModel:
        """Mark a run as failed."""
        run.status = RunStatus.FAILED.value
        run.finished_at = datetime.utcnow()
        run.error = error
        run.stats = stats
        return await self.update(run)
