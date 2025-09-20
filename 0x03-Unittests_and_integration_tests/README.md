# 0x03-Unittests_and_integration_tests

## Description
This project is part of the ALX Backend Python curriculum, focusing on unit and integration testing in Python. It implements unit tests for utility functions in `utils.py` and both unit and integration tests for the `GithubOrgClient` class in `client.py`. The tests use the `unittest` framework, `parameterized` for test parameterization, and `unittest.mock` for mocking external dependencies.

## Files
- **utils.py**: Contains utility functions (`access_nested_map`, `get_json`, `memoize`) for accessing nested dictionaries, fetching JSON from URLs, and memoizing method calls.
- **client.py**: Defines the `GithubOrgClient` class for interacting with GitHub organization data via the GitHub API.
- **fixtures.py**: Provides test fixtures (`TEST_PAYLOAD`) for integration tests.
- **test_utils.py**: Unit tests for functions in `utils.py`, covering `access_nested_map`, `get_json`, and `memoize`.
- **test_client.py**: Unit and integration tests for `GithubOrgClient`, testing methods like `org`, `_public_repos_url`, `public_repos`, and `has_license`.

## Requirements
- Python 3.7
- Ubuntu 18.04 LTS
- `pycodestyle` 2.5 compliance
- Dependencies: `requests`, `parameterized`
- All files must be executable and include shebang (`#!/usr/bin/env python3`)

## Setup
1. Install dependencies:
   ```bash
   pip install requests parameterized