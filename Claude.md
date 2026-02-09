# Claude.md

## Project Overview

This project is a customer support routing system that classifies incoming customer queries and delegates them to specialized handlers. The system uses Large Language Models (LLMs) to intelligently route queries to the appropriate support channel.

## Architecture

### Core Components

#### 1. Query Router (`src/router/__init__.py`)
The main entry point for the application. The `CustomerSupportRouter` class:
- Receives incoming customer queries
- Delegates classification to the `QueryClassifier`
- Routes classified queries to appropriate handlers
- Returns structured responses

#### 2. Query Classifier (`src/router/classifier.py`)
Classifies customer queries into one of three categories:
- **REFUND_REQUEST**: Queries about refunds, returns, or refund status
- **TECHNICAL_SUPPORT**: Questions about technical issues, bugs, or app crashes
- **GENERAL_CHIT_CHAT**: General inquiries, feedback, or greetings

Uses an LLM with a system prompt to perform classification and includes error handling with fallback to GENERAL_CHIT_CHAT.

#### 3. Query Handlers (`src/router/handlers.py`)
Four handler classes implement specific logic for each query type:

**RefundHandler**
- Extracts order ID from query using regex
- Queries mock database for refund status
- Returns structured refund information

**TechnicalSupportHandler**
- Creates support tickets via external API
- Fetches solutions from knowledge base API
- Includes graceful fallback for API failures
- Returns ticket ID and solution to customer

**GeneralChatHandler**
- Uses LLM with customer support system prompt
- Generates natural, friendly responses
- No external dependencies, direct LLM invocation

**Handler (Abstract Base Class)**
- Defines the interface all handlers must implement
- Ensures consistent response format (QueryResponse)

#### 4. LLM Service (`src/services/llm.py`)
Wrapper for LangChain language models:
- **BaseLLM**: Abstract interface for all LLM providers
- **LangchainLLM**: Concrete implementation supporting any LangChain model
  - Converts dictionary messages to LangChain message objects
  - Handles async invocation
  - Extracts model information dynamically
  - Compatible with OpenAI, Anthropic Claude, Ollama, and other LangChain models

#### 5. Data Models (`src/models/schemas.py`)
- **QueryResponse**: Standardized response format with:
  - `route`: The classified query route type
  - `response`: The generated response text
  - `data`: Additional metadata (order IDs, ticket IDs, model names, etc.)

#### 6. Configuration (`config.py`)
- `REFUND_DATABASE`: Mock database mapping order IDs to refund statuses
- `SUPPORT_API_URL`: External API endpoint for technical support operations

## Data Flow

```
Customer Query
    ↓
CustomerSupportRouter.route_query()
    ↓
QueryClassifier.classify() → LLM classifies query
    ↓
Route Type determined (REFUND_REQUEST | TECHNICAL_SUPPORT | GENERAL_CHIT_CHAT)
    ↓
Appropriate Handler selected and executed
    ↓
Handler processes query (API calls, database lookups, or LLM invocation)
    ↓
QueryResponse returned with route, response text, and metadata
```


## Technology Stack

### Core Dependencies
- **langchain-core**: Base abstractions for LLM interfaces
- **langchain-openai**: OpenAI integration
- **langchain-anthropic**: Anthropic Claude integration
- **langgraph**: Workflow orchestration (available for future enhancements)

### Utilities
- **python-dotenv**: Environment variable management
- **loguru**: Enhanced logging with better formatting
- **pydantic**: Data validation and serialization
- **httpx**: Async HTTP client for external API calls
- **requests**: HTTP client library

## Configuration & Environment

### Environment Variables
The project uses a `.env` file for sensitive configuration:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```


Variables are automatically loaded by `python-dotenv` on application startup.

### Poetry Configuration
- Virtual environment created in-project (`.venv/`)
- Python 3.12+ required
- All dependencies defined in `pyproject.toml`

## Entry Point

The `main.py` file serves as the application entry point:
- Initializes the LLM provider (configurable: OpenAI or Anthropic)
- Creates the router instance
- Runs test queries through the system
- Logs classification results and responses

## Error Handling & Resilience

### Graceful Degradation
- **Classification Failures**: Falls back to GENERAL_CHIT_CHAT if LLM returns invalid route
- **API Failures**: Technical support handler returns fallback ticket ID and generic solution
- **Missing Data**: Refund queries return "Order not found" for non-existent IDs

### Logging
- Uses `loguru` for detailed operation tracking
- Logs route classification and query processing
- Helps with debugging and monitoring

## Extension Points

### Adding New Query Types
1. Add new enum value to `RouteType` in `classifier.py`
2. Create new handler class extending `Handler` in `handlers.py`
3. Register handler in `_initialize_handlers()` function in `__init__.py`
4. Update system prompt in `system_prompt.py` to recognize new category

### Switching LLM Providers
Change the model initialization in `main.py`:
```python
# Current
openai_model = ChatOpenAI(model='gpt-3.5-turbo')

# Alternative
claude_model = ChatAnthropic(model='claude-3-sonnet-20240229')
llm_provider = LangchainLLM(claude_model)
```


### Adding External Integrations
- Refund database can be replaced with real database query
- Technical support API URLs can point to actual services
- Additional handlers can call various backend services

## Testing

Run the test suite:
```shell script
poetry run python main.py
```


Test queries demonstrate:
- Refund request classification and handling
- Technical support ticket creation and solution fetching
- General chat response generation

## Code Style & Conventions

- **Async/Await**: Used throughout for non-blocking I/O
- **Type Hints**: Comprehensive type annotations for clarity
- **Docstrings**: Google-style docstrings for all classes and methods
- **Error Handling**: Try-except blocks with specific exception handling
- **Naming**: Clear, descriptive names following PEP 8

## Performance Considerations

- **Async Architecture**: Non-blocking I/O for API calls and LLM invocation
- **Connection Pooling**: `httpx.AsyncClient` reused within context managers
- **Timeout Handling**: 5-second timeout on external API calls
- **Efficient Logging**: Selective logging to avoid performance overhead

## Security Considerations

- API keys stored in `.env` file (not committed to repository)
- Environment variables loaded via `python-dotenv`
- No sensitive data logged or stored in responses
- `.gitignore` excludes `.env` file

## Future Enhancements

- Database integration for real order/refund tracking
- Real external API connections for technical support
- Rate limiting and request throttling
- Caching layer for frequently requested solutions
- Multi-language support via LLM prompts
- Conversation history management
- Analytics and metrics tracking
- Advanced routing based on customer history or priority