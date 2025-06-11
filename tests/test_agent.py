from src.agent import main_agent
import pytest
from pathlib import Path


def load_queries():
    """
    Loads queries from a text file and associates each query with a unique ID.

    Returns:
        list of tuple: A list of tuples where each tuple contains:
                       - The query string (str)
                       - A unique identifier for the query (str)
    """
    # Path to the file containing queries
    query_file = Path("tests/ai_chatbot_real_estate_queries.txt")
    # Read the file, split into lines, and create tuples of query and unique ID
    queries = query_file.read_text().splitlines()
    return [(q.strip(), f"line_{i + 1}") for i, q in enumerate(queries) if q.strip()]


# Load the queries and their IDs
queries = load_queries()


@pytest.mark.parametrize("query,query_id", queries, ids=[qid for _, qid in queries])
def test_main_agent(query, query_id):
    """
    Tests the `main_agent` function with various queries.

    Args:
        query (str): The query to be processed by the `main_agent` function.
        query_id (str): The unique identifier for the query.

    Raises:
        pytest.fail: If the `main_agent` function raises an exception or returns None.
    """
    try:
        # Call the main_agent function with the query
        result = main_agent(query)
        # Assert that the result is not None
        assert result is not None
    except Exception as e:
        # Fail the test if an exception occurs
        pytest.fail(f"Failed: {query}")


# Force testmon to track changes in the queries file
def pytest_sessionstart(session):
    """
    Hook function to ensure that testmon tracks changes in the queries file.

    Args:
        session: The pytest session object.
    """
    # Add the queries file to testmon's change tracking
    session.config.testmon.addchange("tests/ai_chatbot_real_estate_queries.txt")
