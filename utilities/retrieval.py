import os

from pymongo import MongoClient

from utilities.embedding import generate_embeddings

ATLAS_CONNECTION_STRING = os.getenv("ATLAS_CONNECTION_STRING")
ATLAS_CLUSTER_PASSWORD = os.getenv("ATLAS_CLUSTER_PASSWORD")
ATLAS_DATABASE_NAME = os.getenv("ATLAS_DATABASE_NAME")
ATLAS_COLLECTION_NAME = os.getenv("ATLAS_COLLECTION_NAME")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")

MONGODB_ATLAS_CLUSTER_URI = ATLAS_CONNECTION_STRING.replace(
    "<password>", ATLAS_CLUSTER_PASSWORD
)

# initialize MongoDB python client
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

MONGODB_COLLECTION = client[ATLAS_DATABASE_NAME][ATLAS_COLLECTION_NAME]


def vector_search(user_query: str) -> list:
    """Perform a vector search in the MongoDB collection based on the user query

    Args:
        user_query (str): The user's query string

    Returns:
        list: A list of matching documents
    """

    # Generate embedding for the user query
    query_embedding = generate_embeddings(user_query)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "communist-manifesto",  # Search index name
                "queryVector": query_embedding,  # Embedding representation of the use query
                "path": "embedding",  # Document field containing the embeddings
                "numCandidates": 150,  # Number of candidate matches to consider (Limits on the number of results to return)
                "limit": 15,  # Return top 2 matches
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "documentID": 1,  # Include the documentID field
                # "file_path": 1,                           # Include the file_path field
                # "file_name": 1,                           # Include the file_name field
                # "page_number": 1,
                "content": 1,
                # "embedding": 1,
                # "score": {"$meta": "vectorSearchScore"},  # Include the search score
            }
        },
    ]

    # Execute the search
    results = MONGODB_COLLECTION.aggregate(pipeline)
    return list(results)
