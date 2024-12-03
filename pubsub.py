import requests
from bs4 import BeautifulSoup
import re
from anthropic import Anthropic
import os
from typing import List, Tuple, Dict

class StockAnalyzer:
    def __init__(self, api_key: str):
        self.anthropic = Anthropic(api_key=api_key)
        
    def scrape_website(self, url: str) -> str:
        """
        Scrapes text content from a given URL
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise Exception(f"Failed to scrape website: {str(e)}")

    def extract_tickers(self, text: str) -> Dict:
        """
        Uses Claude to extract stock tickers and generate a summary
        """
        prompt = f"""
        Analyze the following text and:
        1. Extract all stock tickers mentioned (e.g., AAPL, GOOGL, etc.)
        3. Return your response in this exact format (don't forget the brackets []):
        TICKERS: [list all tickers separated by commas]

        Text to analyze:
        {text}
        """

        print("Extracting tickers")

        response = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        response_text = response.content[0].text

        print("Response text:", response_text)

        tickers_match = re.search(r'TICKERS: \[(.*?)\]', response_text)
        # summary_match = re.search(r'SUMMARY: (.*)', response_text, re.DOTALL)
        
        tickers = [ticker.strip() for ticker in tickers_match.group(1).split(',')] if tickers_match else []
        # summary = summary_match.group(1).strip() if summary_match else "No summary available"
        
        print("Tickers extracted:", tickers)

        return {
            "tickers": tickers,
            # "summary": summary
        }

    def summarize_ticker(self, text: str, ticker: str) -> Dict:
        """
        Uses Claude to extract stock tickers and generate a summary
        """
        prompt = f"""
        Analyze the following text and:
        1. Provide a brief summary of the main points related to stock ticker {ticker}. The summary should be written for a professional investment analyst.
        2. Return your response in this exact format:
        SUMMARY: [your summary]

        Text to analyze:
        {text}
        """

        print("Summarizing ticker:", ticker)

        response = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        response_text = response.content[0].text

        print("summarized ticker response text:", response_text)

        # tickers_match = re.search(r'TICKERS: (.*?)\n', response_text)
        summary_match = re.search(r'SUMMARY: (.*)', response_text, re.DOTALL)
        
        # tickers = [ticker.strip() for ticker in tickers_match.group(1).split(',')] if tickers_match else []
        summary = summary_match.group(1).strip() if summary_match else "No summary available"
        
        return {
            # "tickers": tickers,
            "summary": summary
        }

    def analyze_url(self, url: str) -> Dict:
        """
        Main function to analyze a URL for stock tickers and content
        """
        text = self.scrape_website(url)

        print("Website text:", text)

        tickers = self.extract_tickers(text)

        print('tickers in analyze_url:', tickers)

        summary = self.summarize_ticker(text, tickers['tickers'][0])

        print('got first ticker summary lfg')

        return {
            "tickers": tickers,
            "summary": summary
        }

def main():
    # Replace with your API key
    api_key = "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"
    analyzer = StockAnalyzer(api_key)
    
    # Example usage
    url = "https://toffcap.substack.com/p/toffcaps-monday-monitor-37"
    try:
        results = analyzer.analyze_url(url)
        print("about to print results...")

        print("Found Tickers:", results["tickers"])
        print("\nSummary:", results["summary"])
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()