import ast
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq

from utilities.retrieval import vector_search

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(model_name="llama3-8b-8192")


# Define your desired data structure.
class ModelOutput(BaseModel):
    response: str = Field(description="the response to the query")
    documentID: list[str] = Field(
        description="documentIDs of relevant contexts used to form response"
    )


def bot_response(
    user_query: str,
) -> tuple[str, list[str], dict]:

    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=ModelOutput)

    # Examples for the prompt
    examples = [
        {
            "question": "Who is the current best F1 Driver?",
            "context": [
                {
                    "documentID": "<Document ID>",
                    "file_path": "<File Path>",
                    "file_name": "<File Name>",
                    "page_number": "<Page Number>",
                }
            ],
            "answer": {
                "response": "The current best F1 driver is Fernando Alonso",
                "documentID": [
                    "d381adfb-d0b6-46ef-8e00-1c44c90ac14b",
                    "d381adfb-d0b6-46ef-8e00-1c44c90ac39b",
                ],
            },
        },
        {
            "question": "Name four F1 Drivers",
            "context": [
                {
                    "documentID": "<Document ID>",
                    "file_path": "<File Path>",
                    "file_name": "<File Name>",
                    "page_number": "<Page Number>",
                }
            ],
            "answer": {
                "response": "Four F1 drivers are:\n Max Verstappen\n Fernando Alonso\n Lewis Hamilton\n Charles Leclerc",
                "documentID": [
                    "d381thfb-d0b6-46ef-8e00-1c44c90ac14b",
                    "d381adfb-d0b6-47sf-8e00-1c44c90ac39b",
                ],
            },
        },
        {
            "question": "Who is the founder of Ferrari?",
            "context": [
                {
                    "documentID": "<Document ID>",
                    "file_path": "<File Path>",
                    "file_name": "<File Name>",
                    "page_number": "<Page Number>",
                }
            ],
            "answer": {
                "response": "I do not know the answer to your question",
                "documentID": [],
            },
        },
    ]

    # Instructions to the bot
    bot_instructions = """1. If the answer is not in the relevant context, respond with "I do not know the answer to your question."
                          2. Use words and terminology directly from the context without creating synonyms.
                          3. Construct grammatically correct sentences using context information.
                          4. Provide the documentID of the context where you found the answer.
                          5. If the answer is found in multiple contexts, list those documentIDs in an array like [] and return the final output.
                          6. Give the final output in JSON format with two keys: 'response' and 'documentID'. Do not deviate from this format.
                          7. If the response is "I do not know the answer to your question," keep the documentID key empty.
                          8. Include bullet points when required with answers.
                          9. Do not include 'documentID' under the "response" key in the final JSON.
                          10. Do not include any information after 'documentID' has been mentioned in the response.
                          11. Do not include any information about 'documentID' under the 'response' key.
                          12. Analyze the contents of the relevant contexts carefully and form your answer based on that. Do not include information not present in the relevant context.
                          13. Stop forming the answer after 'documentID' has been mentioned.
                          14. Do not explain the documentIDs you have included or excluded.
                          15. Provide as detailed of a response as possible.
                          16. Maintain a proper JSON format as provided in the examples
    """

    # This is a prompt template used to format each individual example.
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}\n{context}"),
            ("ai", "{answer}"),
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    final_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're an expert AI assistant specializing in advanced question answering.\
            Generate answers STRICTLY following the below instructions: \n{bot_instructions}\
            The answer format should STRICTLY follow {format_instructions}\
            Do not add extra information outside of the format",
            ),
            few_shot_prompt,
            ("human", "{question}\n{context}"),
        ]
    )

    relevant_context = vector_search(user_query=user_query)
    # print(relevant_context)

    chain = final_prompt | model

    llm_output = chain.invoke(
        {
            "question": user_query,
            "context": relevant_context,
            "bot_instructions": bot_instructions,
            "format_instructions": parser.get_format_instructions(),
        }
    )

    try:
        # print(llm_output.content)

        # Convert the dictionary string to an actual dictionary
        data_dict = ast.literal_eval(llm_output.content)
        print(data_dict)

        # Extract 'response' and 'documentID'
        response = data_dict["response"]
        # print(response)
        documentID = data_dict["documentID"]
        # print(documentID)
    except Exception as e:
        print("oops")

    return response, documentID, relevant_context


def process_bot_response(
    response: str, documentID: list[str], relevant_context: dict
) -> str:
    processed_output = response
    fileNamepageNumber = []
    processed_fileNamepageNumber = ''
    # print(documentID)
    for i in documentID:
        # print(i)
        for j in range(len(relevant_context)):
            # print(len(relevant_context))
            if i == relevant_context[j].get("documentID"):
                page_number = relevant_context[j].get("page_number")
                file_name = relevant_context[j].get("file_name")
                # Check if filename already exists in list
                found = False
                for item in fileNamepageNumber:
                    # Check if page number already exists for this filename
                    if page_number not in item["pageno"]:
                        item["pageno"].append(page_number)
                    found = True
                    break
                if not found:
                    fileNamepageNumber.append(
                        {"filename": file_name, "pageno": [page_number]}
                    )
    
    for file in fileNamepageNumber:
        filename = file['filename']
        page_numbers = ', '.join(file['pageno'])
        processed_fileNamepageNumber += f"{filename}: {page_numbers}\n"

    processed_output = processed_output + '\n\n' + processed_fileNamepageNumber
    print(processed_output)

    return processed_output
