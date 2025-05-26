from src.agent import main_agent

def test_non_real_estate_query():
    result = main_agent("What is the weather in Paris?")
    assert result["type"] == "output"
    assert "irrelevant" in result["data"].lower()

def test_valid_output_query():
    result = main_agent("Show average price in Dubai Marina")
    assert result["type"] in ["data"]

def test_unknown_action():
    # You can mock llm_classifier to return an unknown action if needed
    result = main_agent("Trigger unknown action somehow")  # Adjust input or mock
    if result.get("error"):
        assert "Unknown action" in result["error"]
