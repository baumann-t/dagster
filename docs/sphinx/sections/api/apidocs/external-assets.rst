External Assets (Experimental)
==============================

Instance API
------------

External asset events can be recorded using :py:func:`DagsterInstance.report_runless_asset_event` on :py:class:`DagsterInstance`.

**Example:** reporting an asset materialization

.. code-block:: python

    from dagster import DagsterInstance, AssetMaterialization, AssetKey

    instance = DagsterInstance.get()
    instance.report_runless_asset_event(AssetMaterialization(AssetKey("example_asset")))

**Example:** reporting an asset check evaluation

.. code-block:: python

    from dagster import DagsterInstance, AssetCheckEvaluation, AssetCheckKey

    instance = DagsterInstance.get()
    instance.report_runless_asset_event(
      AssetCheckEvaluation(
        asset_key=AssetKey("example_asset"),
        check_name="example_check",
        passed=True
      )
    )

----

REST API
--------

The ``dagster-webserver`` makes available endpoints for reporting asset events.

/report_asset_materialization/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A ``POST`` request made to this endpoint with the required information will result in an `AssetMaterialization` event being recorded.

Parameters can be passed in multiple ways and will be considered in the following order:

1. URL (``asset_key`` only)
2. JSON body (`Content-Type: application/json` header)
3. Query parameter

Refer to the following table for the list of parameters and how each one can be passed to the API.

Returns JSON:
* empty object with status 200 on success
* `{error: ...}` with status 400 on invalid input

**Params**

.. list-table::
   :widths: 15 15 70
   :header-rows: 1

   * - **Name**
     - **Required/Optional**
     - **Description**
   * - asset_key
     - Required
     - **May be passed as URL path components, JSON, or a query parameter**:
       * **URL**: The asset key can be specified as path components after `/report_asset_materialization/`, where each `/` delimits parts of a multipart :py:class:`AssetKey`.

       * **JSON body**: Value is passed to the :py:class:`AssetKey` constructor.

       * **Query parameter**: Accepts string or JSON encoded array for multipart keys.
   * - metadata
     - Optional
     - **May be passed as JSON or a query parameter**:
       * **JSON body**: Value is passed to the :py:class:`AssetMaterialization` constructor.

       * **Query parameter**: Accepts JSON encoded object.
   * - data_version
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to :py:class:`AssetMaterialization` via `tags`.
   * - description
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to the :py:class:`AssetMaterialization` constructor.
   * - partition
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to the :py:class:`AssetMaterialization` constructor.

**Example:** Report an asset materialization against locally running webserver.

.. code-block:: bash

    curl -X POST localhost:3000/report_asset_materialization/example_asset

**Example:** Report an asset materialization against Dagster+ with a JSON body via cURL. Required authentication done via `Dagster-Cloud-Api-Token` header.

.. code-block:: bash

    curl --request POST \
        --url https://example-org.dagster.cloud/example-deployment/report_asset_materialization/ \
        --header 'Content-Type: application/json' \
        --header 'Dagster-Cloud-Api-Token: example-token' \
        --data '{
            "asset_key": "example_asset",
            "metadata": {
                "rows": 10
            },
        }'


**Example:** Report an asset materialization against an open source deployment (hosted at `DAGSTER_WEBSERVER_HOST`) in Python using `requests`.

.. code-block:: python

    import requests

    url = f"{DAGSTER_WEBSERVER_HOST}/report_asset_materialization/example_asset"
    response = requests.request("POST", url)
    response.raise_for_status()

**Example:** Report an asset materialization against Dagster+ in Python using `requests`. Required authentication done via `Dagster-Cloud-Api-Token` header.

