
# LLM with Tools Example using Ollama and OpenAI Python SDK
###
# 1. mistral:latest wasn't properly supporting function calling
# USE functions and function_call instead of tools and tool_choice
# 




from openai import OpenAI
from pprint import pprint

client = OpenAI(
    api_key="ollama",  # required by the library, but ignored by Ollama
    base_url="http://localhost:11434/v1"
)

def get_current_weather(city: str, unit:str = "celsius") -> str:    
    # dummy weather data
    temperature = 25
    condition = "sunny"
    unit_symbol = "°C" if unit.lower() == "celsius" else "°F"
    return f"It is {temperature}{unit_symbol} and {condition} in {city}."


SYSTEM_PROMPT = """
You are a helpful weather assistant.

You have access to the following tool:

Tool Name: get_current_weather
Description: Returns a short human-readable sentence describing the current weather for a given city.
Function Signature:
    get_current_weather(city: str, unit: str = "celsius") -> str

Instructions:
- When the user asks about the weather in a city, call get_current_weather with the appropriate parameters.
- If the user asks something else, just respond normally.
"""

USER_QUESTION = "What's the weather like in San Francisco today?"

available_tools =  [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Returns a short human-readable sentence describing the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get weather for"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius",
                        "description": "Temperature unit"
                    }
                },
                "required": ["city"]
            }
        }
    }
]


# First, let's try to get the model to call the function
response = client.chat.completions.create(
    #model="llama3.2:latest",
    model="llama3.2:latest",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_QUESTION}
    ],
    tools=available_tools,
    tool_choice="auto"
)

print("=== Initial Response ===")
pprint(response)

# Check if the model made a tool call
message = response.choices[0].message
print(f"\n=== Message Content ===")
print(f"Content: {message.content}")
print(f"Tool calls: {message.tool_calls}")
print(f"Prompt Tokens: {response.usage.prompt_tokens}, Completion Tokens: {response.usage.completion_tokens}, Total Tokens: {response.usage.total_tokens}")

# If the model made a tool call, execute the function
if message.tool_calls:
    print("\n=== Executing Tool Call ===")
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        function_args = tool_call.function.arguments
        
        print(f"Function: {function_name}")
        print(f"Arguments: {function_args}")
    