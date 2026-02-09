from loguru import logger
from src.router.classifier import QueryClassifier, RouteType
from src.router.handlers import RefundHandler, TechnicalSupportHandler, GeneralChatHandler
from src.services.llm import LangchainLLM
from src.models.schemas import QueryResponse


def _initialize_handlers(llm_provider: LangchainLLM) -> dict[RouteType, object]:
    """
    Initialize and return handler mapping for each route type.

    Creates handler instances for each supported route type and associates
    them with their corresponding route type enum values.

    Args:
        llm_provider: The LLM provider instance to pass to handlers that require it.

    Returns:
        Dictionary mapping RouteType enum values to their corresponding handler instances.
    """
    return {
        RouteType.REFUND_REQUEST: RefundHandler(),
        RouteType.TECHNICAL_SUPPORT: TechnicalSupportHandler(),
        RouteType.GENERAL_CHIT_CHAT: GeneralChatHandler(llm_provider)
    }


class CustomerSupportRouter:
    """
    Main router for customer support queries.

    Classifies incoming customer queries and routes them to the appropriate handler
    based on the query type (refund, technical support, or general chat).
    """
    def __init__(self, llm_provider: LangchainLLM):
        """
        Initialize the customer support router.

        Args:
            llm_provider: The LLM provider instance used for query classification.
        """
        self.classifier = QueryClassifier(llm_provider)
        self.handlers = _initialize_handlers(llm_provider)

    async def route_query(self, query: str) -> QueryResponse:
        """
        Classify and route a customer query to the appropriate handler.

        This method classifies the incoming query using the QueryClassifier,
        logs the classification result, and delegates handling to the appropriate
        handler based on the route type.

        Args:
            query: The customer's query string.

        Returns:
            QueryResponse object containing the route, response, and associated data.
        """
        route_type = await self.classifier.classify(query)
        logger.info(f"Classified as: {route_type.value}")
        handler = self.handlers[route_type]
        return await handler.handle(query)