from src.agent import main_agent
import pytest
from tests.query_versions import QUERIES


def id_fn(query_entry):
    # Stable ID based on version + query text hash
    return f"v{query_entry['version']}_{hash(query_entry['text'])}"


############ Test to see whatever query does not crash the main agent. #####################
@pytest.mark.parametrize(
    "query",
    [q["text"] for q in QUERIES],  # Pass just the text to the test
    ids=[id_fn(q) for q in QUERIES]  # But use versioned IDs for tracking
)
def test_main_agent_does_not_crash(query):
    try:
        result = main_agent(query)
        assert result is not None
    except Exception as e:
        pytest.fail(f"Agent crashed for '{query}': {e}")
        
        

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