from src.agent import main_agent
import pytest
from pathlib import Path


def load_queries():
    query_file = Path("tests/ai_chatbot_real_estate_queries.txt")
    queries = query_file.read_text().splitlines()
    return [(q.strip(), f"line_{i+1}") for i, q in enumerate(queries) if q.strip()]

queries = load_queries()

@pytest.mark.parametrize("query,query_id", queries, ids=[qid for _, qid in queries])
def test_main_agent(query, query_id):
    try:
        result = main_agent(query)
        assert result is not None
    except Exception as e:
        pytest.fail(f"Failed: {query}")

# Force testmon to track the queries file
def pytest_sessionstart(session):
    session.config.testmon.addchange("tests/ai_chatbot_real_estate_queries.txt")