from src.agent import main_agent
import pytest

############ Test to see whatever query does not crash the main agent. #####################

test_queries = [
    "Just checking if this runs",
    "Show average price in Dubai Marina",
    "What is the weather in Paris?",
    "Trigger unknown action somehow",
    "List properties under 1 million AED",
    "Show distribution of property prices in Dubai",
    "What is the average rent in Abu Dhabi?",
]

@pytest.mark.parametrize("query", test_queries)
def test_main_agent_does_not_crash(query):
    "Test to see whatever query does not crash the main agent."
    try:
        result = main_agent(query)
        assert result is not None
    except Exception as e:
        pytest.fail(f"main_agent crashed for query '{query}' with error: {e}")

##### Test to see if the main agent returns the expected output type for various queries.######

test_agent_output_type = [
    {"query": "What is the weather in Paris?", "expected_type": "output"},
    {"query": "Show average price in Dubai Marina", "expected_type": "data"},
    {"query": "Show distribution of prices in UAE", "expected_type": "hello"},
]

@pytest.mark.parametrize("case", test_agent_output_type)
def test_main_agent_dynamic(case):
    "Test to see if the main agent returns the expected output type for various queries."
    result = main_agent(case["query"])
    if case["expected_type"]:
        assert result["type"] == case["expected_type"]

        

