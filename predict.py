import os
import numpy as np
import random
from PIL import Image
import glob
import requests
import valohai
from utils.model import load_model


# Function to download output files
def download_output_files(exec_ids):
    auth_token = os.environ.get("VALOHAI_API_TOKEN")
    HEADERS = {'Authorization': 'Token %s' % auth_token}

    for exec_id in exec_ids:
        # Get the url to download
        resp = requests.get(
            f'https://app.valohai.com/api/v0/executions/{exec_id}/outputs/?include=download_url',
            headers=HEADERS
        )
        resp.raise_for_status()
        data = resp.json()

        # Download the model by the url
        url = data[0]['download_url']
        file_name = data[0]['name']

        response = requests.get(url)
        response.raise_for_status()

        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"File {file_name} downloaded successfully.")


# Function to run predictions
def run_predictions(dataset_names, model_paths_all, testset_data_paths):
    # Possible ship categories
    category = {"Cargo": 1, "Military": 2, "Carrier": 3, "Cruise": 4, "Tankers": 5}

    for dataset in dataset_names:
        print("Running predictions for dataset:", dataset)
        current_test_data = next((path for path in testset_data_paths if dataset in path), None)

        # Run predictions for all models provided as inputs
        for model_path in model_paths_all:
            if dataset in model_path:
                model = load_model(model_path)
                model_filename = os.path.basename(model_path)
                model_name = os.path.splitext(model_filename)[0]

                with np.load(current_test_data, allow_pickle=True) as f:
                    test_data = f["test_data"]

                predictions = model.predict(test_data)

                # Pick 3 random images from test set to save with the predicted category
                test_img = random.sample(range(len(test_data)), 3)

                # Save images and predictions
                for i in test_img:
                    img = Image.fromarray(test_data[i], "RGB")
                    for key in category:
                        if category[key] == np.argmax(predictions[i]) + 1:
                            print(f"Model: {model_name}, Predicted ship type: {key}")
                            im_path = f"predictions/{model_name}/img{i}_{key}.png"
                            img.save(valohai.outputs().path(im_path))


if __name__ == "__main__":
    models_path = '/valohai/inputs/models'

    # API get exec ids
    harbours = valohai.parameters('harbours').value
    print(harbours)
    harbours = ''.join(harbours).split(',')
    print(harbours)

    # Get exec ids if we are running parallel_pipelines
    exec_ids = valohai.parameters('exec_ids').value
    if exec_ids[0] != '':
        exec_ids = ''.join(exec_ids).split(',')
        print('Executions to get the outputs from:', exec_ids)

        # Download output files
        download_output_files(exec_ids)
        models_path = '*.h5'

    model_paths_all = glob.glob(models_path)

    # Get model paths
    print(model_paths_all)

    # Get testset data paths
    testset_data_paths = glob.glob('/valohai/inputs/dataset/*')

    # Run predictions
    run_predictions(harbours, model_paths_all, testset_data_paths)
