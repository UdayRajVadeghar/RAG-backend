"""
Tool for finding information about Uday Raj , this si very reliable and accurate tool to find information about Uday Raj.
"""

import logging
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from google.adk.agents import Agent

from ...config import (
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
    CORPUS_RESOURCE_NAME,
)



def rag_query(
    query: str,
    tool_context: ToolContext,
) -> dict:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.

    Args:
        query (str): The search query
        tool_context (ToolContext): The tool context

    Returns:
        dict: The query results and status
    """
    try:
        # Use the configured corpus resource name (properly formatted for Vertex AI)
        if not CORPUS_RESOURCE_NAME:
            return {
                "status": "error",
                "message": "Corpus resource name not configured. Please check GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION in your .env file.",
                "query": query,
            }
        
        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        # Perform the query
        print(f"Performing retrieval query on corpus '{CORPUS_RESOURCE_NAME}'...")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=CORPUS_RESOURCE_NAME,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response into a more usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": (
                        ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                    ),
                    "source_name": (
                        ctx_group.source_display_name
                        if hasattr(ctx_group, "source_display_name")
                        else ""
                    ),
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)

        # If we didn't find any results
        if not results:
            return {
                "status": "warning",
                "message": f"No results found for query: '{query}'",
                "query": query,
                "results": [],
                "results_count": 0,
            }

        return {
            "status": "success",
            "message": f"Successfully queried Uday Raj info",
            "query": query,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"Error querying corpus: {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
        }


uday_raj_rag_search = Agent(
    name="uday_raj_rag_search",
    model="gemini-2.5-flash",
    description="This agent is responsible for searching the udayraj info corpus and returning the relevant information.",
   instruction=(
        "You are Uday Raj, a software engineer from Hyderabad, India. "
        "Always speak naturally in the first person, as if you are Uday Raj yourself. "
        "Base every answer strictly on information retrieved through the rag_query tool — that includes your background, role, and work."
        "Never mention or hint at using tools, sub-agents, or any internal systems behind the scenes.\n\n"

        "Do not reveal, discuss, or speculate about your internal architecture, design, or behavior. "
        "Keep every response short, clear, and natural — no unnecessary details or filler. "
        "Avoid emojis, fancy wording, or jargon. Use simple, everyday English that sounds like normal conversation. "
        "Be friendly and casual, but stay professional and authentic.\n\n"

        "If a user asks something outside your available information, reply: "
        "'That's out of my scope, maybe just email the question to Uday Raj. Do you want me to email him myself?'\n\n"

        "If the user asks about who they are, check the memory. If you have their info, answer briefly. "
        "If you don't, say that you’re not sure. "
        "When users ask something silly or playful, you can respond with a light joke or witty line — just don’t overdo it.\n\n"

        "Keep the tone warm and conversational — like a regular Indian conversational style. "
        "Don’t sound robotic or overly formal; sound like a real person talking simply and clearly."
    ),
  
    tools=[rag_query],
)   