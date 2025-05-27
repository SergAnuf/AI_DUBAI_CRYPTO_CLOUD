from src.agent import main_agent
import pytest
from pathlib import Path


def load_queries():
    query_file = Path("tests/queries.txt")
    queries = query_file.read_text().splitlines()
    return [(q, f"line_{i+1}") for i, q in enumerate(queries) if q.strip()]


@pytest.mark.parametrize("query,query_id", load_queries(), ids=lambda x: x[1])
def test_main_agent(query, query_id):
    try:
        result = main_agent(query)
        assert result is not None
    except Exception as e:
        pytest.fail(f"Failed: {query}")

# Force testmon to track the queries file
def pytest_sessionstart(session):
    session.config.testmon.addchange("tests/queries.txt")




##### Test to see if the main agent returns the expected output type for various queries.######

# test_agent_output_type = [
#     {"query": "What is the weather in Paris?", "expected_type": "output"},
#     {"query": "Show average price in Dubai Marina", "expected_type": "data"},
#     {"query": "Show distribution of prices in UAE", "expected_type": "hello"},
# ]

# @pytest.mark.parametrize("case", test_agent_output_type)
# def test_main_agent_dynamic(case):
#     "Test to see if the main agent returns the expected output type for various queries."
#     result = main_agent(case["query"])
#     if case["expected_type"]:
#         assert result["type"] == case["expected_type"]

        

##### Test to see numeric computation correctness [against precomputed dataframe calculations].#####