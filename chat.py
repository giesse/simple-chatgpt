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

def run(conversation):
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
