# HRE-Email-Automation with O365 and Python

## Overview

This a lite version of the project that automates responses to emails in a Microsoft 365 (Outlook) inbox. It checks for unread messages, determines if they match any known Frequently Asked Questions (FAQs) stored in a CSV, and sends auto-replies where possible. Unmatched emails are moved to a "ManualReview" folder for human follow-up. The system also logs all processed emails in an SQLite database.

**Key Features**:
- **FAQ Matching**: A CSV-based knowledge base with keywords to detect common housing-related questions.
- **Auto-Reply**: Automatically sends a reply (with dynamic information) if an email matches an FAQ.
- **Manual Review**: If no match is found, the email is moved to a special Outlook folder for manual attention.
- **Logging**: Logs each email transaction in a local SQLite database (`auto_reply_log.db`), recording the subject, sender, and the matched FAQ ID (if any).

## Technology Stack

- **Python 3.x**  
- **O365** library for Microsoft Graph/Outlook integration  
- **pandas** for CSV data manipulation  
- **SQLAlchemy** for database interaction (SQLite)  
- **python-dotenv** for loading secure credentials from a `.env` file  

## Prerequisites

1. **Microsoft 365 Tenant & App Registration**  
   - Azure App Registration with the following:
     - **API permissions**: `Mail.ReadWrite`, `Mail.Send`  
     - **Redirect URI** matching `https://login.microsoftonline.com/common/oauth2/nativeclient`  
   - **Client ID, Client Secret, Tenant ID** from Azure, stored in your `.env`.
2. **Python 3.9+** (recommended).

## Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/yourusername/EmailAutomation.git
   cd EmailAutomation
