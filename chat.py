from conversation import Conversation
import sys
from googlesearch import search
import requests

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
        yield ("Available commands:\n"
            "/multiline - starts multiline input\n"
            "/quit - save the conversation and exit")
        for cmd in user_commands:
            yield f"\n{cmd} {user_commands[cmd].help_text}"

def google_search(query: str) -> str:
    results = search(query, num_results=10, advanced=True)
    text = ""
    for result in results:
        text += f"{result.title}\n{result.description}\n{result.url}\n\n"
    return text

def read_url(url: str) -> str:
    response = requests.get(url)
    return f"{response.status_code} {response.reason}\n\n{response.text}\n"

def ai_help():
    help_text = ("As a programming and research assistant, you have access to specialized "
            "commands to execute actions. To ensure proper functioning, please adhere to the "
            "following guidelines:\n\n"
            "1. Commands should be placed at the beginning of your response, "
            "starting with a '/' (slash) symbol.\n"
            "2. Do not include commands within or at the end of text meant for user visibility. "
            "They will not be executed in such cases.\n"
            "3. Execute only one command at a time.\n"
            "4. The user will not see any messages containing commands or their outputs. "
            "Only you will be able to view the results of a command.\n"
            "5. Refrain from instructing the user to execute a command, as it creats confusion.\n"
            "6. Do not mention a command in a response starting with phrases such as \"Sure, let me...\". "
            "Type the command directly to initiate the action.\n\n"
            "Available commands include:")
    for cmd in ai_commands:
        help_text += f"\n- {cmd} {ai_commands[cmd].help_text}"

    help_text += "\n\nPlease follow these guidelines to ensure smooth interactions within the system."
    return help_text

define_user_command("/help", print_help, "- Prints the text you are currently looking at")
define_ai_command("/search", google_search, "query: This initiates a Google search based on the given query.")
define_ai_command("/get", read_url, "url: This fetches the raw content of a specified URL")

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
