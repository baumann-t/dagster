from dagster import DagsterRun, Field, StringSource
from dagster._core.events import EngineEventData
from dagster._core.launcher.base import RunLauncher, CheckRunHealthResult, WorkerStatus, LaunchRunContext
from typing import Any, Dict, List, Mapping, Optional, Sequence
from dagster._serdes.config_class import ConfigurableClassData
# from google.cloud import run_v2
# from google.cloud.run_v2 import types
from dagster._serdes import ConfigurableClass
from typing_extensions import Self
from dagster._core.instance import T_DagsterInstance
import uuid
import json
import logging

class CloudRunLauncher(RunLauncher[T_DagsterInstance], ConfigurableClass):
    def __init__(
        self,
        inst_data: Optional[ConfigurableClassData] = None,
        project_id=None,
        region=None,
        service_account=None,
        image_for_run=None,
        client=None
        ):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f"Initializing CloudRunLauncher with: {project_id}, {region}, {service_account}, {image_for_run}")
        self._inst_data = inst_data
        self.project_id = project_id
        self.region = region
        self.service_account = service_account
        # self.client = client or run_v2.ServicesClient()
        self.image_for_run = image_for_run

    @classmethod
    def config_type(cls):
        return {
            'project_id': Field(StringSource, is_required=False, description='Google Cloud project ID.'),
            'region': Field(StringSource, is_required=False, description='Region for Cloud Run services.'),
            'service_account': Field(StringSource, is_required=False, description='Service account email for Cloud Run.'),
            'image_for_run': Field(StringSource, is_required=False, description='Docker image used to launch the Cloud Run task')
        }

    @classmethod
    def from_config_value(
        cls, inst_data: ConfigurableClassData, config_value: Mapping[str, Any]
    ) -> Self:
        return cls(inst_data=inst_data, **config_value)

    @property
    def inst_data(self):
        return self._inst_data

    def launch_run(self, context: LaunchRunContext) -> None:

        print(context)
    #     """Launches a run on Google Cloud Run."""

        # service_name = f"run-{context.dagster_run.run_id}"
        # container_image = self._get_image_for_run(context)
        # self._launch_cloud_run_job(service_name, container_image, context)

    def _launch_cloud_run_job(self, service_name, container_image, context):
        print("here")
    #     # Construct the Cloud Run service object
    #     service = types.Service(
    #         name=service_name,
    #         template=types.RevisionTemplate(
    #             containers=[types.Container(image=container_image)],
    #             service_account=self.service_account
    #         )
    #     )

    #     # Create or update the Cloud Run service
    #     operation = self.client.create_service(
    #         parent=f"projects/{self.project_id}/locations/{self.region}",
    #         service=service
    #     )
    #     operation.result()  # Wait for the operation to complete

    #     self._instance.report_engine_event(
    #         message=f"Launched Cloud Run service: {service_name}",
    #         dagster_run=context.dagster_run,
    #         engine_event_data=EngineEventData(metadata={'service_name': service_name}),
    #         cls=self.__class__,
    #     )

    def terminate(self, run_id: str) -> bool:
        print("here")
    #     """Terminates the specified run on Cloud Run."""
    #     service_name = f"run-{run_id}"
    #     try:
    #         self.client.delete_service(name=service_name)
    #         return True
    #     except Exception as e:
    #         print(f"Failed to terminate Cloud Run service: {e}")
    #         return False

    def check_run_worker_health(self, run: DagsterRun) -> CheckRunHealthResult:
        print("here")
    #     """Checks the health of the run worker."""
    #     service_name = f"run-{run.run_id}"
    #     try:
    #         service = self.client.get_service(name=service_name)
    #         status = service.status.conditions[0].status
    #         if status == 'Ready':
    #             return CheckRunHealthResult(WorkerStatus.RUNNING)
    #         elif status == 'Failed':
    #             return CheckRunHealthResult(WorkerStatus.FAILED, service.status.conditions[0].message)
    #         return CheckRunHealthResult(WorkerStatus.UNKNOWN)
    #     except Exception as e:
    #         return CheckRunHealthResult(WorkerStatus.NOT_FOUND, str(e))
