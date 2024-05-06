---
title: 'Lesson 4: Speeding up the development cycle'
module: 'dagster_dbt'
lesson: '4'
---

# Speeding up the development cycle

By now, you’ve had to run `dbt parse` and reload your code location quite frequently, which doesn’t feel like the cleanest developer experience.

Before we move on, we’ll reduce the number of steps in the feedback loop. We'll automate the `dbt parse` command by taking advantage of the `DbtCliResource` that we wrote earlier.

---

## Automating running dbt parse in development

The first detail is that resources don’t need to be part of an asset to be executed. This means that once a `dbt_resource` is defined, you can use it to execute commands when your code location is being built. Rather than manually running `dbt parse`, let’s use the `dbt_resource` to run the command for us.

In `dbt.py`, import the `dbt_resource` and the `Path` class from the `pathlib` standard library   with:

```python
from pathlib import Path

from ..resources import dbt_resource
```

Afterward, above your `dbt_manifest_path` declaration, add this snippet to run `dbt parse`:

```python
dbt_resource.cli(["--quiet", "parse"], target_path=Path("target")).wait()
```

If you look at the dbt project’s `/target` directory, you’ll see it stores the artifacts. To read from the generated manifest, you can retrieve the path to this folder from the return value of the `.wait()` call.

Let’s define a new `dbt_manifest_path` that will always point to the `manifest.json` that was just created from this programmatic `dbt parse` command:

```python
dbt_manifest_path = (
    dbt_resource.cli(
        ["--quiet", "parse"],
        target_path=Path("target"),
    )
    .wait()
    .target_path.joinpath("manifest.json")
)
```

Reload your code location in the Dagster UI, and you’ll see that everything should still work: the dbt models are still shown as assets and you can manually materialize any of the models. The key difference is that you no longer have to manually run `dbt parse` anymore!

---

## Specifying manifest build behavior in production

This is great, however, it might feel a bit greedy and intensive to be constantly building a new manifest file. This is especially the case in production where a dbt project is stable. Therefore, let’s lock this computation behind an environment variable and defer to a single copy of our manifest in production.

1. In the `.env` file, define an environment variable named `DAGSTER_DBT_PARSE_PROJECT_ON_LOAD` and set it to `1`:

   ```python
   DUCKDB_DATABASE=data/staging/data.duckdb
   DAGSTER_DBT_PARSE_PROJECT_ON_LOAD=1 # New env var defined here
   ```

2. Next, import the `os` module at the top of the `dbt.py` file so the environment variable is accessible:

   ```python
   import os
   ```

3. Finally, let’s check to see if the variable is set:

   - **If it is**, we’ll use our new logic to generate a new manifest file every time the code location is built
   - **If it isn’t**, then we’ll use our old logic of depending on a specific `manifest.json` in the `target` directory.

   Copy and paste the code to finalize the definition of `dbt_manifest_path`:

   ```python
   if os.getenv("DAGSTER_DBT_PARSE_PROJECT_ON_LOAD"):
       dbt_manifest_path = (
           dbt_resource.cli(["--quiet", "parse"]).wait()
           .target_path.joinpath("manifest.json")
       )
   else:
       dbt_manifest_path = os.path.join(DBT_DIRECTORY, "target", "manifest.json")
   ```
