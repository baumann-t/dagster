from dagster import AssetKey, SourceAsset, asset

my_source_asset = SourceAsset(
    key=AssetKey("my_source_asset"), io_manager_key="s3_io_manager"
)


@asset
def my_derived_asset(my_source_asset):
    return my_source_asset + [4]
