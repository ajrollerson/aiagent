import os
import argparse
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key == None:
    raise RuntimeError("API key not found")

client = genai.Client(api_key=api_key)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

def main():
    for _ in range(20):
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt)
            )
        for candidate in response.candidates: 
            messages.append(candidate.content)
        if args.verbose == True:
            if response.usage_metadata is None:
                raise RuntimeError("Failed API request")
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        if response.function_calls:
                function_response = []
                for call in response.function_calls:
                    result = call_function(call, args.verbose)
                    if not result.parts or result.parts[0].function_response is None or result.parts[0].function_response.response is None:
                        raise Exception("Function_call empty")
                    function_response.append(result.parts[0])
                    if args.verbose:
                        print(f"-> {result.parts[0].function_response.response}")
                messages.append(types.Content(role="user", parts=function_response))    
        else:
            if response.text is not None:
                print(response.text)
                break
    else:
        print("Maximum iterations reached without a final response")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
