# db_logger.py
from sqlalchemy import create_engine

def init_db(db_name='auto_reply_log.db'):
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    with engine.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_address TEXT,
                subject TEXT,
                matched_faq_id TEXT,
                date_utc TEXT
            );
        """)
    return engine

def log_email(engine, email_address, subject, faq_id):
    insert_query = """
        INSERT INTO email_log (email_address, subject, matched_faq_id, date_utc) 
        VALUES (:email_address, :subject, :faq_id, datetime('now'))
    """
    with engine.begin() as conn:
        conn.execute(insert_query, {
            "email_address": email_address,
            "subject": subject,
            "faq_id": str(faq_id) if faq_id else None
        })
