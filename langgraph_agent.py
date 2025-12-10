"""
LangGraph Multi-Model Agent for Travel Assistant.

Extracted and adapted from Assignment D8 (Multi-Model Orchestration)

This module implements an intelligent multi-model routing system that selects
the most appropriate LLM based on query characteristics. It uses heuristic-based
routing to choose between Gemini 2.5 Flash (for simple queries) and Gemini 2.5 Pro
(for complex reasoning, technical, or creative queries).

Architecture:
    1. Query Classification: Heuristics identify query type (simple/complex/technical/creative)
    2. Model Selection: Router chooses optimal model based on classification
    3. Response Generation: Selected model processes query and returns response
    4. Conversation History: All interactions are logged with model attribution

Models Used:
    - Gemini 2.5 Flash: Fast, efficient for simple factual queries
    - Gemini 2.5 Pro: Advanced reasoning for complex queries

Integration:
    - Used by agent.py through LangGraphLLMAdapter
    - Provides create_graph() entry point for LiveKit integration
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
    """Initialize and configure all LLM models for multi-model routing.

    Creates instances of Gemini 2.5 Flash and Pro models with optimized
    configurations. Flash is used for quick, factual responses while Pro
    handles complex reasoning tasks.

    Returns:
        dict: Dictionary mapping model names to initialized ChatGoogleGenerativeAI instances
              Keys: 'gemini_25_flash', 'gemini_25_pro'

    Raises:
        ValueError: If GOOGLE_API_KEY environment variable is not set

    Note:
        Temperature is set to 0.7 for balanced creativity and coherence.
        System messages are converted to human format for Gemini compatibility.
    """
    # Retrieve Google API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    # Initialize both Gemini models with consistent configuration
    models = {
        # Fast model for simple queries (weather, facts, definitions)
        "gemini_25_flash": ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7,  # Balanced creativity
            convert_system_message_to_human=True,  # Gemini compatibility
        ),
        # Advanced model for complex reasoning (analysis, comparisons, technical)
        "gemini_25_pro": ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=api_key,
            temperature=0.7,  # Balanced creativity
            convert_system_message_to_human=True,  # Gemini compatibility
        ),
    }

    return models


# ============================================================================
# Query Classification Heuristics
# ============================================================================


def is_simple_query(text: str) -> bool:
    """Detect if a query is simple/factual requiring fast response.

    Simple queries are typically:
    - Short (8 words or less)
    - Direct questions (what/who/when/where)
    - Requesting facts, definitions, or basic information

    These queries are routed to Gemini Flash for quick responses.

    Args:
        text: User query text

    Returns:
        bool: True if query appears to be simple/factual, False otherwise

    Examples:
        - "What is the capital of France?" -> True
        - "How many continents are there?" -> True
        - "Explain quantum mechanics" -> False
    """
    text_lower = text.lower().strip()

    # Simple queries are typically concise (8 words or fewer)
    if len(text.split()) <= 8:
        # Patterns indicating simple factual questions
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
    """Detect if a query requires deep reasoning or detailed explanation.

    Complex queries typically involve:
    - Explanations of concepts or processes
    - Analytical thinking (compare, contrast, analyze)
    - Cause-and-effect reasoning
    - Step-by-step instructions
    - Understanding relationships and implications

    These queries are routed to Gemini Pro for advanced reasoning.

    Args:
        text: User query text

    Returns:
        bool: True if query requires complex reasoning, False otherwise

    Examples:
        - "Explain how machine learning works" -> True
        - "Compare Python and JavaScript" -> True
        - "What is Python?" -> False
    """
    text_lower = text.lower().strip()

    # Keywords indicating need for deep reasoning or analysis
    complex_indicators = [
        "explain",  # Requests for explanations
        "why",  # Causal reasoning
        "how does",  # Process understanding
        "how do",
        "reasoning",  # Explicit reasoning request
        "step by step",  # Detailed procedures
        "analyze",  # Analytical thinking
        "compare",  # Comparative analysis
        "contrast",
        "differences between",
        "relationship between",
        "implications",  # Understanding consequences
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

    # Log model selection
    print("🤖 MODEL ROUTING:")
    print(f"   Query: {user_query[:100]}...")
    print(f"   Selected: {chosen_model_name.upper()}")
    print(f"   Reason: {reason}")

    # Get the chosen model
    chosen_model = models[chosen_model_name]

    # Call the model
    try:
        print(f"📞 CALLING {chosen_model_name}...")
        response = chosen_model.invoke(user_query)
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )
        print(f"✅ {chosen_model_name} RESPONDED (length={len(response_text)})")
    except Exception as e:
        print(f"❌ ERROR from {chosen_model_name}: {str(e)}")
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
        print("\n" + "=" * 70)
        print("🔷 LANGGRAPH INVOKE STARTED")
        print("=" * 70)

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

        print("=" * 70)
        print(f"🔶 FINAL RESULT: Using {result['chosen_model'].upper()}")
        print(f"   Response preview: {result['response'][:100]}...")
        print("=" * 70 + "\n")

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
