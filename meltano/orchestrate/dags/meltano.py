# This file is managed by the 'airflow' file bundle and updated automatically when `meltano upgrade` is run.
# To prevent any manual changes from being overwritten, remove the file bundle from `meltano.yml` or disable automatic updates:
#     meltano config --plugin-type=files airflow set update orchestrate/dags/meltano.py false

# If you want to define a custom DAG, create
# a new file under orchestrate/dags/ and Airflow
# will pick it up automatically.

import os
import logging
import subprocess
import json

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import timedelta

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "catchup": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "concurrency": 1,
}

project_root = os.getenv("MELTANO_PROJECT_ROOT", os.getcwd())

# This creates the DAG's by getting the list of schedules from the
result = subprocess.run(
    [".meltano/run/bin", "schedule", "list", "--format=json"],
    cwd=project_root,
    stdout=subprocess.PIPE,
    universal_newlines=True,
    check=True,
)
schedules = json.loads(result.stdout)

for schedule in schedules:
    logging.info(f"Considering schedule '{schedule['name']}': {schedule}")

    if not schedule["cron_interval"]:
        logging.info(
            f"No DAG created for schedule '{schedule['name']}' because its interval is set to `@once`."
        )
        continue

    args = DEFAULT_ARGS.copy()
    if schedule["start_date"]:
        args["start_date"] = schedule["start_date"]

    dag_id = f"meltano_{schedule['name']}"

    # from https://airflow.apache.org/docs/stable/scheduler.html#backfill-and-catchup
    #
    # It is crucial to set `catchup` to False so that Airflow only create a single job
    # at the tail end of date window we want to extract data.
    #
    # Because our extractors do not support date-window extraction, it serves no
    # purpose to enqueue date-chunked jobs for complete extraction window.
    dag = DAG(dag_id, catchup=False, default_args=args, schedule_interval=schedule["interval"])

    elt = BashOperator(
        task_id="extract_load",
        bash_command=f"cd {project_root}; .meltano/run/bin elt {' '.join(schedule['elt_args'])}",
        dag=dag,
        env={
            # inherit the current env
            **os.environ,
            **schedule["env"],
        },
    )

    # register the dag
    globals()[dag_id] = dag

    logging.info(f"DAG created for schedule '{schedule['name']}'")
