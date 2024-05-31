import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

# Initialise Atlas Connection String and Password
atlas_connection_string = os.getenv("ATLAS_CONNECTION_STRING")
atlas_cluster_password = os.getenv("ATLAS_CLUSTER_PASSWORD")
database_name = os.getenv("ATLAS_DATABASE_NAME")
collection_name = os.getenv("ATLAS_COLLECTION_NAME")

updated_connection_string = atlas_connection_string.replace(
    "<password>", atlas_cluster_password
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
        command = f"mongoimport {updated_connection_string}{database_name} --collection {collection_name} {folder_path}\\{file} --jsonArray"

        # Execute the command for Windows
        try:
            result = subprocess.run(
                ["cmd", "/c", command], shell=True, capture_output=True, text=True
            )
            print("Command executed successfully for: {}".format(file))
        except subprocess.CalledProcessError as e:
            print("Error occurred while executing the command.")
