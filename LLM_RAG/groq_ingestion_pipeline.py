import json
from pydantic import BaseModel

# Data model for LLM to generate


class Response(BaseModel):
    label: str
    explanation: str


def get_label(log_message: str, rag, client) -> Response:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are going to act as a Intrusion Detection System, labeling the logs (normal_log or attack) and explaining the attacks.Use less than 50 words for the explanation, the log is between \".\
                    Here you have a RAG with the most similar logs and their labels to help you.{rag}\n"
                # Pass the json schema to the model. Pretty printing improves results.
                f" The JSON object must use the schema: {json.dumps(Response.model_json_schema(), indent=1)}",
            },
            {
                "role": "user",
                "content": f"log message: \"{log_message}\"",
            },
        ],
        model="llama-3.1-8b-instant",
        temperature=0,
        # Streaming is not supported in JSON mode
        stream=False,
        # Enable JSON mode by setting the response format
        response_format={"type": "json_object"},
    )
    return Response.model_validate_json(chat_completion.choices[0].message.content)


def print_response(response: Response):
    print("Label:", response.label)
    print("\nExplanation:", response.explanation)