.. code-block:: python

    import requests

    url = "https://example-org.dagster.cloud/example-deployment/report_asset_materialization/"

    payload = {
        "asset_key": "example_asset",
        "metadata": {"rows": 10},
    }
    headers = {
        "Content-Type": "application/json",
        "Dagster-Cloud-Api-Token": "example-token"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()

/report_asset_check/
^^^^^^^^^^^^^^^^^^^^

A ``POST`` request made to this endpoint with the required information will result in an `AssetCheckEvaluation` event being recorded.

Parameters can be passed in multiple ways and will be considered in the following order:

1. URL (``asset_key`` only)
2. JSON body (`Content-Type: application/json` header)
3. Query parameter

Refer to the following table for the list of parameters and how each one can be passed to the API.

Returns JSON:
* empty object with status 200 on success
* `{error: ...}` with status 400 on invalid input

**Params**

.. list-table::
   :widths: 15 15 70
   :header-rows: 1

   * - **Name**
     - **Required/Optional**
     - **Description**
   * - asset_key
     - Required
     - **May be passed as URL path components, JSON, or a query parameter**:
       * **URL**: The asset key can be specified as path components after `/report_asset_check/`, where each `/` delimits parts of a multipart :py:class:`AssetKey`.

       * **JSON body**: Value is passed to the :py:class:`AssetKey` constructor.

       * **Query parameter**: Accepts string or JSON encoded array for multipart keys.
   * - passed
     - Required
     - **May be passed as JSON or a query parameter**:
       * **JSON body**: Value is passed to the :py:class:`AssetCheckEvaluation` constructor.

       * **Query parameter**: Accepts JSON encoded boolean 'true' or 'false'.

   * - metadata
     - Optional
     - **May be passed as JSON or a query parameter**:
       * **JSON body**: Value is passed to the :py:class:`AssetCheckEvaluation` constructor.

       * **Query parameter**: Accepts JSON encoded object.
   * - severity
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to the :py:class:`AssetCheckSeverity` constructor.

**Example:** report an successful asset check against locally running webserver

.. code-block:: bash

    curl -X POST "localhost:3000/report_asset_check/example_asset?check_name=example_check&passed=true"

**Example:** report a failed asset check against Dagster+ with JSON body via cURL (required authentication done via `Dagster-Cloud-Api-Token` header).

.. code-block:: bash

    curl --request POST \
        --url https://example-org.dagster.cloud/example-deployment/report_asset_check/ \
        --header 'Content-Type: application/json' \
        --header 'Dagster-Cloud-Api-Token: example-token' \
        --data '{
            "asset_key": "example_asset",
            "check_name": "example_check",
            "passed": false,
            "metadata": {
                "null_rows": 3
            },
        }'


/report_asset_observation/
^^^^^^^^^^^^^^^^^^^^^^^^^^

A ``POST`` request made to this endpoint with the required information will result in an `AssetObservation` event being recorded.

Parameters can be passed in multiple ways and will be considered in the following order:

1. URL (``asset_key`` only)
2. JSON body (`Content-Type: application/json` header)
3. Query parameter

Refer to the following table for the list of parameters and how each one can be passed to the API.

Returns JSON:
* empty object with status 200 on success
* `{error: ...}` with status 400 on invalid input

**Params**

.. list-table::
   :widths: 15 15 70
   :header-rows: 1

   * - **Name**
     - **Required/Optional**
     - **Description**
   * - asset_key
     - Required
     - **May be passed as URL path components, JSON, or a query parameter**:
       * **URL**: The asset key can be specified as path components after `/report_asset_observation/`, where each `/` delimits parts of a multipart :py:class:`AssetKey`.

       * **JSON body**: Value is passed to the :py:class:`AssetKey` constructor.

       * **Query parameter**: Accepts string or JSON encoded array for multipart keys.
   * - metadata
     - Optional
     - **May be passed as JSON or a query parameter**:
       * **JSON body**: Value is passed to the :py:class:`AssetObservation` constructor.

       * **Query parameter**: Accepts JSON encoded object.
   * - data_version
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to :py:class:`AssetObservation` via `tags`.
   * - description
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to the :py:class:`AssetObservation` constructor.
   * - partition
     - Optional
     - **May be passed in JSON body or as query parameter.** Value is passed to the :py:class:`AssetObservation` constructor.



**Example:** report an asset observation with data version against locally running webserver

.. code-block:: bash

    curl -X POST "localhost:3000/report_asset_observation/example_asset?data_version=example_data_version"

**Example:** report an asset observation against Dagster+ with json body via curl (required authentication done via `Dagster-Cloud-Api-Token` header).

.. code-block:: bash

    curl --request POST \
        --url https://example-org.dagster.cloud/example-deployment/report_asset_observation/ \
        --header 'Content-Type: application/json' \
        --header 'Dagster-Cloud-Api-Token: example-token' \
        --data '{
            "asset_key": "example_asset",
            "metadata": {
                "rows": 10
            },
            "data_version": "example_data_version",
        }'
