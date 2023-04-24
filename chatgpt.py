import openai
import toml
import argparse
#import sys

# Read API key from config.toml
config = toml.load("config.toml")
openai.api_key = config["openai"]["api_key"]

def generate_text(prompt, messages, model='gpt-3.5-turbo'):
    try:
        if not messages:
            messages.append({"role": "system", "content": "You are a helpful assistant."})

        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )

        generated_text = response.choices[0].message["content"].strip()
        messages.append({"role": "assistant", "content": generated_text})
        return generated_text
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def main():
    # Command line argument parser
    parser = argparse.ArgumentParser(description="GPT Model Selector")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    args = parser.parse_args()

    # Initialize an empty conversation
    messages = []

    while True:
        # Get user input
        prompt = input("User: ")

        # Exit the loop if the user enters 'quit'
        if prompt.lower() == "quit":
            break

        # Generate text
        generated_output = generate_text(prompt, messages, model=args.model)
        print(f"Assistant: {generated_output}")

if __name__ == "__main__":
    main()
