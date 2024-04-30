from typing import Optional

import duckdb
from dagster import (
    AssetExecutionContext,
    AssetKey,
    AutoMaterializePolicy,
    AutoMaterializeRule,
    Definitions,
)
from dagster._core.definitions.auto_materialize_rule_impls import MaterializeOnCronRule
from dagster._core.definitions.materialize import materialize
from dagster_embedded_elt.dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dlt import Pipeline
from dlt.extract.resource import DltResource

from .dlt_test_sources.duckdb_with_transformer import pipeline


def test_example_pipeline_asset_keys(dlt_pipeline: Pipeline) -> None:
    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline)
    def example_pipeline_assets(
        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
    ):
        yield from dlt_pipeline_resource.run(context=context)

    assert {
        AssetKey("dlt_pipeline_repos"),
        AssetKey("dlt_pipeline_repo_issues"),
    } == example_pipeline_assets.keys


def test_example_pipeline(dlt_pipeline: Pipeline) -> None:
    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline)
    def example_pipeline_assets(
        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
    ):
        yield from dlt_pipeline_resource.run(context=context)

    res = materialize(
        [example_pipeline_assets],
        resources={"dlt_pipeline_resource": DagsterDltResource()},
    )
    assert res.success

    temporary_duckdb_path = f"{dlt_pipeline.pipeline_name}.duckdb"
    with duckdb.connect(database=temporary_duckdb_path, read_only=True) as conn:
        row = conn.execute("select count(*) from example.repos").fetchone()
        assert row and row[0] == 3

        row = conn.execute("select count(*) from example.repo_issues").fetchone()
        assert row and row[0] == 7


def test_multi_asset_names_do_not_conflict(dlt_pipeline: Pipeline) -> None:
    class CustomDagsterDltTranslator(DagsterDltTranslator):
        def get_asset_key(self, resource: DltResource) -> AssetKey:
            return AssetKey("custom_" + resource.name)

    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline, name="multi_asset_name1")
    def assets1():
        pass

    @dlt_assets(
        dlt_source=pipeline(),
        dlt_pipeline=dlt_pipeline,
        name="multi_asset_name2",
        dlt_dagster_translator=CustomDagsterDltTranslator(),
    )
    def assets2():
        pass

    assert Definitions(assets=[assets1, assets2])


def test_get_materialize_policy(dlt_pipeline: Pipeline):
    class CustomDagsterDltTranslator(DagsterDltTranslator):
        def get_auto_materialize_policy(
            self, resource: DltResource
        ) -> Optional[AutoMaterializePolicy]:
            return AutoMaterializePolicy.eager().with_rules(
                AutoMaterializeRule.materialize_on_cron("0 1 * * *")
            )

    @dlt_assets(
        dlt_source=pipeline(),
        dlt_pipeline=dlt_pipeline,
        dlt_dagster_translator=CustomDagsterDltTranslator(),
    )
    def assets():
        pass

    for item in assets.auto_materialize_policies_by_key.values():
        assert any(
            isinstance(rule, MaterializeOnCronRule) and rule.cron_schedule == "0 1 * * *"
            for rule in item.rules
        )


def test_example_pipeline_has_required_metadata_keys(dlt_pipeline: Pipeline):
    required_metadata_keys = {
        "destination_type",
        "destination_name",
        "dataset_name",
        "first_run",
        "started_at",
        "finished_at",
        "jobs",
    }

    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline)
    def example_pipeline_assets(
        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
    ):
        for asset in dlt_pipeline_resource.run(context=context):
            assert asset.metadata
            assert all(key in asset.metadata.keys() for key in required_metadata_keys)
            yield asset

    res = materialize(
        [example_pipeline_assets],
        resources={"dlt_pipeline_resource": DagsterDltResource()},
    )
    assert res.success


def test_example_pipeline_subselection(dlt_pipeline: Pipeline) -> None:
    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline)
    def example_pipeline_assets(
        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
    ):
        yield from dlt_pipeline_resource.run(context=context)

    res = materialize(
        [example_pipeline_assets],
        resources={"dlt_pipeline_resource": DagsterDltResource()},
        selection=[AssetKey(["dlt_pipeline_repo_issues"])],
    )
    assert res.success

    asset_materializations = res.get_asset_materialization_events()
    assert len(asset_materializations) == 1

    found_asset_keys = [
        mat.event_specific_data.materialization.asset_key  # pyright: ignore
        for mat in asset_materializations
    ]
    assert found_asset_keys == [AssetKey(["dlt_pipeline_repo_issues"])]


def test_subset_pipeline_using_with_resources(dlt_pipeline: Pipeline) -> None:
    @dlt_assets(dlt_source=pipeline().with_resources("repos"), dlt_pipeline=dlt_pipeline)
    def example_pipeline_assets(
        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
    ):
        yield from dlt_pipeline_resource.run(context=context)

    assert len(example_pipeline_assets.keys) == 1
    assert example_pipeline_assets.keys == {AssetKey("dlt_pipeline_repos")}

    res = materialize(
        [example_pipeline_assets],
        resources={"dlt_pipeline_resource": DagsterDltResource()},
    )
    assert res.success

    temporary_duckdb_path = f"{dlt_pipeline.pipeline_name}.duckdb"
    with duckdb.connect(database=temporary_duckdb_path, read_only=True) as conn:
        row = conn.execute("select count(*) from example.repos").fetchone()
        assert row and row[0] == 3
