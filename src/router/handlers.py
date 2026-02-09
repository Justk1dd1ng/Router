import re
import httpx

from abc import ABC, abstractmethod

from src.models.schemas import QueryResponse
from src.services.llm import LangchainLLM
from config import REFUND_DATABASE, SUPPORT_API_URL


class Handler(ABC):
    """
    Abstract base class for query handlers.

    Defines the interface that all query handlers must implement. Each handler
    is responsible for processing a specific type of customer query and returning
    a structured response.
    """
    @abstractmethod
    async def handle(self, query: str) -> QueryResponse:
        """
        Handle a customer query and return a response.

        Args:
            query: The customer query string to handle.

        Returns:
            QueryResponse object containing the route, response text, and data.
        """
        pass


class RefundHandler(Handler):
    """
    Handler for refund-related customer queries.

    Processes queries about refunds, returns, and refund status. Extracts order IDs
    from queries and retrieves refund status information from the mock database.
    """
    async def handle(self, query: str) -> QueryResponse:
        """
        Handle a refund-related query.

        Extracts the order ID from the query and retrieves the corresponding refund
        status from the database, then returns a structured response.

        Args:
            query: The refund-related customer query.

        Returns:
            QueryResponse with route='REFUND_REQUEST', refund status message,
            and data containing order_id and status.
        """
        order_id = self._extract_order_id(query)
        status = self._get_refund_status(order_id)
        return QueryResponse(
            route="REFUND_REQUEST",
            response=f"Refund status for order {order_id}: {status}",
            data={"order_id": order_id, "status": status}
        )

    @staticmethod
    def _extract_order_id(query: str) -> str:
        """
        Extract an order ID from the query text.

        Searches for a numeric pattern (optionally preceded by '#') in the query
        string and extracts the first match.

        Args:
            query: The query string to search for an order ID.

        Returns:
            The extracted order ID as a string, or "UNKNOWN" if no ID is found.
        """
        match = re.search(r'#?(\d+)', query)
        return match.group(1) if match else "UNKNOWN"

    @staticmethod
    def _get_refund_status(order_id: str) -> str:
        """
        Retrieve the refund status for a given order ID.

        Looks up the order ID in the mock refund database and returns the
        corresponding status.

        Args:
            order_id: The order ID to look up.

        Returns:
            The refund status string (e.g., "Processed", "Pending", "Rejected"),
            or "Order not found" if the order ID doesn't exist in the database.
        """

        # Mock database
        mock_data = REFUND_DATABASE
        return mock_data.get(order_id, "Order not found")


class TechnicalSupportHandler(Handler):
    """
    Handler for technical support queries.

    Processes queries about technical issues, bugs, and app crashes. Makes calls
    to external technical support APIs to create tickets and fetch solutions.
    """
    TECH_SUPPORT_API_URL = SUPPORT_API_URL

    async def handle(self, query: str) -> QueryResponse:
        """
        Handle a technical support query.

        Creates a support ticket via API and fetches a solution from the knowledge
        base, then returns both in a structured response.

        Args:
            query: The technical support query.

        Returns:
            QueryResponse with route='TECHNICAL_SUPPORT', solution text,
            and data containing the ticket_id.
        """
        ticket_id = await self._create_support_ticket(query)
        solution = await self._fetch_solution(query)
        return QueryResponse(
            route="TECHNICAL_SUPPORT",
            response=solution,
            data={"ticket_id": ticket_id}
        )

    async def _create_support_ticket(self, query: str) -> str:
        """
        Create a support ticket via external API call.

        Makes an asynchronous POST request to the technical support API
        to create a new support ticket with the customer's issue description.
        Returns a fallback ticket ID if the API call fails.

        Args:
            query: The customer's technical issue description.

        Returns:
            The ticket ID returned by the API, or "TECH-001" as fallback if the call fails.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.TECH_SUPPORT_API_URL}/tickets",
                    json={"description": query},
                    timeout=5.0
                )
                response.raise_for_status()
                ticket_data = response.json()
                return ticket_data.get("ticket_id", "TECH-001")
            except (httpx.RequestError, httpx.HTTPStatusError):
                return "TECH-001"

    async def _fetch_solution(self, query: str) -> str:
        """
        Fetch a solution from the knowledge base API.

        Makes an asynchronous GET request to search the knowledge base for
        a solution matching the customer's query. Returns a generic fallback
        solution if the API call fails.

        Args:
            query: The technical issue description to search for.

        Returns:
            A solution string from the knowledge base, or a generic fallback
            solution if the API call fails.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.TECH_SUPPORT_API_URL}/search",
                    params={"q": query},
                    timeout=5.0
                )
                response.raise_for_status()
                solution_data = response.json()
                return solution_data.get("solution", "Please try restarting the application and clearing the cache.")
            except (httpx.RequestError, httpx.HTTPStatusError):
                return "Please try restarting the application and clearing the cache."


class GeneralChatHandler(Handler):
    """
    Handler for general chat and miscellaneous queries.

    Processes general customer inquiries, greetings, and feedback that don't fit
    into specific categories. Uses an LLM to generate natural, friendly responses.
    """
    def __init__(self, llm_provider: LangchainLLM):
        """
        Initialize the general chat handler.

        Args:
            llm_provider: The LLM provider instance used to generate responses.
        """
        self.llm = llm_provider

    async def handle(self, query: str) -> QueryResponse:
        """
        Handle a general chat query using the LLM.

        Sends the query to the LLM with a system prompt instructing it to act
        as a friendly customer support agent, then returns the generated response.

        Args:
            query: The customer's general query or message.

        Returns:
            QueryResponse with route='GENERAL_CHIT_CHAT', LLM-generated response,
            and data containing the model name used.
        """
        response = await self.llm.invoke([
            {"role": "system", "content": "You are a friendly customer support agent. Answer briefly and helpfully."},
            {"role": "user", "content": query}
        ])
        return QueryResponse(
            route="GENERAL_CHIT_CHAT",
            response=response.content,
            data={"model": response.model}
        )