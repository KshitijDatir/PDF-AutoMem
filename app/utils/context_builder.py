import logging
import asyncio
from typing import List, Dict, Any, Optional
from app.utils.graph_db import get_related_edges, get_user_facts
from app.utils.helpers import text_processor

logger = logging.getLogger(__name__)

async def build_context(conn, query: str, user_id: str, chat_id: Optional[str], vector_results: List[Dict[str, Any]]) -> str:
    """
    Combines Vector Search results with Knowledge Graph facts and User Preferences.
    
    1. Extracts entities from the query.
    2. Queries the Graph DB for edges related to those entities.
    3. Queries user facts from the Graph DB based on chat_id.
    4. Formats it all into a single unified context string.
    """
    context_parts = []
    
    # 1. Fetch User Memory Facts (Global per user)
    user_facts = get_user_facts(conn, user_id=user_id)
    if user_facts:
        facts_str = "\n".join([f"- {fact['fact']}" for fact in user_facts])
        context_parts.append(f"### Persistent User Facts:\n{facts_str}\n")
        logger.info(f"Context Builder: Injected {len(user_facts)} global user facts.")
            
    # 2. Fetch Graph Memory (Document Entities)
    entities = await text_processor.extract_entities(query)
    if entities:
        logger.info(f"Context Builder: Extracted entities from query: {entities}")
        graph_edges = get_related_edges(conn, entities=entities, user_id=user_id, limit=10)
        
        if graph_edges:
            edges_str = "\n".join([f"- {edge['source_node']} {edge['relation']} {edge['target_node']}" for edge in graph_edges])
            context_parts.append(f"### Knowledge Graph Context (Fact Relationships):\n{edges_str}\n")
            logger.info(f"Context Builder: Injected {len(graph_edges)} graph relationships.")
            
    # 3. Fetch Vector Search Results (Document Chunks)
    if vector_results:
        chunks_str = ""
        for i, res in enumerate(vector_results, 1):
            chunks_str += f"\n--- Source Document: {getattr(res, 'filename', 'Unknown')} ---\n"
            chunks_str += f"{getattr(res, 'content', '')}\n"
            
        context_parts.append(f"### Document Context (Chunks):\n{chunks_str}\n")
        logger.info(f"Context Builder: Injected {len(vector_results)} vector chunks.")
        
    if not context_parts:
        return "No relevant context found in documents or memory."
        
    return "\n".join(context_parts)
