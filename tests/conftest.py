# conftest.py
import pytest
import re
from pathlib import Path

results = {}
queries_map = {}

def pytest_sessionstart(session):
    query_file = Path("tests/ai_chatbot_real_estate_queries.txt")
    queries = query_file.read_text().splitlines()
    for i, q in enumerate(queries):
        qid = f"line_{i+1}"
        queries_map[qid] = q.strip()

def pytest_runtest_logreport(report):
    if report.when == "call":
        nodeid = report.nodeid
        status = "PASS" if report.passed else "FAIL"

        # Extract the ID from the nodeid — it should be line_1, line_2, etc.
        m = re.search(r"\[(line_\d+)\]$", nodeid)
        if m:
            query_id = m.group(1)
            query_text = queries_map.get(query_id)
            results[nodeid] = (status, query_text)
        else:
            results[nodeid] = (status, None)

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    with open("results_ai_chatbot_real_estate_queries.txt", "w") as f:
        for nodeid in sorted(results):
            status, query = results[nodeid]
            query_part = f' | "{query}"' if query else ""
            f.write(f"{nodeid}{query_part} :: {status}\n")
