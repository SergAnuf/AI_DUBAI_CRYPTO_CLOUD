from src.agent import main_agent
import pytest



test_agent_output_type = [
    {"query": "What is the weather in Paris?", "expected_type": "output", "expected_substring": "irrelevant"},
    {"query": "Show average price in Dubai Marina", "expected_type": "data", "expected_substring": None},
    {"query": "Trigger unknown action somehow", "expected_type": None, "expected_substring": "Unknown action"},
]


test_agent_top_20_questions = [
    {"query": "What is the weather in Paris?", "expected_type": "output", "expected_substring": "irrelevant"},
    {"query": "Show average price in Dubai Marina", "expected_type": "data", "expected_substring": None},
    {"query": "Trigger unknown action somehow", "expected_type": None, "expected_substring": "Unknown action"},
]



@pytest.mark.parametrize("case", test_agent_output_type)
def test_main_agent_dynamic(case):
    result = main_agent(case["query"])
    print(result)
    if case["expected_type"]:
        assert result["type"] == case["expected_type"]

    if case["expected_substring"]:
        data = result.get("data", "") or result.get("error", "")
        assert case["expected_substring"].lower() in data.lower()
        
        
        
# @pytest.mark.parametrize("precision calculation", test_agent_top_20_questions)
# def test_main_agent_dynamic_part2(case):
#     result = main_agent(case["query"])

#     if case["expected_type"]:
#         assert result["type"] == case["expected_type"]

#     if case["expected_substring"]:
#         data = result.get("data", "") or result.get("error", "")
#         assert case["expected_substring"].lower() in data.lower()
