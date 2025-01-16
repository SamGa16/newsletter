from os import path, listdir
from json import load
from datetime import datetime
from src.agent4_design.config import load_config
from src.common.path import get_full_path
from src.common.logs import log_message

class NewsDesigner:
    def __init__(self, log_path=None):
        self.config = load_config()
        self.RDCT_DATA_DIR = get_full_path(self.config["paths"]["input"])
        self.NEWSLETTER_DIR = get_full_path(self.config["paths"]["output"])
        self.TMPLT_PATH = get_full_path(self.config["paths"]["template"])

        if log_path:
            self.logs = log_path
        else:
            self.logs = self.config["logs"]

    def load_data(self):
        """
        Load redacted data in JSON format.
        """
        files = [f for f in listdir(self.RDCT_DATA_DIR) if f.endswith(".json")]
        if not files:
            log_message(f"Error: No redacted data files found in {self.RDCT_DATA_DIR}", self.logs, log_level="ERROR")
            raise FileNotFoundError("No redacted data files found in the redacted data directory.")
        
        # Load the latest file by modification date
        latest_file = max(files)
        with open(path.join(self.RDCT_DATA_DIR, latest_file), "r", encoding="utf-8") as f:
            return load(f)
        
    def load_template(self):
        """
        Load the base HTML template.
        """
        try:
            with open(self.TMPLT_PATH, 'r', encoding='utf-8') as file:
                return file.read()
        
        except Exception:
            log_message(f"Error: template is not imported", self.logs, log_level="ERROR")
            raise ImportError

    def generate_section(self, block_name, news_items):
        """
        Generate HTML for a specific section with multiple news items.
        """
        formatted_block_name = self.config["sections"][block_name]
        section_html = (
            f"<h3 style='text-align: center;'>" +
                f"<span style='color:#13285b;'>{formatted_block_name}</span></h3><br/>"
            )
        for item in news_items:
            section_html += (
                f"<p style='text-align: justify;'><a href={item['link']} "+
                    f"target='_blank' style='color: #13285b; text-decoration: none;'>{item['summary']}</a></p><br/>"
            )
        section_html += "<p class='last-child'></p><br/>"
        return section_html

    def generate_html(self, rdct_data):
        """
        Generate the final HTML content.
        """
        template = self.load_template()
        html_configs = self.config["html_parts"]
        body_content = html_configs["body_init"]

        # Insert main content
        main = rdct_data["Main"]
        body_content += (
            f"<h2 style='text-align: left;'><span style='color:#13285b;'>"+
                f"<a href={main['link']} target='_blank' style='color: #13285b; text-decoration: none;'>"+
                f"<b>{main['summary']}</b></a></span></h2><br/><p style='text-align: left;' class='last-child'>"+
                f"<span style='color:#707070;'>{datetime.now().strftime('%B %d, %Y')} • Boletín #102</span></p>"
            )
        
        body_content += html_configs["body_news"]

        # Insert sections
        for idx, (block_name, news_items) in enumerate(rdct_data["sections"].items()):
            if idx == 0:
                # Action for the first iteration
                body_content += self.generate_section(block_name, news_items)
                body_content += html_configs["advertisement"]
            else:
                body_content += self.generate_section(block_name, news_items)

        body_content += html_configs["body_close"]

        # Combine template with dynamic content
        return (
            template.replace("{{HEADER}}", html_configs["header"])
            .replace("{{FOOTER}}", html_configs["footer"])
            .replace("{{BODY}}", body_content)
        )
    
    def save_Newsletter(self, content):
        """
        Save the Newsletter to the output directory.
        """
        output_file = path.join(self.NEWSLETTER_DIR, f"Newsletter_{datetime.now().strftime('%Y%m%d')}.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        log_message(f"Newsletter saved to: {output_file}", self.logs)

    def run_designer(self):
        """
        Main execution of the design process.
        """
        log_message("Loading last redacted data...", self.logs)
        data = self.load_data()

        log_message("Generating html file...", self.logs)
        formatted_html = self.generate_html(data)
      
        log_message("Saving Newsletter...", self.logs)
        self.save_Newsletter(formatted_html)

        log_message("Newsletter design complete.", self.logs)