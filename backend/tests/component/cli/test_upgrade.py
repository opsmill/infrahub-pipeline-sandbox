from dataclasses import dataclass

import pytest

from infrahub.cli.upgrade import _upgrade_execute
from infrahub.core.branch import Branch
from infrahub.core.initialization import get_root_node
from infrahub.core.migrations.shared import GraphMigration, MigrationResult
from infrahub.database import InfrahubDatabase


class Migration001(GraphMigration):
    """Dummy migration whose validation always reports an error."""

    name: str = "001_failing_dummy_migration"
    description: str = "Dummy migration that fails validation."
    minimum_version: int = 0
    queries: list = []

    async def validate_migration(self, db: InfrahubDatabase) -> MigrationResult:
        return MigrationResult(errors=["Unable to connect to the database"])


@dataclass
class FailedUpgradeTestCase:
    name: str
    verbose: bool


class TestUpgradeExecute:
    @pytest.mark.parametrize(
        "test_case",
        [
            FailedUpgradeTestCase(name="default-output", verbose=False),
            FailedUpgradeTestCase(name="verbose", verbose=True),
        ],
        ids=lambda tc: tc.name,
    )
    async def test_upgrade_execute_reports_failed_migration(
        self,
        db: InfrahubDatabase,
        default_branch: Branch,
        monkeypatch: pytest.MonkeyPatch,
        test_case: FailedUpgradeTestCase,
    ) -> None:
        """A failed migration must be reported to the command so it can exit with a nonzero code."""
        monkeypatch.setattr("infrahub.core.migrations.graph.MIGRATIONS", [Migration001])
        root_node = await get_root_node(db=db)
        initial_version = root_node.graph_version

        root_node.graph_version = 0
        await root_node.save(db=db)

        try:
            result = await _upgrade_execute(db=db, root_node_graph_version=0, verbose=test_case.verbose)
            graph_version_after = (await get_root_node(db=db)).graph_version
        finally:
            root_node.graph_version = initial_version
            await root_node.save(db=db)

        assert graph_version_after == 0
        assert result is False
