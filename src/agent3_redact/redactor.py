from os import path, listdir
from json import load, dump
from datetime import datetime
from src.agent3_redact.config import load_config
from src.common.logs import log_message
from src.common.path import get_full_path
from transformers import pipeline, BartTokenizer

class NewsRedactor:
    def __init__(self, log_path=None):
        self.config = load_config()
        self.PRCS_DATA_DIR = get_full_path(self.config["paths"]["input"])
        self.RDCT_DATA_DIR = get_full_path(self.config["paths"]["output"])

        if log_path:
            self.logs = log_path
        else:
            self.logs = self.config["logs"]
        try:
            # Load the summarizing model
            summary_model = self.config["summarization_model"]
            log_message(f"Loading Model {summary_model}...", self.logs)
            self.summarizer = pipeline("summarization", model=summary_model, tokenizer=summary_model, device="cuda")
            self.tokenizer = BartTokenizer.from_pretrained(summary_model)
            log_message(f"Model {summary_model} loaded!", self.logs)

            # Load the translate model
            translator_model = self.config["translator_model"]
            log_message(f"Loading Model {translator_model}...", self.logs)
            self.translator = pipeline("translation_en_to_es", model=translator_model, device="cuda")
            log_message(f"Model {translator_model} loaded!", self.logs)

        except OSError as e:
            log_message(f"Error: Could not load model or tokenizer: {e}", self.logs, log_level="ERROR")
        except Exception as e:
            log_message(f"Error: An unexpected error occurred: {e}", self.logs, log_level="ERROR")

    def load_data(self):
        """
        Load processed data in JSON format.
        """
        files = [f for f in listdir(self.PRCS_DATA_DIR) if f.endswith(".json")]
        if not files:
            log_message(f"Error: No processed data files found in {self.PRCS_DATA_DIR}", self.logs, log_level="ERROR")
            raise FileNotFoundError("No processed data files found in the processed data directory.")
        
        # Load the latest file by modification date
        latest_file = max(files)
        with open(path.join(self.PRCS_DATA_DIR, latest_file), "r", encoding="utf-8") as f:
            return load(f)
            
    def generate_summary(self, text, limit, max_tokens=1024, min_tokens=20):
        """
        Generate a summary for large text by dividing it into manageable chunks.
        """
        # Tokenize and chunk the text into segments of max_tokens
        inputs = self.tokenizer(text, return_tensors="pt", truncation=False)
        input_ids = inputs["input_ids"][0]
        chunk_size = max_tokens - limit - 10
        chunks = [input_ids[i:i+chunk_size] for i in range(0, len(input_ids), chunk_size)]

        summaries = []
        for chunk in chunks:
            # Decode chunk back to text for summarization
            chunk_text = self.tokenizer.decode(chunk, skip_special_tokens=True)
            summary = self.summarizer(chunk_text,
                                      max_length=limit,
                                      min_length=min_tokens,
                                      do_sample=False)[0]["summary_text"]
            summaries.append(summary)

        if len(summaries) == 1:
            return summaries[0]

        # Combine all summaries into a final summary
        combined_text = ". ".join(summaries)
        final_summary = self.summarizer(combined_text, 
                                        max_length=limit, 
                                        min_length=min_tokens,
                                        do_sample=False)[0]["summary_text"]

        return final_summary

    def translate_summary(self, text, min_tokens=20):
        """
        Translate the summary using a pre-trained translation model.
        """
        # Parameterize the LLM (e.g., max tokens)
        translation = self.translator(text, min_length=min_tokens, do_sample=False)[0]['translation_text']

        return translation
    
    def format_news(self, news, parameters=100):
        """
        Format the main new of the Newsletter.
        """
        # Generate a summary and key concept using the LLM library
        content = news.get("content", "")
        summary = self.generate_summary(content, parameters)
        if news.get("en", "en") == "en":
            summary = self.translate_summary(summary)

        return {
            "summary": summary,
            "key_concept": "", 
            "link": news.get("link", "")
            }
    
    def redact_newsletter(self, data):
        """
        Redact the entire newsletter content from the categorized data.
        """
        # Organize the information
        categorized_news = data["sections"]
        principal_dict = {}
        redacted_blocks = {}

        # Redact the main new
        log_message(f"Processing main new", self.logs)
        principal_dict["Main"] = self.format_news(data["Main"], parameters=30)
        
        # Redact the news
        for block_name, news_list in categorized_news.items():
            log_message(f"Processing block: {block_name}", self.logs)
            formatted_news = []
            for news in news_list:
                formatted_news.append(self.format_news(news))
            redacted_blocks[block_name] = formatted_news

        principal_dict["sections"] = redacted_blocks

        return principal_dict

    def save_newsletter(self, content):
        """
        Save the formatted newsletter to the output directory.
        """
        output_file = path.join(self.RDCT_DATA_DIR, f"redacted_news_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            dump(content, f, ensure_ascii=False, indent=4)

        log_message(f"Redacted news saved to: {output_file}", self.logs)

    def run_redactor(self):
        """
        Main execution of the redaction process.
        """
        log_message("Loading last processed data...", self.logs)
        data = self.load_data()

        log_message("Redacting news...", self.logs)
        newsletter_content = self.redact_newsletter(data)

        log_message("Saving redacted news...", self.logs)
        self.save_newsletter(newsletter_content)

        log_message("Newsletter redaction complete.", self.logs)