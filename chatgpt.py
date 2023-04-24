import openai
import toml
import argparse
import copy
import os
import yaml

# Read API key from config.toml
config = toml.load("config.toml")
openai.api_key = config["openai"]["api_key"]

def init_conversation(model='gpt-3.5-turbo'):
    return {
            "model": model,
            "messages": [{"role": "system", "content": config["openai"]["system_message"]}],
            "file": None,
            "title": None,
            "total_tokens": 0
            }

def save_conversation(conversation):
    if not conversation["file"]:
        conversation["title"] = input("Title: ")
        conversation["file"] = conversation["title"].replace(" ", "-") + ".yaml"

    file_path = os.path.join("conversations", conversation["file"])
    print(f"Saving conversation to {file_path}...")
    yaml_string = yaml.dump(conversation)
    with open(file_path, "w") as f:
        f.write(yaml_string)

def load_conversation(file):
    with open(file, "r") as f:
        conversation = yaml.load(f, Loader=yaml.FullLoader)

    return conversation

def generate_text(conversation, prompt):
    try:
        conversation["messages"].append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=conversation["model"],
            messages=conversation["messages"]
        )

        generated_text = response.choices[0].message["content"].strip()
        conversation["messages"].append({"role": "assistant", "content": generated_text})
        conversation["total_tokens"] += response.usage.total_tokens
        return generated_text
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def main():
    # Command line argument parser
    parser = argparse.ArgumentParser(description="Simple ChatGPT")
    parser.add_argument("-c", "--conversation", help="Conversation file (to resume a previous conversation)")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    args = parser.parse_args()

    if args.conversation:
        conversation = load_conversation(args.conversation)
    else:
        conversation = init_conversation(args.model)

    while True:
        # Get user input
        prompt = input(">>> ")

        # Exit the loop if the user enters 'quit'
        if prompt.lower() == "quit":
            save_conversation(conversation)
            break

        # Generate text
        generated_output = generate_text(conversation, prompt)
        print(f"{generated_output}\n\n")

if __name__ == "__main__":
    main()
