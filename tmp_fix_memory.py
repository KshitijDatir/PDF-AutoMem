from app.celery_app import extract_user_memory, process_ocr
from app.utils.helpers import get_db_connection
import asyncio

def fix_memory():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Re-trigger chat extraction for the latest chat
            cur.execute("SELECT chat_id, user_id FROM chat_sessions ORDER BY updated_at DESC LIMIT 1;")
            chat = cur.fetchone()
            if chat:
                print(f"Re-triggering memory extraction for chat: {chat[0]}")
                extract_user_memory.delay(chat[0], chat[1])
            
            # 2. Re-trigger graph extraction for all processed documents
            cur.execute("SELECT file_id, user_id, file_type, category, filename FROM file_metadata WHERE status = 'processed';")
            docs = cur.fetchall()
            for doc in docs:
                print(f"Re-triggering OCR processing (graph part) for file: {doc[4]}")
                process_ocr.delay(doc[0], doc[1], doc[2], doc[3], doc[4])
    finally:
        conn.close()

if __name__ == "__main__":
    fix_memory()
