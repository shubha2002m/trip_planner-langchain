
import sys
import io
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for stdout
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables from root .env (works from src/ or root)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from langchain_core.messages import AIMessage

def extract_ai_message(response):
    """Extract the final AI message content from the agent response"""
    if isinstance(response, dict) and 'messages' in response:
        # Get messages list and find the last AIMessage with content
        messages = response['messages']
        for message in reversed(messages):
            if isinstance(message, AIMessage) and message.content and message.content.strip():
                return message.content
    # Fallback for direct AIMessage response
    if isinstance(response, AIMessage):
        return response.content
    return str(response)

from trip_agents import city_selection_agent, local_expert_agent, travel_concierge_agent

def main():
    print("## Welcome to Trip Planner Crew")
    print('-------------------------------')
    origin = input("Where are you traveling from? ")
    cities = input("Enter city options (comma separated): ").split(",")
    date_range = input("Enter trip date range: ")
    interests = input("Enter your travel interests: ")

    # Step 1: City selection
    city_agent = city_selection_agent()
    city_response = city_agent.invoke({
        "messages": [{"role": "user", "content": f"Select the best city for a trip from {origin} to {cities} during {date_range} with interests: {interests}. If year isnt provided assume current year.  Make reasonable assumptions about dates and provide a clear recommendation without asking for clarification."}]
    })
    city_content = extract_ai_message(city_response)
    print("\nBest city selection:\n", city_content)

    # Step 2: Local expert guide - pass only the clean AI recommendation
    expert_agent = local_expert_agent()
    expert_response = expert_agent.invoke({
        "messages": [{"role": "user", "content": f"The city selection recommended: {city_content}\n\nBased on this recommendation, provide detailed local expert insights. Focus on attractions, customs, best neighborhoods, and tips for travelers with interests: {interests}. Give practical recommendations."}]
    })
    expert_content = extract_ai_message(expert_response)
    print("\nLocal expert guide:\n", expert_content)

    # Step 3: Travel concierge plan - pass cleaned up recommendations
    concierge_agent = travel_concierge_agent()
    concierge_response = concierge_agent.invoke({
        "messages": [{"role": "user", "content": f"Selected city: {city_content}\n\nLocal expert insights: {expert_content}\n\nCreate a detailed itinerary for this city during {date_range}. Include day-by-day activities, accommodation recommendations, budget breakdown, packing list, and dining suggestions for travelers with interests: {interests}. Create an itinerary that matches the exact dates provided, not a fixed 7 days."}]
    })
    concierge_content = extract_ai_message(concierge_response)
    print("\nTravel plan:\n", concierge_content)

if __name__ == "__main__":
    main()
