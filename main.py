from datetime import datetime
from src.agent0_config import NewsConfigurator
from src.agent1_search import NewsScraper
from src.agent2_select import NewsSelector
from src.agent3_redact import NewsRedactor
from src.agent4_design import NewsDesigner
from src.common.logs import log_message

def main(): #python -X pycache_prefix=tmp\pycache .\main.py
    """
    Main pipeline script to orchestrate the newsletter creation process.
    """
    LOG_PATH = str(datetime.now().strftime('%Y-%m-%d'))

    # 0. Create directories
    try:
        log_message("Running Configuration: Checking Directories...", LOG_PATH)
        config_agent = NewsConfigurator(log_path=LOG_PATH)
        config_agent.run_configurator()
        log_message("Agent 0 completed successfully.", LOG_PATH)
    except Exception as e:
        log_message(f"Error in Configuration: {e}", LOG_PATH, log_level="ERROR")
        return
    
    log_message("Starting Newsletter Automation Process...", LOG_PATH)

    # 1. Search Content (Agent 1)
    try:
        log_message("Running Agent 1: Search Content...", LOG_PATH)
        search_agent = NewsScraper(log_path=LOG_PATH)
        search_agent.run_scraper()
        log_message("Agent 1 completed successfully.", LOG_PATH)
    except Exception as e:
        log_message(f"Error in Agent 1: {e}", LOG_PATH, log_level="ERROR")
        return

    # 2. Select Content (Agent 2)
    try:
        log_message("Running Agent 2: Select Content...", LOG_PATH)
        select_agent = NewsSelector(log_path=LOG_PATH)
        select_agent.run_selector()
        log_message("Agent 2 completed successfully.", LOG_PATH)
    except Exception as e:
        log_message(f"Error in Agent 2: {e}", LOG_PATH, log_level="ERROR")
        return

    # 3. Redact Content (Agent 3)
    try:
        log_message("Running Agent 3: Redact Content...", LOG_PATH)
        redact_agent = NewsRedactor(log_path=LOG_PATH)
        redact_agent.run_redactor()
        log_message("Agent 3 completed successfully.", LOG_PATH)
    except Exception as e:
        log_message(f"Error in Agent 3: {e}", LOG_PATH, log_level="ERROR")
        return

    # 4. Design Content (Agent 4)
    try:
        log_message("Running Agent 4: Design Content...", LOG_PATH)
        layout_agent = NewsDesigner(log_path=LOG_PATH)
        layout_agent.run_designer()
        log_message("Agent 4 completed successfully.", LOG_PATH)
    except Exception as e:
        log_message(f"Error in Agent 4: {e}", LOG_PATH, log_level="ERROR")
        return

    log_message("Newsletter Automation Process completed successfully.", LOG_PATH)

if __name__ == "__main__":
    main()