# Run only changed tests

pytest --testmon


# Resetting Testmon (clean slate)

rm -rf .testmondata .pytest_cache
pytest --testmon
