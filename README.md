# Getting Started

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.12 or higher
- Poetry (Python package manager)

If you don't have Poetry installed, follow the [official installation guide](https://python-poetry.org/docs/#installation).

## Installation Steps

### 1. Clone the Repository

```shell script
git clone <repository-url>
cd router
```


### 2. Install Dependencies

Poetry will automatically create a virtual environment in the project directory (as configured in `poetry.toml`).

```shell script
poetry install
```


This command will:
- Create a virtual environment in `.venv` directory
- Install all project dependencies from `pyproject.toml`
- Set up the development environment

### 3. Set Up Environment Variables

The project requires API keys for LLM providers. Create a `.env` file in the project root directory:

```shell script
touch .env
```


Add your API keys to the `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```


Replace the placeholder values with your actual API keys:

- **OpenAI API Key**: Get it from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic API Key**: Get it from [Anthropic Console](https://console.anthropic.com/)

**Security Note**: Never commit the `.env` file to version control. The `.gitignore` file should already exclude it.

### 4. Verify Installation

Run the following command to verify that everything is set up correctly:

```shell script
poetry run python main.py
```


This will execute the test cases defined in `main.py` using the configured LLM provider.

## Project Structure

```
interview/
├── src/
│   ├── router/              # Query routing and classification
│   │   ├── __init__.py      # Main router class
│   │   ├── classifier.py    # Query classification logic
│   │   ├── handlers.py      # Query handlers for each route type
│   │   └── system_prompt.py # LLM prompts
│   ├── services/
│   │   └── llm.py          # LLM provider wrapper
│   └── models/
│       └── schemas.py      # Data models and schemas
├── config.py               # Configuration constants
├── main.py                 # Entry point for testing
├── pyproject.toml          # Project dependencies
├── poetry.toml             # Poetry configuration
├── .env                    # Environment variables (create this)
└── README.md               # Project documentation
```


## Running the Application

### Using Poetry

To run the application with Poetry:

```shell script
poetry run python main.py
```


### Activating the Virtual Environment

Alternatively, activate the virtual environment and run directly:

```shell script
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```


## Managing Dependencies

### Adding a New Dependency

```shell script
poetry add package_name
```


### Updating Dependencies

```shell script
poetry update
```


### Installing Development Dependencies

If you need to add development-only dependencies:

```shell script
poetry add --group dev package_name
```


## Environment Variables Reference

The following environment variables are used by the project:

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API authentication | Yes (if using OpenAI) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API authentication | Yes (if using Claude) |

These are automatically loaded by the `python-dotenv` package when the application starts.

## Troubleshooting

### Poetry Cache Issues

If you encounter issues during installation, try clearing the Poetry cache:

```shell script
poetry cache clear . --all
poetry install
```


### Python Version Mismatch

Ensure your Python version matches the requirement (3.12+):

```shell script
python --version
```


If you have multiple Python versions installed, you can specify which one Poetry should use:

```shell script
poetry env use /path/to/python3.12
poetry install
```


### Missing API Keys

If you get authentication errors when running the application:

1. Verify the `.env` file exists in the project root
2. Check that API keys are correctly formatted (no extra spaces)
3. Ensure the `.env` file is readable by your user
4. Restart your terminal or IDE after creating/modifying the `.env` file

### Import Errors

If you encounter import errors, ensure the virtual environment is activated:

```shell script
poetry shell
python main.py
```


## Next Steps

After successful setup, you can:

1. Review the test cases in `main.py` to understand the router's behavior
2. Modify the LLM provider in `main.py` to use a different model
3. Add custom handlers for new query types in `src/router/handlers.py`
4. Adjust system prompts in `src/router/system_prompt.py`

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)