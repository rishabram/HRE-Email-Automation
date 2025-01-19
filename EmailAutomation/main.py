# main.py

import os
import pandas as pd
import re
from dotenv import load_dotenv
from O365 import Account, FileSystemTokenBackend
from sqlalchemy.exc import SQLAlchemyError

from db_logger import init_db, log_email  # Import from your separate db_logger.py

# Load environment variables from .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

print("CLIENT_ID:", CLIENT_ID)
print("CLIENT_SECRET:", CLIENT_SECRET)
print("TENANT_ID:", TENANT_ID)

# OAuth token storage in the local folder (so you don't have to login every time)
token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
credentials = (CLIENT_ID, CLIENT_SECRET)

def init_account():
    """
    Creates and authenticates an O365 Account object using Azure credentials.
    """
    account = Account(
        credentials,
        auth_flow_type='authorization',
        token_backend=token_backend,
        tenant_id=TENANT_ID
    )

    if not account.is_authenticated:
        # Provide a redirect URI that matches what you configured in Azure
        account.authenticate(
            scopes=['https://graph.microsoft.com/.default'],
            redirect_uri='https://login.microsoftonline.com/common/oauth2/nativeclient'
        )
    return account

def load_knowledge_base(csv_path='knowledge_base.csv'):
    """
    Loads FAQ data from the specified CSV and converts the 'keywords' column into a list.
    """
    df = pd.read_csv(csv_path)
    df['keywords'] = df['keywords'].apply(lambda x: [k.strip().lower() for k in x.split(',')])
    return df

def find_faq_match(email_subject, email_body, faq_df):
    """
    Returns the first matching FAQ row if any keyword is found in the email,
    otherwise returns None.
    """
    text = (email_subject + " " + email_body).lower()
    for _, row in faq_df.iterrows():
        for kw in row['keywords']:
            # Use a simple word-boundary search
            if re.search(r'\b{}\b'.format(re.escape(kw)), text):
                return row
    return None

def send_auto_reply(account, message, faq_row):
    """
    Sends an auto-reply to the sender with the matched FAQ answer.
    """
    mailbox = account.mailbox()
    new_message = mailbox.new_message()
    new_message.to.add(message.sender.address)
    new_message.subject = f"Re: {message.subject}"

    body_content = f"""
    Hello {message.sender.name or 'Student'},

    Thank you for contacting Housing & Residential Education at the University of Utah!

    Based on your question, here's some info that might help:

    {faq_row['answer_text']}

    For more details, check out:
    {faq_row['link']}

    If this doesn't address your question fully, feel free to reply or call us anytime.

    Best regards,
    The Housing Ambassador Team
    """
    new_message.body = body_content
    new_message.send()

def move_to_manual_review(message, folder_name="ManualReview"):
    """
    Moves the message to a 'ManualReview' folder if no FAQ match is found.
    """
    target_folder = message.folder.parent.get_folder(folder_name)
    if not target_folder:
        # Create the folder if it doesn't exist
        target_folder = message.folder.parent.create_child_folder(folder_name)
    message.move(target_folder)

def main():
    try:
        # 1. Initialize / Authenticate Account
        account = init_account()

        # 2. Load FAQ CSV
        faq_df = load_knowledge_base('knowledge_base.csv')

        # 3. Initialize DB
        db_engine = init_db('auto_reply_log.db')

        # 4. Grab the inbox folder
        mailbox = account.mailbox()
        inbox = mailbox.inbox_folder()

        # 5. Fetch up to 20 unread messages
        unread_messages = inbox.get_messages(limit=20, download_attachments=False)

        for message in unread_messages:
            if not message.is_read:
                email_subject = message.subject
                email_body = message.body or ""

                matched_faq = find_faq_match(email_subject, email_body, faq_df)

                if matched_faq is not None:
                    # Auto-reply and mark as read
                    send_auto_reply(account, message, matched_faq)
                    message.mark_as_read()
                    # Log with matched_faq['id']
                    log_email(db_engine, message.sender.address, email_subject, matched_faq['id'])
                else:
                    # Move to manual review
                    move_to_manual_review(message, folder_name="ManualReview")
                    log_email(db_engine, message.sender.address, email_subject, None)

        print("Processing completed. Check your mailbox and the DB log for updates.")

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()
