"""
LangGraph Agent for Travel Assistant
Extracted from D8 Multi-Model Orchestration Assignment

This module provides a simplified interface for multi-model orchestration
using LangChain models with router pattern for intelligent model selection.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()


# ============================================================================
# Model Configuration
# ============================================================================


def setup_models():
    """Initialize and return all LLM models used in the agent."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    # Initialize Gemini models with different configurations
    models = {
        "gemini_25_flash": ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True,
        ),
        "gemini_25_pro": ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True,
        ),
    }

    return models


# ============================================================================
# Query Classification Heuristics
# ============================================================================


def is_simple_query(text: str) -> bool:
    """Detect if a query is simple/factual (short, direct questions)."""
    text_lower = text.lower().strip()

    # Check length - simple queries are usually short
    if len(text.split()) <= 8:
        # Check for simple question patterns
        simple_patterns = [
            "what is",
            "who is",
            "when is",
            "where is",
            "what's",
            "who's",
            "when's",
            "where's",
            "define",
            "meaning of",
            "capital of",
            "how many",
            "how much",
            "how old",
        ]
        if any(pattern in text_lower for pattern in simple_patterns):
            return True

    return False


def is_complex_query(text: str) -> bool:
    """Detect if a query requires deep reasoning or explanation."""
    text_lower = text.lower().strip()

    complex_indicators = [
        "explain",
        "why",
        "how does",
        "how do",
        "reasoning",
        "step by step",
        "analyze",
        "compare",
        "contrast",
        "differences between",
        "relationship between",
        "implications",
        "consequences",
        "effect of",
    ]

    return any(indicator in text_lower for indicator in complex_indicators)


def is_creative_query(text: str) -> bool:
    """Detect if a query requires creative output."""
    text_lower = text.lower().strip()

    creative_keywords = [
        "write a story",
        "poem",
        "creative",
        "imagine",
        "compose",
        "draft",
        "marketing",
        "slogan",
        "brainstorm",
        "design",
        "invent",
    ]

    return any(keyword in text_lower for keyword in creative_keywords)


def is_technical_query(text: str) -> bool:
    """Detect if a query is technical/coding related."""
    text_lower = text.lower().strip()

    technical_keywords = [
        "code",
        "python",
        "javascript",
        "function",
        "algorithm",
        "implement",
        "debug",
        "sql",
        "api",
        "class",
        "programming",
        "software",
        "developer",
        "technical",
    ]

    return any(keyword in text_lower for keyword in technical_keywords)


# ============================================================================
# Router Pattern Implementation
# ============================================================================


def route_query(user_query: str, models: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route query to the best single model based on heuristics.

    Args:
        user_query: The user's input query
        models: Dictionary of initialized LLM models

    Returns:
        dict with keys:
        - chosen_model: str (name of the model)
        - reason: str (explanation for model choice)
        - response: str (model's answer)
    """
    # Determine which model to use based on query characteristics
    if is_simple_query(user_query):
        chosen_model_name = "gemini_25_flash"
        reason = "Simple factual query - using fast Gemini 2.5 Flash"
    elif is_complex_query(user_query):
        chosen_model_name = "gemini_25_pro"
        reason = "Complex reasoning query - using Gemini 2.5 Pro"
    elif is_technical_query(user_query):
        chosen_model_name = "gemini_25_pro"
        reason = "Technical/coding query - using Gemini 2.5 Pro"
    elif is_creative_query(user_query):
        chosen_model_name = "gemini_25_pro"
        reason = "Creative query - using Gemini 2.5 Pro"
    else:
        # Default to flash for general queries
        chosen_model_name = "gemini_25_flash"
        reason = "General query - using Gemini 2.5 Flash"

    # Get the chosen model
    chosen_model = models[chosen_model_name]

    # Call the model
    try:
        response = chosen_model.invoke(user_query)
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )
    except Exception as e:
        response_text = f"Error calling model: {str(e)}"

    return {
        "chosen_model": chosen_model_name,
        "reason": reason,
        "response": response_text,
    }


# ============================================================================
# Graph Interface (Required by Assignment)
# ============================================================================


class TravelAssistantGraph:
    """
    A wrapper class that acts as a 'graph' for the travel assistant.
    This provides the interface expected by the LiveKit agent.
    """

    def __init__(self):
        """Initialize the graph with models."""
        self.models = setup_models()
        self.conversation_history = []

    def invoke(self, user_input: str) -> str:
        """
        Process user input through the graph and return a response.

        Args:
            user_input: The user's message/query

        Returns:
            str: The agent's response
        """
        # Route the query to the appropriate model
        result = route_query(user_input, self.models)

        # Store in conversation history
        self.conversation_history.append(
            {
                "user": user_input,
                "assistant": result["response"],
                "model": result["chosen_model"],
                "reason": result["reason"],
            }
        )

        return result["response"]

    def get_last_model_used(self) -> str:
        """Get the name of the last model that was used."""
        if self.conversation_history:
            return self.conversation_history[-1]["model"]
        return "none"


# ============================================================================
# Public API (Required by Assignment)
# ============================================================================


def create_graph() -> TravelAssistantGraph:
    """
    Create and return a travel assistant graph instance.

    This is the main entry point required by the LiveKit agent.

    Returns:
        TravelAssistantGraph: Initialized graph ready to process queries
    """
    return TravelAssistantGraph()


def invoke_graph(graph: TravelAssistantGraph, user_input: str) -> str:
    """
    Invoke the graph with user input and get a response.

    Args:
        graph: An initialized TravelAssistantGraph instance
        user_input: The user's message/query

    Returns:
        str: The agent's response
    """
    return graph.invoke(user_input)


# ============================================================================
# Testing and Debug
# ============================================================================

if __name__ == "__main__":
    # Test the agent
    print("=" * 70)
    print("LANGGRAPH AGENT TEST")
    print("=" * 70)

    # Create graph
    graph = create_graph()

    # Test queries
    test_queries = [
        "What is the capital of France?",
        "Explain how neural networks work step by step",
        "Write a Python function for binary search",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        response = invoke_graph(graph, query)
        print(f"Response: {response[:200]}...")
        print(f"Model used: {graph.get_last_model_used()}")
        print("-" * 70)
