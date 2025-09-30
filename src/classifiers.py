import openai
from prompts.classifiers import spam_prompt, task_prompt
from openai.types.chat import ChatCompletionUserMessageParam
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the OpenAI client using the API key from environment variables
official_ai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_uae_real_estate_query(query: str) -> bool:
    """
    Determines if a given query is related to London real estate.

    Args:
        query (str): The user query to classify.

    Returns:
        bool: True if the query is classified as related to London real estate, False otherwise.
    """
    # Generate a prompt for the query using the spam_prompt function
    prompt = spam_prompt(query)

    # Send the prompt to the OpenAI API and get the response
    response = official_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[ChatCompletionUserMessageParam(role="user", content=prompt)],
        temperature=0,
        max_tokens=3,
    )

    # Extract and normalize the decision from the API response
    decision = response.choices[0].message.content.strip().lower()

    # Return True if the decision is "yes", otherwise False
    return decision == "yes"


def llm_classifier(query: str) -> str:
    """
    Classifies a given query using a large language model (LLM).

    Args:
        query (str): The user query to classify.

    Returns:
        str: The classification result as a string.
    """
    # Generate a prompt for the query using the task_prompt function
    prompt = task_prompt(query)

    # Send the prompt to the OpenAI API and get the response
    response = official_ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[ChatCompletionUserMessageParam(role="user", content=prompt)],
        temperature=0,
        max_tokens=10,
    )

    # Extract, clean, and normalize the decision from the API response
    decision = response.choices[0].message.content.strip().strip('"').lower()

    # Print the decision for debugging purposes
    print(decision)

    # Return the classification result
    return decision
