from enum import Enum
from loguru import logger

from src.services.llm import LangchainLLM
from src.router.system_prompt import ROUTER_PROMPT, GENERAL_SUPPORT_PROMPT


class RouteType(str, Enum):
    """
    Enumeration of supported customer query route types.

    Attributes:
        REFUND_REQUEST: Queries related to refunds, returns, or refund status.
        TECHNICAL_SUPPORT: Queries about technical issues, bugs, or app crashes.
        GENERAL_CHIT_CHAT: General queries, greetings, or feedback.
    """
    REFUND_REQUEST = "REFUND_REQUEST"
    TECHNICAL_SUPPORT = "TECHNICAL_SUPPORT"
    GENERAL_CHIT_CHAT = "GENERAL_CHIT_CHAT"


def _parse_classification(classification_text: str) -> RouteType:
    """
    Parse LLM response text into a RouteType enum value.

    Attempts to match the LLM's response to a valid RouteType. If the response
    doesn't match any valid type, defaults to GENERAL_CHIT_CHAT and logs a warning.

    Args:
        classification_text: The raw text response from the LLM classifier.

    Returns:
        A RouteType enum value corresponding to the classification.
        Defaults to GENERAL_CHIT_CHAT if parsing fails.
    """
    try:
        return RouteType(classification_text.strip().upper())
    except ValueError:
        logger.warning(f"Invalid classification: {classification_text}. Switching to GENERAL_CHIT_CHAT.")
        return RouteType.GENERAL_CHIT_CHAT


class QueryClassifier:
    """
    Classifier for customer support queries.

    Uses an LLM to classify incoming customer queries into one of the predefined
    route types (refund request, technical support, or general chat).
    """
    def __init__(self, llm_provider: LangchainLLM):
        """
        Initialize the query classifier.

        Args:
            llm_provider: The LLM provider instance to use for classification.
        """
        self.llm = llm_provider
        self.prompt = ROUTER_PROMPT

    async def classify(self, query: str) -> RouteType:
        """
        Classify a customer query into one of the supported route types.

        Formats the query using the router prompt template, invokes the LLM
        to classify it, and parses the response into a RouteType enum value.

        Args:
            query: The customer query string to classify.

        Returns:
            RouteType enum value indicating the classification of the query.
        """
        formatted_messages = self.prompt.format_messages(query=query)
        messages_dict = [{"role": msg.type, "content": msg.content} for msg in formatted_messages]
        response = await self.llm.invoke(messages_dict)
        return _parse_classification(response.content)

