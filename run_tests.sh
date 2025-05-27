#!/bin/bash


# Run the test and save both stdout and stderr to result_summary.txt
pytest tests/test_agent.py --junitxml=results.xml > result_summary.txt 2>&1

echo "Test run complete."
echo "Summary written to result_summary.txt"
echo "JUnit report written to results.xml"
