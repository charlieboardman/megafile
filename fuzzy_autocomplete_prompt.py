from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder

class FuzzyCompleter(Completer):
    def __init__(self, options):
        self.options = options

    def get_completions(self, document, complete_event):
        word = document.text_before_cursor
        completions = fuzzyfinder(word, self.options)
        for completion in completions:
            yield Completion(
                completion,
                start_position=-len(word),
            )

def fuzzy_autocomplete_prompt(field, options):
    """
    Prompt the user for input with fuzzy autocomplete functionality.
    
    :param field: The name of the field being prompted for (used in the prompt message).
    :param options: A list of strings to use for autocomplete options.
    :return: The user's input as a string.
    """
    user_input = prompt(
        f'Enter {field}: ',
        completer=FuzzyCompleter(options)
    )
    return user_input

if __name__ == "__main__":
    # Example usage
    sample_options = ["apple", "banana", "cherry", "date", "elderberry"]
    result = fuzzy_autocomplete_prompt("fruit", sample_options)
    print(f"You selected: {result}")