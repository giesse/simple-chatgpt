import openai
import toml
import argparse
from conversation import Conversation

config = toml.load("config.toml")
openai.api_key = config["openai"]["api_key"]

def get_input():
    try:
        text = input(">>> ")
        if text.lower().startswith("/multiline"):
            text = input("[end with .]\n")
            while True:
                line = input()
                if line == ".":
                    break
                text += "\n" + line
            print("[end]")
        return text
    except KeyboardInterrupt:
        # Allow user to exit gracefully with Ctrl+C
        return "/quit"
    except Exception as e:
        print(f"Error getting input: {e}")
        return ""

commands = {}

class Command:
    def __init__(self, func, help_text):
        self.call = func
        self.help_text = help_text

def define_command(name, func, help_text):
    commands[name] = Command(func, help_text)

def print_help(cmd=None):
    help_text = None
    if cmd:
        if not cmd.startswith("/"):
            cmd = "/" + cmd
        if cmd in commands:
            help_text = commands[cmd].help_text
    if not help_text:
        help_text = "Available commands:\n/multiline - starts multiline input\n/quit - save the conversation and exit"
        for cmd in commands:
            help_text += "\n" + cmd + " - " + commands[cmd].help_text
    return help_text

define_command("/help", print_help, "Prints the text you are currently looking at")
        
def main():
    parser = argparse.ArgumentParser(description="Simple ChatGPT")
    parser.add_argument("-c", "--conversation", help="Conversation file (to resume a previous conversation)")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    args = parser.parse_args()

    # Initialize a Conversation object, either by loading an existing conversation from a file or creating a new one
    if args.conversation:
        conversation = Conversation(file=args.conversation)
    else:
        conversation = Conversation(model=args.model, system_message=config["openai"]["system_message"])

    print("Welcome to Simple ChatGPT!\nType /multiline to enter multiple lines of input. /quit to quit and save conversation.\nType /help for more commands.")

    # Print the conversation so far
    conversation.print()

    while True:
        # Get user input (handles /multiline command)
        prompt = get_input()

        # Exit the loop and save the conversation if the user enters 'quit'
        if prompt.lower() == "/quit":
            conversation.save()
            break
        if prompt.startswith("/"):
            tokens = prompt.split()
            cmd = tokens[0]
            args = tokens[1:]
            if cmd in commands:
                generated_output = commands[cmd].call(*args)
            else:
                generated_output = f"Unknown command {cmd}"
        else:
            # Generate text using OpenAI's API
            generated_output = conversation.generate_text(prompt)

        # Display the generated text
        print(f"{generated_output}\n")

if __name__ == "__main__":
    main()
