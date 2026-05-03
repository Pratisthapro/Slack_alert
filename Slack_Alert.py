import os
import json
import requests
import pandas as pd
from tabulate import tabulate
import snowflake.connector
from json import dumps

class Runner(object):
    @staticmethod
    def runner(file_object):
        # Get DCM credentials
        dcm_host = os.environ.get("INDATA_WORKFLOW_HOST")
        dcm_port = str(os.environ.get("INDATA_WORKFLOW_PORT"))
        datastore_name = "warehouse"

        response = requests.get(
            f"http://{dcm_host}:{dcm_port}/collection/credential?datastore_name={datastore_name}&user_id=dap_user"
        )
        credentials = json.loads(response.content)["data"]
        host = credentials['host']
        user = credentials['username']
        password = credentials['password']

        # Connect to Snowflake
        con = snowflake.connector.connect(
            user=user,
            password=password,
            account='-------------',
            warehouse='-------------',
            database='DAP',
            schema='L1'
        )

        # SQL Query: Always return at least one row
        query = '''select * from l1.Z_Medical_Slack_Alert'''

        # Read query result into DataFrame
        df = pd.read_sql_query(query, con)

        # Prepare Slack message
        alert_text = (
            "------------------------------DAP Notification Alert---------------------\n\n"
            "Alert: Z Medical Data Extraced into S3.\n\n"
        )

        table_text = tabulate([list(row) for row in df.values], headers=list(df.columns), tablefmt="github")

        data = {"text": alert_text + table_text}

        # Slack Webhook URL
        url="https://hooks.slack.com/services/-------------"
        headers = {'Content-Type': 'application/json'}
        requests.post(url, headers=headers, data=dumps(data))

        # Close Snowflake connection
        con.close()

        yield 'abc'
