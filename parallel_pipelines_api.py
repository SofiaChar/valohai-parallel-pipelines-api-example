import time
import requests
import os
import valohai
from utils.api_jsons import create_pipeline, run_predict_execution

# Retrieve Valohai API token from environment variable
auth_token = os.environ.get("VALOHAI_API_TOKEN")
HEADERS = {'Authorization': 'Token %s' % auth_token}


# Creates pipelines for different datasets and epochs.
def create_pipelines(harbors, epochs_values):
    pipeline_ids = []
    for epochs in epochs_values:
        create_pipeline["nodes"][1]["template"]["parameters"]["epochs"] = epochs
        for harbor in harbors:
            create_pipeline["nodes"][0]["template"]["parameters"]["dataset_name"] = harbor
            create_pipeline["nodes"][1]["template"]["parameters"]["dataset_name"] = harbor
            create_pipeline["title"] = f'training-pipeline-{harbor}-epochs-{epochs}'
            resp = requests.post(
                url="https://app.valohai.com/api/v0/pipelines/",
                headers=HEADERS,
                json=create_pipeline,
            )
            if resp.status_code == 201:
                print(f"Pipeline {create_pipeline['title']} created successfully.")
            else:
                print('Error occurred: ', resp.json())
            pipeline_ids.append(resp.json()["id"])
    return pipeline_ids


# Retrieve train execution IDs for all pipelines.
def get_train_exec_ids(pipeline_ids):
    all_pipelines_complete = False
    train_exec_ids = []
    while not all_pipelines_complete:
        all_pipelines_complete = True
        for pip_id in pipeline_ids:
            resp = requests.get(
                url=f'https://app.valohai.com/api/v0/pipelines/{pip_id}/',
                headers=HEADERS,
            )
            data = resp.json()

            current_train_node = data['nodes'][0]['execution']['id']
            if data['status'] != 'complete':
                all_pipelines_complete = False
                print(f"Pipeline {pip_id} is not yet complete.")
            elif current_train_node not in train_exec_ids:
                train_exec_ids.append(current_train_node)
        if not all_pipelines_complete:
            print("Still waiting until all pipelines complete...")
            time.sleep(30)
    return train_exec_ids


# Start the prediction execution.
def execute_predict(train_exec_ids, harbours):
    run_predict_execution["parameters"]["exec_ids"] = train_exec_ids
    run_predict_execution["parameters"]["harbours"] = harbours
    resp = requests.post(
        url='https://app.valohai.com/api/v0/executions/',
        headers=HEADERS,
        json=run_predict_execution,
    )
    if resp.status_code == 201:
        print(f"Execution to predict the models created successfully.")
    else:
        print('Error occurred: ', resp.json())


if __name__ == "__main__":
    harbours = valohai.parameters('harbours').value
    harbours = ''.join(harbours).split(',')

    epochs_values = valohai.parameters('epochs').value
    epochs_values = ''.join(epochs_values).split(',')

    print('Parameters: ')
    print('harbours: ', harbours)
    print('epochs: ', epochs_values)

    pipeline_ids = create_pipelines(harbours, epochs_values)
    train_exec_ids = get_train_exec_ids(pipeline_ids)

    print("\nAll pipelines completed and train ids are retrieved")
    execute_predict(train_exec_ids, harbours)
