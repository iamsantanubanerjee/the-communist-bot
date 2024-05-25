import json
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extraction(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:

    # Initialize an empty dictionary to store the key-value pairs for JSON
    pages_dict = {}

    directory_path = 'extracted-data'
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()  # Extracting pagewise Data

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len, is_separator_regex=False)

    for i, document in enumerate(pages):
        split_result = text_splitter.split_text(
            document.page_content)  # Chunking pagewise data
        pages_dict["{}".format(document.metadata['page'] + 1)] = split_result

    # Convert the dictionary to a JSON string
    json_output = json.dumps(pages_dict, indent=4)

    # Define the directory and file path where the JSON data will be stored
    json_file_path = os.path.join(directory_path, file_name + '.json')

    # Create the directory if it does not exist
    os.makedirs(directory_path, exist_ok=True)

    # Write the JSON string to a file
    with open(json_file_path, 'w') as json_file:
        json_file.write(json_output)
