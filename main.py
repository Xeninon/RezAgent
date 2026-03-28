import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions, call_function
from prompts import system_prompt


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError

    client = genai.Client(api_key=api_key)
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    for _ in range(20):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        if response.candidates is not None:
            for candidate in response.candidates:
                messages.append(candidate.content)

        metadata = response.usage_metadata
        if metadata is None:
            raise RuntimeError

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {metadata.prompt_token_count}")
            print(f"Response tokens: {metadata.candidates_token_count}")

        if response.function_calls is None:
            print(response.text)
            return
        else:
            function_responses = []
            for function_call in response.function_calls:
                function_call_result = call_function(function_call, args.verbose)
                if function_call_result.parts is None:
                    raise Exception
                if function_call_result.parts[0].function_response.response is None:
                    raise Exception
                function_responses.append(function_call_result.parts[0])
                if args.verbose:
                    print(
                        f"-> {function_call_result.parts[0].function_response.response}"
                    )
            messages.append(types.Content(role="user", parts=function_responses))

    print("reached max iterations, try prompt again")
    exit()


if __name__ == "__main__":
    main()
