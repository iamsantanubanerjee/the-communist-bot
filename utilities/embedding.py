import os
import json
import uuid

from sentence_transformers import SentenceTransformer


def generate_embeddings(text: str) -> list[float]:
    """Generate embedding for a string using HuggingFace embedding

    Args:
        text (str): The string of which embedding is to be created

    Returns:
        list[float]: The embedded vector
    """
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(text)

    return embeddings.tolist()


def transform_data(input_folder_path: str, output_folder_path) -> None:
    """Consolidates pagewise metadata and embedding for each chunk into JSON file and stores them under corresponding folders named after individual files.

    Args:
        input_folder_path (str): Path of extracted folder containing JSON files for each document
        output_folder_path (str): Path where JSON files containing metadata and embeddings are to be stored
    """
    json_file_paths = []
    for root, directories, files in os.walk(input_folder_path):
        for file in files:
            # Construct the full file path and add it to the list
            full_path = os.path.join(root, file)
            json_file_paths.append(full_path)

    print(len(json_file_paths))

    for json_file in json_file_paths:

        output_folder_path = (
            output_folder_path + "/" + os.path.basename(json_file).split(".json")[0]
        )

        # Create output folder if not exist
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        file_name = f"{os.path.basename(json_file).split('.json')[0]}.pdf"
        file_path = os.path.join("manifesto", file_name)

        try:
            with open(json_file, "r") as file:
                loaded_dict = json.load(file)

            for page_number, page_content in loaded_dict.items():
                # List to store document metadata
                doc_metadata = []

                for chunk in page_content:
                    temp = {
                        "documentID": str(uuid.uuid4()),
                        "file_path": file_path,
                        "file_name": file_name,
                        "page_number": page_number,
                        "content": chunk,
                        "embedding": generate_embeddings(chunk),
                    }

                    doc_metadata.append(temp)

                json_data = json.dumps(doc_metadata)

                output_file_path = os.path.join(
                    output_folder_path, f"{page_number}.json"
                )
                with open(output_file_path, "w") as f:
                    f.write(json_data)

        except Exception as e:
            print(e)
