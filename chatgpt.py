import openai
import toml
import argparse
import sys

# Read API key from config.toml
config = toml.load("config.toml")
openai.api_key = config["openai"]["api_key"]

def generate_text(prompt, model='gpt-3.5-turbo'):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def main():
    # Command line argument parser
    parser = argparse.ArgumentParser(description="GPT Model Selector")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    args = parser.parse_args()

    # Get user input
    prompt = input("Enter your prompt: ")

    # Generate text
    generated_output = generate_text(prompt, model=args.model)
    print(f"Generated text: {generated_output}")

if __name__ == "__main__":
    main()
