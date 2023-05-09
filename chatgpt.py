import openai
import toml
import argparse
from conversation import Conversation
import chat

def main():
    parser = argparse.ArgumentParser(description="Simple ChatGPT")
    parser.add_argument("-c", "--conversation", help="Conversation file (to resume a previous conversation)")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    parser.add_argument("-C", "--config", default="config.toml", help="Configuration file name")
    args = parser.parse_args()

    config = toml.load(args.config)
    openai.api_key = config["openai"]["api_key"]

    # Initialize a Conversation object, either by loading an existing conversation from a file or creating a new one
    if args.conversation:
        conversation = Conversation(file=args.conversation)
    else:
        conversation = Conversation(model=args.model, system_message=config["openai"]["system_message"])

    print("Welcome to Simple ChatGPT!\nType /multiline to enter multiple lines of input. /quit to quit and save conversation.\nType /help for more commands.")

    # Print the conversation so far
    conversation.print()

    chat.run(conversation)

if __name__ == "__main__":
    main()
