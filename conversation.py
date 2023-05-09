import openai
import os
import yaml

class Conversation:
    """
    A class for managing conversations with OpenAI's chat model.
    
    Attributes:
        model (str): The name of the OpenAI model to use for the conversation.
        file (str or None): The name of the YAML file to load the conversation from, or None if a new conversation is being created.
        title (str or None): The title of the conversation, used as the filename if the conversation is saved to a YAML file.
        total_tokens (int): The total number of tokens used in the conversation, used to track usage for billing purposes.
        messages (list): A list of messages in the conversation, represented as dictionaries with "role" ("system", "user" or "assistant") and "content" keys.
    """
    def __init__(self, model='gpt-3.5-turbo', file=None, system_message=None):
        self.model = model
        self.file = file
        self.title = None
        self.total_tokens = 0
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})
        
        if self.file:
            try:
                self.load()
            except Exception as e:
                print(f"Error loading conversation: {e}")

    def save(self):
        """
        Save the conversation to a YAML file.
        If a file name is not specified, prompt the user for a title to use for the file.
        If a file with the same name already exists, prompt the user to confirm whether to overwrite it.
        """
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
        """
        Load conversation data from a YAML file specified by file attribute.
        Update conversation attributes with loaded data.
        """
        # Load conversation data from the provided YAML file
        with open(self.file, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        # Update conversation attributes with the loaded data
        self.__dict__.update(data)

    def print(self, debug):
        """
        Print the conversation messages in a readable format.
        If debug is true, also print system messages.
        """
        print(f"Model: {self.model}\n")
        for message in self.messages:
            text = message["content"]
            role = message["role"]
            if role == "system" and debug:
                print(f"System: {text}\n")
            elif role == "user":
                print(f"User: {text}\n")
            elif role == "assistant":
                print(f"Assistant: {text}\n")

    def generate_text(self, prompt, role="user"):
        """
        Generate a response from the chat model based on the provided prompt.
        Add the user prompt to the conversation messages, along with role "user".
        Add the generated response to the conversation messages, along with role "assistant".
        Track the total number of tokens used in the conversation for billing purposes.
        
        Args:
            prompt (str): The user's prompt to generate a response to.
            role (str): The role of the message ("system", "user" or "assistant"), defaults to "user".
            
        Returns:
            str: The generated response from the chat model.
        """
        try:
            # Add the user prompt to the conversation messages
            self.messages.append({"role": role, "content": prompt})

            yield "Assistant: "

            # Make an API call to OpenAI's chat model
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                stream=True
            )

            message = {"content": ""}
            finish_reason = None
            for chunk in response:
                choice = chunk.choices[0]
                finish_reason = choice.finish_reason
                if "role" in choice.delta:
                    message["role"] = choice.delta["role"]
                if "content" in choice.delta:
                    content = choice.delta["content"]
                    if not (content == "\n\n" and message["content"] == ""):
                        message["content"] += content
                        yield content

            # Add the generated text to the conversation messages
            self.messages.append(message)
            if finish_reason != "stop":
                yield f"\nWarning: finish_reason = {finish_reason}\n"
            # Update the total tokens used in the conversation
            #self.total_tokens += response.usage.total_tokens
        except Exception as e:
            yield f"\nError generating text: {e}\n"

    def get_last(self):
        return self.messages[-1]["content"]
