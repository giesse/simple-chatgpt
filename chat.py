from conversation import Conversation
import sys
from googlesearch import search

def get_input() -> str:
    """Gets user input from the console, handling the /multiline command.
    
    Returns:
        str: The user input as text.
    """
    try:
        text = input("User: ")
        if text.lower().startswith("/multiline"):
            print("[end with .]")
            lines = iter(input, ".")
            text = "\n".join(list(lines))
        print("")
        return text
    except KeyboardInterrupt:
        # Allow user to exit gracefully with Ctrl+C
        return "/quit"
    except Exception as e:
        print(f"Error getting input: {e}")
        return ""

user_commands = {}
ai_commands = {}

class Command:
    """A class representing a usable command.
    
    Attributes:
        call (callable): The function that the command executes.
        help_text (str): The description of what the command does.
    """
    def __init__(self, func, help_text):
        self.call = func
        self.help_text = help_text

def define_user_command(name: str, func: callable, help_text: str) -> None:
    """Defines a new command to be used in the console.
    
    Args:
        name (str): The name of the command (with the '/' prefix).
        func (callable): The function that the command executes.
        help_text (str): The description of what the command does.
    
    Returns:
        None
    """
    user_commands[name] = Command(func, help_text)

def define_ai_command(name: str, func: callable, help_text: str) -> None:
    """Defines a new command to be used by the AI.
    
    Args:
        name (str): The name of the command (with the '/' prefix).
        func (callable): The function that the command executes.
        help_text (str): The description of what the command does.
    
    Returns:
        None
    """
    ai_commands[name] = Command(func, help_text)

def print_help(cmd: str = None):
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
        if cmd in user_commands:
            help_text = user_commands[cmd].help_text
    if help_text:
        yield help_text
    else:
        yield "Available commands:\n/multiline - starts multiline input\n/quit - save the conversation and exit"
        for cmd in user_commands:
            yield f"\n{cmd} {user_commands[cmd].help_text}"

def google_search(query: str) -> str:
    results = search(query, num_results=10, advanced=True)
    text = ""
    for result in results:
        text += f"{result.title}\n{result.description}\n{result.url}\n\n"
    return text

def ai_help():
    help_text = "You can use the following commands to execute actions. A command is only accepted if your response starts with '/'. You cannot execute commands in the middle of other text. You can only execute one command at a time.\n"
    for cmd in ai_commands:
        help_text += f"\n{cmd} {ai_commands[cmd].help_text}"
    return help_text

define_user_command("/help", print_help, "- Prints the text you are currently looking at")
define_ai_command("/search", google_search, "query - Perform a Google search")

def run(conversation: Conversation, debug) -> None:
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

        trigger_ai_command = False

        # Exit the loop and save the conversation if the user enters 'quit'
        if prompt.lower() == "/quit":
            conversation.save()
            break
        if prompt.startswith("/"):
            tokens = prompt.split()
            cmd = tokens[0]
            args = tokens[1:]
            if cmd in user_commands:
                output_stream = user_commands[cmd].call(*args)
            else:
                output_stream = [f"Unknown command {cmd}"]
        else:
            # Generate text using OpenAI's API
            output_stream = conversation.generate_text(prompt)
            trigger_ai_command = True

        while True:
            # TODO: don't print AI commands unless in debug mode
            # Display the generated text
            for string in output_stream:
                print(string, end="")
                sys.stdout.flush()
            print("\n") # this is two newlines
            if trigger_ai_command:
                message = conversation.get_last()
                if message.startswith("/"):
                    tokens = message.split(maxsplit=1)
                    cmd = tokens[0]
                    args = tokens[1]
                    if cmd in ai_commands:
                        result = ai_commands[cmd].call(args)
                    else:
                        result = f"Unknown command {cmd}"
                    if debug:
                        print(f"System: {result}\n")
                    output_stream = conversation.generate_text(result, role="system")
                else:
                    break
            else:
                break
