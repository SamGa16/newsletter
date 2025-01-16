from json import load, dump
from os import path, listdir
from datetime import datetime
from re import sub
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from langdetect import detect as lang_detector
from src.agent2_select.config import load_config
from src.common.logs import log_message
from src.common.path import get_full_path

class NewsSelector:
    def __init__(self, log_path=None):
        self.config = load_config()
        self.RAW_DATA_DIR = get_full_path(self.config["paths"]["input"])
        self.PRCS_DATA_DIR = get_full_path(self.config["paths"]["output"])

        if log_path:
            self.logs = log_path
        else:
            self.logs = self.config["logs"]

    def load_scraped_data(self):
        """
        Load the most recent scraped news data from the raw data folder.
        """
        files = [f for f in listdir(self.RAW_DATA_DIR) if f.endswith(".json")]
        if not files:
            log_message(f"Error: No scraped data files found in {self.RAW_DATA_DIR}", self.logs, log_level="ERROR")
            raise FileNotFoundError("No scraped data files found in the raw data directory.")
        
        # Load the latest file by date
        latest_file = max(files)
        with open(path.join(self.RAW_DATA_DIR, latest_file), "r", encoding="utf-8") as f:
            return load(f)
        
    def clean_news(self, news_data):
        """
        Clean news for legibility by removing duplicates and unrelated prefixes/suffixes.
        """
        # Remove duplicates
        seen = set()
        unique_data = []
        for new in news_data:
            dict_tuple = tuple(sorted(new.items()))
            if dict_tuple not in seen:
                seen.add(dict_tuple)
                unique_data.append(new)

        # Add specific patterns that match to remove
        patterns = self.config["patterns_to_remove"]
        for news in unique_data:
            for pattern in patterns:
                news["content"] = sub(pattern, "", news["content"]).strip()
        log_message(f"Found {len(unique_data)} news to categorize!", self.logs)
        return unique_data
    
    def language_detection(self, text):
        """
        Detect the language using langdetect.
        """
        language = lang_detector(text)
        if language == 'es':

            return language
        return 'en'

    def tokenize_text(self, text, language_parameters):
        """
        Compute score of matching to category based on keywords.
        """
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = sub(language_parameters["characters"], '', text)

        # Tokenize
        language = language_parameters["stopwords"]
        tokens = word_tokenize(text, language=language)
        
        # Remove stopwords
        stop_words = set(stopwords.words(language))
        tokens = [word for word in tokens if word not in stop_words]
    
        return tokens
    
    def calculate_score(self, tokens, content_blocks):
        """
        Compute score of matching to category based on keywords.
        """
        # Calculate scores for each category
        scores = {}
        for category, keywords in content_blocks.items():
            match_count = sum(1 for token in tokens if token in keywords)
            if keywords:
                scores[category] = round((match_count / len(keywords)) * 200, 2)
            else:
                scores[category] = 0

        # Find the best category based on the highest score
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        return best_category, best_score

    def categorize_news(self, cleaned_data):
        """
        Categorize news into content blocks based on keywords and ECHO detection.
        """

        # Initialize the result dictionary
        principal_dict = {}
        categories = self.config["languages"]["en"]["content_blocks"]
        categorized_news = {category: [] for category in categories}
        principal_dict['Main'] = []
        principal_dict['Uncategorized'] = []
        score_threshold = self.config["score_threshold"]
        highest_score = 0

        for news in cleaned_data:
            # Detect language
            language = self.language_detection(news.get('content', ''))
            language_parameters =self.config["languages"][language]

            # Tokenize and combine
            title_tokens = self.tokenize_text(news.get('title', ''), language_parameters)
            content_tokens = self.tokenize_text(news.get('content', ''), language_parameters)
            all_tokens = set(title_tokens + content_tokens)

            # Calculate the best category and score
            best_category, score = self.calculate_score(all_tokens, categories)

            # Add the score and language to the news item
            news['languages'] = language
            news['score'] = score

            # Get the main new for the Newsletter
            if score > highest_score:
                principal_dict['Main'] = news
                highest_score = score

            # Categorize the news if the score exceeds the threshold
            if score >= score_threshold:
                categorized_news[best_category].append(news)
            else:
                principal_dict['Uncategorized'].append(news)

        # Append categories to the main dict
        principal_dict["sections"] = categorized_news

        return principal_dict

    def select_top_news(self, categorized_news):
        """
        Select the top news items for each block based on score.
        """
        max_news_per_block = self.config["max_news_per_block"]
        
        # Sort each category by score in descending order
        for category in categorized_news["sections"]:
            categorized_news["sections"][category].sort(key=lambda x: x['score'], reverse=True)
            categorized_news["sections"][category] = categorized_news["sections"][category][:max_news_per_block]
            log_message(f"Category '{category}' has {len(categorized_news['sections'][category])} news items selected.", 
                    self.logs)
            
        return categorized_news

    def save_selected_news(self, final_selection):
        """
        Save the selected news into a processed JSON file.
        """
        # Save the scraped news to a JSON file
        output_file = path.join(self.PRCS_DATA_DIR, f"selected_news_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            dump(final_selection, f, ensure_ascii=False, indent=4)

        log_message(f"Selected news saved to {output_file}", self.logs)

    def run_selector(self):
        """
        Main method to load, categorize, and select news.
        """
        log_message("Loading scraped data...", self.logs)
        scraped_data = self.load_scraped_data()

        log_message("Cleaning scraped data...", self.logs)
        cleaned_news = self.clean_news(scraped_data)

        log_message("Categorizing news...", self.logs)
        categorized_news = self.categorize_news(cleaned_news)

        log_message("Selecting top news...", self.logs)
        final_selection = self.select_top_news(categorized_news)

        log_message("Saving selected news...", self.logs)
        self.save_selected_news(final_selection)

        log_message("Newsletter selection complete.", self.logs)