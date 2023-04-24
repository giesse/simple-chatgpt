import openai
import toml
import argparse
import copy
import os
import yaml

# Load the OpenAI API key from the config file
config = toml.load("config.toml")
openai.api_key = config["openai"]["api_key"]

# Initialize a conversation and return it
def init_conversation(model='gpt-3.5-turbo'):
    return {
            "model": model,
            "messages": [{"role": "system", "content": config["openai"]["system_message"]}],
            "file": None,
            "title": None,
            "total_tokens": 0
            }

# Save the conversation to a file
def save_conversation(conversation):
    # If the file name isn't set, ask for it and set it
    if not conversation["file"]:
        conversation["title"] = input("Title: ")
        conversation["file"] = conversation["title"].replace(" ", "-") + ".yaml"

    # Write the conversation to a file
    file_path = os.path.join("conversations", conversation["file"])
    print(f"Saving conversation to {file_path}...")
    yaml_string = yaml.dump(conversation)
    with open(file_path, "w") as f:
        f.write(yaml_string)

# Load a conversation from a file
def load_conversation(file):
    with open(file, "r") as f:
        conversation = yaml.load(f, Loader=yaml.FullLoader)

    return conversation

# Print the conversation
def print_conversation(conversation):
    for message in conversation["messages"]:
        text = message["content"]
        role = message["role"]
        if role == "system":
            print(f"[{text}]")
        elif role == "user":
            print(f">>> {text}")
        elif role == "assistant":
            print(f"{text}\n\n")

# Generate text using OpenAI's API
def generate_text(conversation, prompt, role="user"):
    try:
        # Add the prompt to the conversation messages
        conversation["messages"].append({"role": role, "content": prompt})

        # Make an API call to OpenAI's chat model
        response = openai.ChatCompletion.create(
            model=conversation["model"],
            messages=conversation["messages"]
        )

        # Get the generated text from the API response
        generated_text = response.choices[0].message["content"].strip()

        # Add the generated text to the conversation messages
        conversation["messages"].append({"role": "assistant", "content": generated_text})

        # Record the number of tokens used for the API call
        conversation["total_tokens"] += response.usage.total_tokens

        return generated_text
    except Exception as e:
        # Handle errors that occur while generating text
        print(f"Error generating text: {e}")
        return None

# Get user input (either multiline or single line)
def get_input(multiline):
    if multiline:
        # Let the user input multiple lines (ended by a line with '.')
        result = input(">>> [end with .]\n")
        while True:
            line = input()
            if line == ".":
                break
            result += "\n" + line
        return result
    else:
        # Let the user input a single line
        return input(">>> ")

# Main function to run the conversation
def main():
    # Command line argument parser
    parser = argparse.ArgumentParser(description="Simple ChatGPT")
    parser.add_argument("-c", "--conversation", help="Conversation file (to resume a previous conversation)")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    args = parser.parse_args()

    # Load the conversation from a file if given, otherwise initialize a new one
    if args.conversation:
        conversation = load_conversation(args.conversation)
    else:
        conversation = init_conversation(args.model)

    # Print the conversation so far
    print_conversation(conversation)

    while True:
        # Get user input
        prompt = get_input(config["openai"]["multiline"])

        # Exit the loop if the user enters 'quit'
        if prompt.lower() == "quit":
            save_conversation(conversation)
            break

        # Generate text using OpenAI's API
        generated_output = generate_text(conversation, prompt)

        # Display the generated text
        print(f"{generated_output}\n\n")

if __name__ == "__main__":
    main()
