
import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main([
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "--cov-config=.coveragerc",
        "tests/"
    ]))
