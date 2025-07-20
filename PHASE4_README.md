# Phase 4: Frontend Testing Implementation

This phase implements comprehensive test cases for the frontend components of Toshy, ensuring that buttons and other UI elements work correctly.

## Overview

The frontend testing framework is designed to test the GUI components of Toshy, particularly the GTK4 interface. The tests cover:

1. Basic UI component rendering
2. Button click functionality
3. Form input and validation
4. Theme switching
5. Service control buttons

## Test Structure

The tests are organized into several files:

- `tests/conftest.py`: Contains test fixtures and setup for GUI testing
- `tests/test_gui_components.py`: Tests for basic UI component rendering
- `tests/test_gui_buttons.py`: Tests for button click functionality
- `tests/test_gui_forms.py`: Tests for form input and validation
- `pytest.ini`: Configuration for test markers and settings
- `.github/workflows/test.yml`: GitHub Actions workflow for CI/CD

## Running the Tests

### Local Testing

To run the frontend tests locally:

```bash
# Run all tests
pytest tests/

# Run only frontend tests
pytest tests/ -m frontend

# Run only backend tests
pytest tests/ -m "not frontend"

# Run with coverage report
pytest --cov=toshy tests/
```

### Headless Testing

For headless testing (e.g., in CI/CD environments):

```bash
# Install Xvfb
sudo apt-get install xvfb

# Run tests with Xvfb
xvfb-run --auto-servernum pytest tests/ -m frontend
```

## Test Markers

The following test markers are available:

- `frontend`: Marks tests as frontend tests
- `backend`: Marks tests as backend tests
- `slow`: Marks tests as slow (deselect with `-m "not slow"`)
- `integration`: Marks tests as integration tests

## CI/CD Integration

The GitHub Actions workflow in `.github/workflows/test.yml` automatically runs the tests on push to main and cline branches, as well as on pull requests to main. It:

1. Sets up a Python environment
2. Installs GTK4 and other dependencies
3. Runs backend tests
4. Runs frontend tests with Xvfb
5. Generates and uploads a coverage report

## Test Fixtures

The test fixtures in `conftest.py` provide:

1. A GTK application instance
2. A main window instance
3. Settings panel and service panel instances
4. Mock configuration file handling

These fixtures make it easy to test different aspects of the GUI without duplicating setup code.

## Handling Different GTK Versions

The tests are designed to work with both GTK4 and GTK3, with a preference for GTK4. If neither is available, the tests will be skipped with appropriate messages.

## Mocking

The tests use extensive mocking to avoid dependencies on actual system services and configuration files. This makes the tests more reliable and faster to run.

## Future Improvements

1. Add more specific tests for each UI component
2. Add visual regression testing
3. Add end-to-end testing with real user scenarios
4. Improve test coverage for edge cases
5. Add performance testing for UI responsiveness

## Integration with NixOS

The frontend tests are integrated with the NixOS flake in `~/sources/nixos/flake.nix`, which provides a development environment with all the necessary dependencies for running the tests.

To use this environment:

```bash
cd ~/sources/nixos
nix develop
```

This will provide a shell with all the necessary tools for running the tests, including GTK4, pytest, and Xvfb.
