import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

# Initialise Atlas Connection String and Password
ATLAS_CONNECTION_STRING = os.getenv("ATLAS_CONNECTION_STRING")
ATLAS_CLUSTER_PASSWORD = os.getenv("ATLAS_CLUSTER_PASSWORD")
ATLAS_DATABASE_NAME = os.getenv("ATLAS_DATABASE_NAME")
ATLAS_COLLECTION_NAME = os.getenv("ATLAS_COLLECTION_NAME")

UPDATED_CONNECTION_STRING = ATLAS_CONNECTION_STRING.replace(
    "<password>", ATLAS_CLUSTER_PASSWORD
)


def atlas_ingestion(folder_path: str) -> None:
    """Ingests JSON files inside folder_path to MongoDB Atlas

    Args:
        folder_path (str): Folder where consolidated metadata and embedded JSON files are present
    """
    json_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                json_files.append(relative_path)

    for file in json_files:
        command = f"mongoimport {UPDATED_CONNECTION_STRING}{ATLAS_DATABASE_NAME} --collection {ATLAS_COLLECTION_NAME} {folder_path}\\{file} --jsonArray"

        # Execute the command for Windows
        try:
            result = subprocess.run(
                ["cmd", "/c", command], shell=True, capture_output=True, text=True
            )
            print("Command executed successfully for: {}".format(file))
        except subprocess.CalledProcessError as e:
            print("Error occurred while executing the command.")
