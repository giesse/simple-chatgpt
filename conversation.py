import openai
import os
import yaml

class Conversation:
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
