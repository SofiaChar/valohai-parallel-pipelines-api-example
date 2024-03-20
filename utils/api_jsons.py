create_pipeline = {
    "edges": [
        {
            "source_node": "preprocess",
            "source_key": "run_training_for",
            "source_type": "metadata",
            "target_node": "train",
            "target_type": "parameter",
            "target_key": "dataset_name"
        }
    ],
    "nodes": [
        {
            "name": "preprocess",
            "type": "execution",
            "template": {
                "environment": "01764236-1f69-fea3-392a-be679bf067b3",
                "commit": "main",
                "step": "preprocess-dataset",
                "image": "valohai/dynamic-pipelines-demo:0.1",
                "command": "python ./preprocess.py",
                "inputs": {
                    "dataset": [
                        "s3://valohai-demo-library-data/dynamic-pipelines/train/images.zip"
                    ],
                    "labels": [
                        'https://valohai-demo-library-data.s3.eu-west-1.amazonaws.com/dynamic-pipelines/train/train_harbor_A.csv',
                        'https://valohai-demo-library-data.s3.eu-west-1.amazonaws.com/dynamic-pipelines/train/train_harbor_B.csv'
                    ]
                },
                "parameters": {
                    "dataset_name": "harbor_A",
                    "validation_split": 0.3
                },
                "runtime_config": {},
                "inherit_environment_variables": True,
                "environment_variable_groups": [],
                "tags": [],
                "time_limit": 0,
                "environment_variables": {}
            },
            "on_error": "stop-all"
        },
        {
            "name": "train",
            "type": "execution",
            "template": {
                "environment": "01764236-1f69-fea3-392a-be679bf067b3",
                "commit": "main",
                "step": "train",
                "image": "valohai/dynamic-pipelines-demo:0.1",
                "command": "python ./train_model.py {parameters}",
                "inputs": {
                    "dataset": [
                        "dataset://{parameter:dataset_name}_train/latest"
                    ]
                },
                "parameters": {
                    "epochs": 25,
                    "learning_rate": 0.001,
                    "batch_size": 64,
                    "dataset_name": "harbor_A"
                },
                "runtime_config": {},
                "inherit_environment_variables": True,
                "environment_variable_groups": [],
                "tags": [],
                "time_limit": 0,
                "environment_variables": {}
            },
            "on_error": "stop-all"
        }
    ],
    "project": "018e1923-e286-194d-b5b5-4819a17e6f65",
    "tags": [],
    "parameters": {},
    "title": "training-pipeline"
}

run_predict_execution = {
    "project": "018e1923-e286-194d-b5b5-4819a17e6f65",
    "environment": "01764236-1f69-fea3-392a-be679bf067b3",
    "commit": "main",
    "step": "predict-models",
    "image": "docker.io/noorai/dynamic-pipelines-demo:0.1",
    "command": "python predict.py {parameters}",
    "inputs": {
        "dataset": [
            "dataset://harbor_A_test/latest",
            "dataset://harbor_B_test/latest"
        ]
    },
    "parameters": {
        "exec_ids": [],
        "harbours": []
    },
    "runtime_config": {},
    "inherit_environment_variables": True,
    "environment_variable_groups": [],
    "tags": [],
    "time_limit": 0,
    "environment_variables": {}
}
