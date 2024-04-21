from dagster import DagsterRun, Field, StringSource
from dagster._core.events import EngineEventData
from dagster._core.launcher.base import RunLauncher, CheckRunHealthResult, WorkerStatus, LaunchRunContext
from typing import Any, Dict, List, Mapping, Optional, Sequence
from dagster._serdes.config_class import ConfigurableClassData
from google.cloud import run_v2
from collections import namedtuple
from dagster._core.storage.tags import RUN_WORKER_ID_TAG
import dagster._check as check
from dagster._grpc.types import ExecuteRunArgs
from dagster._serdes import ConfigurableClass
from typing_extensions import Self
from dagster._core.instance import T_DagsterInstance
import uuid
import json
from google.api_core.exceptions import GoogleAPIError
from google.api_core.operation import Operation
import logging

Tags = namedtuple('Tags', ['job_name', 'job_uuid'])

class CloudRunJobLauncher(RunLauncher[T_DagsterInstance], ConfigurableClass):
    def __init__(
        self,
        inst_data: Optional[ConfigurableClassData] = None,
        project_id=None,
        region=None,
        service_account=None,
        cloud_run_job_name=None,
        ):

        self._inst_data = inst_data
        self.project_id = project_id
        self.region = region
        self.service_account = service_account
        self.cloud_run = run_v2.JobsClient()
        self.cloud_run_job_name = cloud_run_job_name

    @classmethod
    def config_type(cls):
        return {
            'project_id': Field(StringSource, is_required=False, description='Google Cloud project ID.'),
            'region': Field(StringSource, is_required=False, description='Region for Cloud Run services.'),
            'service_account': Field(StringSource, is_required=False, description='Service account email for Cloud Run.'),
            'cloud_run_job_name': Field(StringSource, is_required=False, description='Docker image used to launch the Cloud Run task'),
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

    #     """Launches a run on Google Cloud Run."""

        job_name = self.cloud_run_job_name
        run = context.dagster_run

        job_code_origin = check.not_none(context.job_code_origin)

        command = ExecuteRunArgs(
            job_origin=job_code_origin,
            run_id=run.run_id,
            instance_ref=self._instance.get_ref(),
        ).get_command_args()

        self._launch_cloud_run_job(job_name, command, run)


    def _launch_cloud_run_job(self, job_name, command, run) -> None:
        # Construct the Cloud Run service object
        try:
            request = run_v2.RunJobRequest(
                name=job_name,
                overrides= {
                    "container_overrides": [{
                        "args": command,
                    }]
                }
            )
            operation = self.cloud_run.run_job(request=request)
            self._set_run_tags(run, operation)
            self.report_launch_events(run, operation)

        except GoogleAPIError as e:
            raise Exception(f"An error occurred: {e}")


    def report_launch_events(self, run: DagsterRun, operation: Operation) -> None:

        metadata = {}
        metadata["Cloud Run operation"] = operation.metadata.name
        metadata["Cloud Run operation uid"] = operation.metadata.uid

        metadata["Run ID"] = run.run_id
        self._instance.report_engine_event(
            message="Launching run in Cloud Run Job",
            dagster_run=run,
            engine_event_data=EngineEventData(metadata),
            cls=self.__class__,
        )

    def _set_run_tags(self, run: DagsterRun, operation: Operation) -> None:
        tags = {
            "cloud_run/job_name": operation.metadata.name,
            "cloud_run/run_uuid": operation.metadata.uid,
            RUN_WORKER_ID_TAG: str(uuid.uuid4().hex)[0:6],
        }
        self._instance.add_run_tags(run.run_id, tags)

    def _get_run_tags(self, run_id: str) -> Tags:
        run = self._instance.get_run_by_id(run_id)
        tags = run.tags if run else {}
        job_name = tags.get("cloud_run/job_name")
        job_uuid = tags.get("cloud_run/run_uuid")

        return Tags(job_name, job_uuid)

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

    @property
    def supports_check_run_worker_health(self) -> bool:
        return True

    def check_run_worker_health(self, run: DagsterRun) -> CheckRunHealthResult:

    #     """Checks the health of the run worker."""
        run_worker_id = run.tags.get(RUN_WORKER_ID_TAG)
        tags = self._get_run_tags(run.run_id)

        if not (tags.job_name and tags.job_uuid):
            return CheckRunHealthResult(WorkerStatus.UNKNOWN, "", run_worker_id=run_worker_id)

        job = self.cloud_run.get_execution(name=tags.job_name)
        print(job)