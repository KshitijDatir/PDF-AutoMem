import logging
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def save_memory_node(conn, node_type: str, value: str, source_id: str, user_id: str) -> Optional[str]:
    """Save a single node to the Knowledge Graph. Returns the node ID or None on failure."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memory_nodes (type, value, source_id, user_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (type, value, source_id, user_id) DO UPDATE SET created_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (node_type, value, source_id, user_id)
            )
            node_id = cur.fetchone()[0]
            conn.commit()
            return str(node_id)
    except Exception as e:
        logger.error(f"Failed to save memory node for user {user_id}: {str(e)}", exc_info=True)
        conn.rollback()
        return None

def save_memory_edge(conn, source_node: str, relation: str, target_node: str, source_id: str, user_id: str, confidence: float = 1.0) -> Optional[str]:
    """Save an edge (relationship) between two nodes. Returns the edge ID or None on failure."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memory_edges (source_node, relation, target_node, confidence, source_id, user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_node, relation, target_node, source_id, user_id) DO UPDATE SET confidence = EXCLUDED.confidence
                RETURNING id
                """,
                (source_node, relation, target_node, confidence, source_id, user_id)
            )
            edge_id = cur.fetchone()[0]
            conn.commit()
            return str(edge_id)
    except Exception as e:
        logger.error(f"Failed to save memory edge for user {user_id}: {str(e)}", exc_info=True)
        conn.rollback()
        return None

def get_related_edges(conn, entities: List[str], user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve all edges where the given entities match and belong to the user."""
    if not entities:
        return []
        
    try:
        with conn.cursor() as cur:
            query = """
                SELECT source_node, relation, target_node, confidence, source_id, created_at
                FROM memory_edges
                WHERE user_id = %s AND (source_node = ANY(%s) OR target_node = ANY(%s))
                ORDER BY confidence DESC, created_at DESC
                LIMIT %s
            """
            cur.execute(query, (user_id, entities, entities, limit))
            rows = cur.fetchall()
            
            edges = []
            for row in rows:
                edges.append({
                    "source_node": row[0],
                    "relation": row[1],
                    "target_node": row[2],
                    "confidence": row[3],
                    "source_id": row[4],
                    "created_at": row[5]
                })
            return edges
    except Exception as e:
        logger.error(f"Failed to retrieve related edges: {str(e)}", exc_info=True)
        return []

def get_user_facts(conn, user_id: str, chat_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all user facts for a specific user, optionally filtered by chat_session."""
    try:
        with conn.cursor() as cur:
            sql = "SELECT value, created_at FROM memory_nodes WHERE type = 'user_fact' AND user_id = %s"
            params = [user_id]
            if chat_id:
                sql += " AND source_id = %s"
                params.append(chat_id)
            sql += " ORDER BY created_at DESC"
            
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return [{"fact": row[0], "created_at": row[1]} for row in rows]
    except Exception as e:
        logger.error(f"Failed to retrieve user facts for user {user_id}: {str(e)}", exc_info=True)
        return []

def clear_user_memory(conn, user_id: str) -> bool:
    """Deletes all Knowledge Graph data (nodes and edges) for a specific user."""
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM memory_edges WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM memory_nodes WHERE user_id = %s", (user_id,))
            conn.commit()
            logger.info(f"Cleared all memory for user: {user_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to clear memory for user {user_id}: {str(e)}", exc_info=True)
        conn.rollback()
        return False
