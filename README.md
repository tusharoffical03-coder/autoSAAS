# Global AI Lead Engine v3.5 - Setup & Execution Guide

Follow these steps to run the refined lead generation system:

## 1. Prerequisites
*   **Python 3.8+** installed.
*   **Playwright Browsers**: Run the following command after installing dependencies:
    ```bash
    playwright install chromium
    ```

## 2. Environment Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **API Key**: Ensure your Gemini API key is in the `.env` file:
    ```env
    GEMINI_API_KEY="your_api_key_here"
    ```

## 3. Launching the Dashboard (Recommended)
The easiest way to use the system is through the interactive web dashboard:
1.  **Start the Server**:
    ```bash
    python app.py
    ```
2. **Access UI**: Open `http://127.0.0.1:8000` or `http://localhost:8000` in your browser.
   - *Note*: `0.0.0.0` is the host address, but you should use `127.0.0.1` in your browser bar.
3.  **Generate Leads**: Enter a Niche (e.g., "Med Spa") and Location (e.g., "Miami") and click **GENERATE LEADS**. The swarm agents will start working in the background.

**Important**: Make sure you keep the terminal window open where the script is running. If you close the terminal, the website will stop working.

## 4. Troubleshooting
- **Port 8000 already in use**: If you see an error saying the port is busy, you can change the port in `app.py` (e.g., to 8080) or kill the existing process.
- **Connection Refused**: Ensure you have run `python app.py` and it says "Application startup complete."

## 5. Running the Swarm Orchestrator (CLI)
If you want to run the automated cycle without the UI:
```bash
python multi_agent_orchestrator.py
```
This will systematically cycle through the targets defined in the script and populate the database.

## 5. Running the AI Enricher
To analyze and score "New" leads found by the scrapers:
```bash
python enricher.py
```

## 6. Database Migration
If you are upgrading from an older version, run this once to update your database schema:
```bash
python migrate_db.py
```

---
**Note:** For more details on what this system can do, see `CAPABILITIES.md`.
