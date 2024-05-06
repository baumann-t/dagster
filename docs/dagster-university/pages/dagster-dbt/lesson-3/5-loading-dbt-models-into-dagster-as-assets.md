---
title: 'Lesson 3: Loading dbt models into Dagster as assets'
module: 'dagster_dbt'
lesson: '3'
---

# Loading dbt models into Dagster as assets

Now is the moment that we’ve been building up to since the beginning of this module. Let’s see your dbt models in a Dagster asset graph!

---

## Turning dbt models into assets with  @dbt_assets

The star of the show here is the `@dbt_assets` decorator. This is a specialized asset decorator that wraps around a dbt project to tell Dagster what dbt models exist. In the body of the `@dbt_assets` definition, you write exactly how you want Dagster to run your dbt models.

Many Dagster projects may only need one `@dbt_assets`-decorated function that manages the entire dbt project. However, you may need to create multiple definitions for various reasons, such as:

- You have multiple dbt projects
- You want to exclude certain dbt models
- You want to only execute `dbt run` and not `dbt build` on specific models
- You want to customize what happens after certain models finish, such as sending a notification
- You need to configure some sets of models differently

We’ll only create one `@dbt_assets` definition for now, but in a later lesson, we’ll encounter a use case for needing another `@dbt_assets` definition.

---

## Loading the models as assets

1. Create a new file in the `assets` directory called `dbt.py`.

2. Add the following imports to the top of the file:

   ```python
   from dagster import AssetExecutionContext
   from dagster_dbt import dbt_assets, DbtCliResource

   import os

   from .constants import DBT_DIRECTORY
   ```

3. The `@dbt_assets` decorator requires a path to the project’s manifest file, which is within our `DBT_DIRECTORY`. Use that constant to create a path to the `manifest.json` by copying and pasting the code below:

   ```python
   dbt_manifest_path = os.path.join(DBT_DIRECTORY, "target", "manifest.json")
   ```

   Similar to how we used `joinpath` earlier to point to the dbt project’s directory, we’re using it once again to reference `target/manifest.json` more precisely.

4. Now, use the `@dbt_assets` decorator to create a new asset function and provide it with a reference to the manifest:

   ```python
   @dbt_assets(
       manifest=dbt_manifest_path,
   )
   def dbt_analytics(context: AssetExecutionContext, dbt: DbtCliResource):
   ```

5. Finally, add the following to the body of `dbt_analytics` function:

   ```python
   yield from dbt.cli(["run"], context=context).stream()
   ```

   Notice we provided two arguments here. The first argument is the `context`, which indicates which dbt models to run and any related configurations. The second refers to the dbt resource you’ll be using to run dbt.

   Let’s review what’s happening in this line in a bit more detail:

   - We use the `dbt` argument (which is a `DbtCliResource`) to execute a dbt command through its `.cli` method.
   - The `.stream()` method fetches the events and results of this dbt execution.
     - This is one of multiple ways to get the Dagster events, such as what models materialized or tests passed. We recommend starting with this and exploring other methods in the future as your use cases grow (such as fetching the run artifacts after a run). In this case, the above line will execute `dbt run`.
   - The results of the `stream` are a Python generator of what Dagster events happened. We used [`yield from`](https://pythonalgos.com/generator-functions-yield-and-yield-from-in-python/) (not just `yield`!) to have Dagster track asset materializations.

At this point, `dbt.py` should look like this:

```python
from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets, DbtCliResource

from .constants import DBT_DIRECTORY


dbt_manifest_path = DBT_DIRECTORY.joinpath("target", "manifest.json")


@dbt_assets(
    manifest=dbt_manifest_path,
)
def dbt_analytics(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["run"], context=context).stream()
```
