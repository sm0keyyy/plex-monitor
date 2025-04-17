# Contributing to Plex Monitor

Thank you for considering contributing to Plex Monitor! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. A clear, descriptive title
2. A detailed description of the issue, including steps to reproduce
3. The expected behavior and what actually happened
4. Any relevant logs or error messages
5. Your environment (OS, Python version, etc.)

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue with the following information:

1. A clear, descriptive title
2. A detailed description of the enhancement
3. Why you think it would be valuable
4. Any implementation ideas you have

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Run the tests to ensure they pass
5. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/plex-monitor.git
   cd plex-monitor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a config file:
   ```bash
   python setup_config.py
   ```

5. Run the tests:
   ```bash
   python run_tests.py
   ```

## Coding Standards

- Follow PEP 8 style guidelines
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate
- Write unit tests for new functionality
- Keep functions small and focused on a single task
- Use meaningful variable and function names

## Testing

- All new features should include unit tests
- Run the existing tests before submitting a pull request
- Aim for high test coverage

## Documentation

- Update the README.md file with any new features or changes
- Document any new configuration options
- Include examples where appropriate

## Commit Messages

- Use clear, descriptive commit messages
- Start with a short summary line (50 chars or less)
- Optionally, follow with a blank line and a more detailed explanation

## Versioning

We use [Semantic Versioning](https://semver.org/) for this project:

- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward-compatible manner
- PATCH version for backward-compatible bug fixes

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

Thank you for your contributions!
