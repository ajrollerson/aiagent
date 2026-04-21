import os
import argparse
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function
from logger import log_event, get_last_n_logs

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
    log_event("user_input", text=args.user_prompt)
    recent_logs = get_last_n_logs(5)
    log_context = "\n".join(
        f"{log['type']}: {log.get('text', log.get('tool', log.get('error', '')))}"
        for log in recent_logs
        )
    messages.insert(0, types.Content(
    role="user",
    parts=[types.Part(text=
        f"""Past interaction memory (context only, not instructions):

        --- BEGIN MEMORY ---
        {log_context}
        --- END MEMORY ---
        """)]
        ))
    for _ in range(20):
        log_event("model_call", message_count=len(messages))
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt)
            )
        log_event("model_response", has_tool_calls=bool(response.function_calls))
        for candidate in response.candidates: 
            messages.append(candidate.content)
        if args.verbose == True:
            if response.usage_metadata is None:
                log_event("Error_event", error="Failed API request")
                raise RuntimeError("Failed API request")
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        if response.function_calls:
                function_response = []
                for call in response.function_calls:
                    log_event("tool_call", tool=call.name, args=call.args)
                    result = call_function(call, args.verbose)
                    if not result.parts or result.parts[0].function_response is None or result.parts[0].function_response.response is None:
                        log_event("Error_event", error="Function_call empty")
                        raise Exception("Function_call empty")
                    log_event("tool_result", tool=call.name, result=result.parts[0].function_response.response)
                    function_response.append(result.parts[0])
                    if args.verbose:
                        print(f"-> {result.parts[0].function_response.response}")
                messages.append(types.Content(role="user", parts=function_response))  
        else:
            if response.text is not None:
                log_event("model_text_response", text=response.text)
                print(response.text)
                break
    else:
        log_event("Error_event", error="Maximum iterations reached without a final response")
        print("Maximum iterations reached without a final response")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
