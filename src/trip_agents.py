


# --- New LangChain Agent API ---
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
import os

# --- Standalone tool functions ---
import json
import os
import requests
import re
import ast
import operator
from unstructured.partition.html import partition_html

@tool("search_internet")
def search_internet(query: str) -> str:
        """Useful to search the internet about a given topic and return relevant results"""
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
                'X-API-KEY': os.environ['SERPER_API_KEY'],
                'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if 'organic' not in response.json():
                return "Sorry, I couldn't find anything about that, there could be an error with your serper api key."
        else:
                results = response.json()['organic']
                string = []
                for result in results[:top_result_to_return]:
                        try:
                                string.append('\n'.join([
                                        f"Title: {result['title']}", f"Link: {result['link']}",
                                        f"Snippet: {result['snippet']}", "\n-----------------"
                                ]))
                        except KeyError:
                                continue
                return '\n'.join(string)

@tool("scrape_website_content")
def scrape_and_summarize_website(website: str) -> str:
        """Scrape and summarize a website's main content using Browserless /scrape endpoint."""
        # Target common content selectors for general-purpose summarization
        selectors = ["h1", "h2", "h3", "p", "article", "main", "section"]
        url = f"https://chrome.browserless.io/scrape?token={os.environ['BROWSERLESS_API_KEY']}"
        payload = json.dumps({
                "url": website,
                "elements": [{"selector": sel} for sel in selectors]
        })
        headers = {'content-type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)
        try:
                data = response.json()
                results = []
                for el in data.get("data", []):
                        selector = el.get("selector", "")
                        for res in el.get("results", []):
                                text = res.get("text")
                                if text:
                                        results.append(f"[{selector}] {text}")
                if not results:
                        return "No content found with common selectors."
                return "\n".join(results)
        except Exception as e:
                return f"Scraping error: {str(e)}"

@tool("calculate")
def calculate(operation: str) -> str:
        """Useful to perform any mathematical calculations, like sum, minus, multiplication, division, etc."""
        try:
                allowed_operators = {
                        ast.Add: operator.add,
                        ast.Sub: operator.sub,
                        ast.Mult: operator.mul,
                        ast.Div: operator.truediv,
                        ast.Pow: operator.pow,
                        ast.Mod: operator.mod,
                        ast.USub: operator.neg,
                        ast.UAdd: operator.pos,
                }
                if not re.match(r'^[0-9+\-*/().% ]+$', operation):
                        return "Error: Invalid characters in mathematical expression"
                tree = ast.parse(operation, mode='eval')
                def _eval_node(node):
                        if isinstance(node, ast.Expression):
                                return _eval_node(node.body)
                        elif isinstance(node, ast.Constant):
                                return node.value
                        elif isinstance(node, ast.Num):
                                return node.n
                        elif isinstance(node, ast.BinOp):
                                left = _eval_node(node.left)
                                right = _eval_node(node.right)
                                op = allowed_operators.get(type(node.op))
                                if op is None:
                                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                                return op(left, right)
                        elif isinstance(node, ast.UnaryOp):
                                operand = _eval_node(node.operand)
                                op = allowed_operators.get(type(node.op))
                                if op is None:
                                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                                return op(operand)
                        else:
                                raise ValueError(f"Unsupported node type: {type(node).__name__}")
                result = _eval_node(tree)
                return str(result)
        except Exception as e:
                return f"Calculation error: {str(e)}"


# --- Gemini 3.1 Pro Preview LLM ---
if "GOOGLE_API_KEY" not in os.environ:
        raise RuntimeError("GOOGLE_API_KEY must be set in your environment or .env file.")
llm = init_chat_model("google_genai:gemini-2.5-flash-lite")

# --- Agent creation functions ---
def city_selection_agent():
        return create_agent(
                model=llm,
                tools=[search_internet, scrape_and_summarize_website],
                system_prompt="You are a City Selection Expert. Select the best city based on weather, season, and prices. You are an expert in analyzing travel data to pick ideal destinations. If the year is not specified in the date range, assume the current year 2026. If only months are given, assume travel during that month. Make reasonable assumptions about dates and provide a clear recommendation without asking for clarification."
        )

def local_expert_agent():
        return create_agent(
                model=llm,
                tools=[search_internet, scrape_and_summarize_website],
                system_prompt="You are a Local Expert at this city. Provide the BEST insights about the selected city. You are a knowledgeable local guide with extensive information about the city, its attractions and customs. If dates are unclear or incomplete, make reasonable assumptions (e.g., assume current year) and provide insights without asking for clarification. Focus on practical recommendations."
        )

def travel_concierge_agent():
        return create_agent(
                model=llm,
                tools=[search_internet, scrape_and_summarize_website, calculate],
                system_prompt="You are an Amazing Travel Concierge. Create the most amazing travel itineraries with budget and packing suggestions for the city. You are a specialist in travel planning and logistics with decades of experience. If dates are unclear or incomplete, make reasonable assumptions (e.g., assume current year ) and provide a complete itinerary without asking for clarification. Always provide actionable recommendations."
        )
