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
                "commit": "~32b78daf6d19cd72f25ffa0796d7647ba31d59082291f87784059d22d845998d",
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
                "commit": "~32b78daf6d19cd72f25ffa0796d7647ba31d59082291f87784059d22d845998d",
                "step": "train",
                "image": "docker.io/noorai/dynamic-pipelines-demo:0.1",
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
    "copy_source": "018e3291-fe27-a826-1460-9dcd640d4902",
    "parameters": {},
    "title": "training-pipeline (copy)"
}

run_predict_execution = {
        "project": "018e1923-e286-194d-b5b5-4819a17e6f65",
        "environment": "01764236-1f69-fea3-392a-be679bf067b3",
        "commit": "~e8471dd937427f2bc18625378a36003d4d12bf696518fd7104e26eaa4a0db077",
        "step": "predict-models",
        "image": "docker.io/noorai/dynamic-pipelines-demo:0.1",
        "command": "python predict.py {parameters}",
        "inputs": {
            "dataset": [
                "dataset://harbor_B_test/latest",
                "dataset://harbor_A_test/latest"
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
        "environment_variables": {},
        "upload_store": "015e516a-2a89-ad95-38b9-cae527cde9a8",
        "copy_source": "018e33eb-89cd-be09-ff2d-9aed0f19e093"
}