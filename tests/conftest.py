import pytest

results = {}

def pytest_runtest_logreport(report):
    if report.when == "call":
        nodeid = report.nodeid
        if "[" in nodeid and "]" in nodeid:
            query_id = nodeid.split("[")[-1].rstrip("]")
            status = "PASS" if report.passed else "FAIL"
            results[query_id] = status

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    with open("results_log.txt", "w") as f:
        for query_id in sorted(results):
            f.write(f"{query_id} :: {results[query_id]}\n")
