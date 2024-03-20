import requests
import time
import copy
import os
import valohai

from utils.api_jsons import create_pipeline

# Retrieve Valohai API token from environment variable
auth_token = os.environ.get("VALOHAI_API_TOKEN")
HEADERS = {'Authorization': 'Token %s' % auth_token}


def create_big_pipeline(harbors, epochs_values):
    dynamic_pipeline_json = copy.deepcopy(create_pipeline)
    dynamic_pipeline_json["nodes"] = []  # Reset nodes to start fresh for this dynamic creation
    dynamic_pipeline_json["edges"] = []  # Reset edges
    dynamic_pipeline_json["title"] = "single-training-pipeline"

    train_nodes = []
    node_count = 0
    for epochs in epochs_values:
        for harbor in harbors:
            preprocess_node_name = f"preprocess{node_count}"
            train_node_name = f"train{node_count}"

            # Clone and update preprocess node from create_pipeline
            preprocess_node = copy.deepcopy(create_pipeline["nodes"][0])
            preprocess_node["name"] = preprocess_node_name
            preprocess_node["template"]["parameters"]["dataset_name"] = harbor

            # Clone and update train node from create_pipeline
            train_node = copy.deepcopy(create_pipeline["nodes"][1])
            train_node["name"] = train_node_name
            train_node["template"]["parameters"]["dataset_name"] = harbor
            train_node["template"]["parameters"]["epochs"] = epochs

            # Add updated nodes to dynamic_pipeline_json
            dynamic_pipeline_json["nodes"].append(preprocess_node)
            dynamic_pipeline_json["nodes"].append(train_node)

            # Create and add edge between preprocess and train nodes
            dynamic_pipeline_json["edges"].append({
                "source_node": preprocess_node_name,
                "source_key": "run_training_for",
                "source_type": "metadata",
                "target_node": train_node_name,
                "target_type": "parameter",
                "target_key": "dataset_name"
            })
            train_nodes.append(train_node_name)
            node_count += 1

    # Create predicting node
    dynamic_pipeline_json["nodes"].append({
        "name": "predict",
        "type": "execution",
        "template": {
            "environment": dynamic_pipeline_json["nodes"][0]["template"]["environment"],
            "commit": "main",
            "step": "predict-models",
            "image": "valohai/dynamic-pipelines-demo:0.1",
            "command": "python ./predict.py",
            "inputs": {
                "dataset": [
                    "dataset://harbor_B_test/latest",
                    "dataset://harbor_A_test/latest"
                ],
                "models": []
            },
            "parameters": {
                "exec_ids": [],
                "harbours": harbors
            },
        },
        "on_error": "stop-all"
    })

    # Connect each train node to the predict node
    for train_node_name in train_nodes:
        dynamic_pipeline_json["edges"].append({
            "source_node": train_node_name,
            "source_key": "*",
            "source_type": "output",
            "target_node": "predict",
            "target_type": "input",
            "target_key": "models"

        })
    print('The JSON of an API request')
    print(dynamic_pipeline_json)
    print()
    resp = requests.post(
        url="https://app.valohai.com/api/v0/pipelines/",
        headers=HEADERS,
        json=dynamic_pipeline_json,
    )
    if resp.status_code == 201:
        print(f"Single big pipeline created successfully.")
        return resp.json()["id"]
    else:
        print('Error occurred: ', resp.status_code)
        print(resp.text)
        return None


if __name__ == "__main__":
    harbors = valohai.parameters('harbours').value
    harbors = ''.join(harbors).split(',')

    epochs_values = valohai.parameters('epochs').value
    epochs_values = ''.join(epochs_values).split(',')

    print('Parameters: ')
    print('harbors: ', harbors)
    print('epochs: ', epochs_values)

    pipeline_ids = create_big_pipeline(harbors, epochs_values)



