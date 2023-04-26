from conversation import Conversation

def get_input() -> str:
    """Gets user input from the console, handling the /multiline command.
    
    Returns:
        str: The user input as text.
    """
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
    """A class representing a usable command.
    
    Attributes:
        call (callable): The function that the command executes.
        help_text (str): The description of what the command does.
    """
    def __init__(self, func, help_text):
        self.call = func
        self.help_text = help_text

def define_command(name: str, func: callable, help_text: str) -> None:
    """Defines a new command to be used in the console.
    
    Args:
        name (str): The name of the command (with the '/' prefix).
        func (callable): The function that the command executes.
        help_text (str): The description of what the command does.
    
    Returns:
        None
    """
    commands[name] = Command(func, help_text)

def print_help(cmd: str = None) -> str:
    """Generates help text for the console, listing all available commands or giving
    help text for a specific command if supplied.
    
    Args:
        cmd (Optional[str]): The name of the command to show help text for, with or without
        the '/' prefix. Default is None, which shows help text for all commands.
    
    Returns:
        str: The help text for the specified command(s).
    """
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

def run(conversation: Conversation) -> None:
    """Runs the console loop to receive input from the user and generate responses using
    OpenAI's API. Handles defined commands and saves the conversation to a file on /quit.
    
    Args:
        conversation (Conversation): The Conversation object to use for generating responses.
    
    Returns:
        None
    """
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
