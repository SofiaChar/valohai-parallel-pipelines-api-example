import requests
import time
import os
import valohai

# Retrieve Valohai API token from environment variable
auth_token = os.environ.get("VALOHAI_API_TOKEN")
HEADERS = {'Authorization': 'Token %s' % auth_token}


def create_big_pipeline(harbors, epochs_values):
    create_pipeline = {
        "edges": [],
        "nodes": [],
        "project": "018e1923-e286-194d-b5b5-4819a17e6f65",
        "tags": [],
        "parameters": {},
        "title": "single-training-pipeline"
    }
    train_nodes = []
    node_count = 0
    for epochs in epochs_values:
        for harbor in harbors:
            preprocess_node_name = f"preprocess{node_count}"
            train_node_name = f"train{node_count}"
            # Add preprocess node
            create_pipeline["nodes"].append({
                "name": preprocess_node_name,
                "type": "execution",
                "template": {
                    "environment": "01764236-1f69-fea3-392a-be679bf067b3",
                    "commit": "main",
                    "step": "preprocess-dataset",
                    "image": "docker.io/noorai/dynamic-pipelines-demo:0.1",
                    "command": "python ./preprocess.py",
                    "inputs": {
                        "dataset": [
                            "s3://valohai-demo-library-data/dynamic-pipelines/train/images.zip"
                        ],
                        "labels": [
                            "s3://valohai-demo-library-data/dynamic-pipelines/train/*.csv"
                        ]
                    },
                    "parameters": {
                        "dataset_name": harbor,
                        "validation_split": 0.3
                    },
                }
            })
            # Add train node
            create_pipeline["nodes"].append({
                "name": train_node_name,
                "type": "execution",
                "template": {
                    "environment": "01764236-1f69-fea3-392a-be679bf067b3",
                    "commit": "main",
                    "step": "train",
                    "image": "docker.io/noorai/dynamic-pipelines-demo:0.1",
                    "command": "python ./train_model.py {parameters}",
                    "inputs": {
                        "dataset": [
                            "dataset://{parameter:dataset_name}_train/latest"
                        ]
                    },
                    "parameters": {
                        "epochs": epochs,
                        "dataset_name": harbor,
                        # Add other parameters as needed
                    },
                }
            })
            # Create edges between preprocess and train
            create_pipeline["edges"].append({
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
    create_pipeline["nodes"].append({
        "name": "predict",
        "type": "execution",
        "template": {
            "environment": "01764236-1f69-fea3-392a-be679bf067b3",
            "commit": "~b3926d0f642f5352c362b8a399407c3dc0abe82708ca01a4cd1eddab1c33f804",
            "step": "predict-models",
            "image": "python:3.9",
            "command": "pip install numpy valohai-utils\npython ./predict.py",
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
        create_pipeline["edges"].append({
            "source_node": train_node_name,
            "source_key": "*",
            "source_type": "output",
            "target_node": "predict",
            "target_type": "input",
            "target_key": "models"

        })

    resp = requests.post(
        url="https://app.valohai.com/api/v0/pipelines/",
        headers=HEADERS,
        json=create_pipeline,
    )
    if resp.status_code == 201:
        print(f"Big pipeline created successfully.")
        return resp.json()["id"]
    else:
        print('Error occurred: ', resp.status_code)
        return None


if __name__ == "__main__":
    harbours = valohai.parameters('harbours').value
    harbours = ''.join(harbours).split(',')

    epochs_values = valohai.parameters('epochs').value
    epochs_values = ''.join(epochs_values).split(',')

    print('Parameters: ')
    print('harbours: ', harbours)
    print('epochs: ', epochs_values)

    pipeline_ids = create_big_pipeline(harbours, epochs_values)



