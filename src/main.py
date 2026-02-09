import asyncio

from loguru import logger
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from src.router import CustomerSupportRouter
from src.services.llm import LangchainLLM


load_dotenv()


async def main():
    # Initialize LLM provider. It doesn't necessarily have to be an OpenAI provider
    openai_model = ChatOpenAI(model='gpt-3.5-turbo')
    llm_provider = LangchainLLM(openai_model)

    # Create router
    router = CustomerSupportRouter(llm_provider)

    # Test cases
    test_queries = [
        "Where is my refund for order #12345?",
        "The app keeps crashing on login",
        "Hi! Just wanted to say your service is great!"
    ]

    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Test Case {i}: {query}")
        logger.info('=' * 60)

        result = await router.route_query(query)
        logger.info(f"Route: {result.route}")
        logger.info(f"Response: {result.response}")
        logger.info(f"Data: {result.data}")


if __name__ == "__main__":
    asyncio.run(main())