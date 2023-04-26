import openai
import toml
import argparse
import os
import yaml

config = toml.load("config.toml")
openai.api_key = config["openai"]["api_key"]

class Conversation:
    def __init__(self, model='gpt-3.5-turbo', file=None):
        self.model = model
        self.file = file
        self.title = None
        self.total_tokens = 0
        self.messages = [{"role": "system", "content": config["openai"]["system_message"]}]
        
        if self.file:
            try:
                self.load()
            except Exception as e:
                print(f"Error loading conversation: {e}")

    def save(self):
        try:
            if not self.file:
                self.title = input("Title: ")
                self.file = self.title.replace(" ", "-") + ".yaml"

            file_path = os.path.join("conversations", self.file)
            if os.path.exists(file_path):
                overwrite = input("File already exists. Do you want to overwrite it? (y/n): ")
                if overwrite.lower() != "y":
                    new_filename = input("Please enter a new file name: ")
                    self.file = new_filename + ".yaml"
                    file_path = os.path.join("conversations", self.file)

            print(f"Saving conversation to {file_path}...")
            yaml_string = yaml.dump(self.__dict__)
            with open(file_path, "w") as f:
                f.write(yaml_string)
        except Exception as e:
            print(f"Error saving conversation: {e}")

    def load(self):
        # Load conversation data from the provided YAML file
        with open(self.file, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        # Update conversation attributes with the loaded data
        self.__dict__.update(data)

    def print(self):
        print(f"Model: {self.model}\n")
        for message in self.messages:
            text = message["content"]
            role = message["role"]
            if role == "system":
                print(f"[{text}]")
            elif role == "user":
                print(f">>> {text}")
            elif role == "assistant":
                print(f"{text}\n")

    def generate_text(self, prompt, role="user"):
        try:
            # Add the user prompt to the conversation messages
            self.messages.append({"role": role, "content": prompt})

            # Make an API call to OpenAI's chat model
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages
            )

            # Extract the generated text from the API response
            generated_text = response.choices[0].message["content"].strip()
            # Add the generated text to the conversation messages
            self.messages.append({"role": "assistant", "content": generated_text})
            # Update the total tokens used in the conversation
            self.total_tokens += response.usage.total_tokens

            return generated_text
        except Exception as e:
            print(f"Error generating text: {e}")
            return None

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
        conversation = Conversation(model=args.model)

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
