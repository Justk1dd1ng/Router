from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from models.llm import LLMResponse


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.

    Defines the interface that all LLM provider implementations must follow,
    enabling easy swapping between different LLM services (OpenAI, Anthropic, etc.).
    """
    @abstractmethod
    async def invoke(self, messages: list[dict]) -> LLMResponse:
        """
        Invoke the LLM with a list of messages.

        Args:
            messages: List of dictionaries with 'role' and 'content' keys.
                     role can be 'system', 'user', 'assistant', etc.
                     content is the message text.

        Returns:
            LLMResponse object containing the model's response and metadata.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used"""
        pass


class LangchainLLM(BaseLLM):
    """
    Wrapper for LangChain language models.

    Provides a unified interface for interacting with any LangChain-supported
    language model (OpenAI, Anthropic Claude, Ollama, etc.). Handles message
    format conversion and standardized response formatting.
    """
    def __init__(self, model: BaseLanguageModel):
        """
        Initialize the LangChain LLM wrapper.

        Args:
            model: Any LangChain BaseLanguageModel instance (e.g., ChatOpenAI,
                   ChatAnthropic, Ollama, etc.)
        """
        self.model = model

    async def invoke(self, messages: list[dict]) -> LLMResponse:
        """
        Invoke the LLM asynchronously with the provided messages.

        Converts dictionary-format messages to LangChain message objects,
        calls the model asynchronously, and wraps the response in an LLMResponse object.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.

        Returns:
            LLMResponse containing the model's response content and model name.
        """
        lc_messages = self._convert_messages(messages)
        response = await self.model.ainvoke(lc_messages)

        return LLMResponse(
            content=response.content,
            model=self.get_model_name()
        )

    def get_model_name(self) -> str:
        """
        Extract and return the model name from the underlying LangChain model.

        Attempts to retrieve the model name from various possible attributes
        (model_name, model) and falls back to the class name if neither is found.

        Returns:
            String representation of the model name.
        """
        if hasattr(self.model, 'model_name'):
            return self.model.model_name
        elif hasattr(self.model, 'model'):
            return self.model.model
        return self.model.__class__.__name__

    @staticmethod
    def _convert_messages(messages: list[dict]) -> list[BaseMessage]:
        """
        Convert dictionary-format messages to LangChain message objects.

        Transforms a list of message dictionaries into the appropriate LangChain
        message types (SystemMessage for 'system' role, HumanMessage for others).

        Args:
            messages: List of dictionaries with 'role' and 'content' keys.

        Returns:
            List of LangChain BaseMessage objects.
        """
        lc_messages = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'system':
                lc_messages.append(SystemMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        return lc_messages