# conftest.py
import pytest
import re
from pathlib import Path

# Dictionary to store test results with their corresponding query text
results = {}

# Dictionary to map query IDs to their respective query text
queries_map = {}


def pytest_sessionstart(session):
    """
    Hook function that runs at the start of the pytest session.
    Reads queries from a file and maps them to unique IDs.

    Args:
        session: The pytest session object.
    """
    # Path to the file containing real estate queries
    query_file = Path("tests/ai_chatbot_real_estate_queries.txt")
    # Read the file and split it into lines
    queries = query_file.read_text().splitlines()
    # Map each query to a unique ID (e.g., line_1, line_2, etc.)
    for i, q in enumerate(queries):
        qid = f"line_{i + 1}"
        queries_map[qid] = q.strip()


def pytest_runtest_logreport(report):
    """
    Hook function that processes the test report after each test is run.
    Extracts the test status and associates it with the corresponding query.

    Args:
        report: The test report object containing details of the test run.
    """
    if report.when == "call":  # Only process the "call" phase of the test
        nodeid = report.nodeid  # Unique identifier for the test
        status = "PASS" if report.passed else "FAIL"  # Determine test status

        # Extract the query ID from the nodeid (e.g., line_1, line_2, etc.)
        m = re.search(r"\[(line_\d+)\]$", nodeid)
        if m:
            query_id = m.group(1)
            query_text = queries_map.get(query_id)  # Get the query text
            results[nodeid] = (status, query_text)
        else:
            # If no query ID is found, store the status with None as the query
            results[nodeid] = (status, None)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Hook function that runs at the end of the pytest session.
    Writes the test results to a file.

    Args:
        session: The pytest session object.
        exitstatus: The exit status of the pytest session.
    """
    # Write the test results to a file
    with open("results_ai_chatbot_real_estate_queries.txt", "w") as f:
        for nodeid in sorted(results):  # Sort results by nodeid
            status, query = results[nodeid]
            # Include the query text in the output if available
            query_part = f' | "{query}"' if query else ""
            f.write(f"{nodeid}{query_part} :: {status}\n")
