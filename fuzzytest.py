from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder

def fuzzy_autocomplete_prompt(field, strings):
    class FuzzyCompleter(Completer):
        def get_completions(self, document, complete_event):
            # Get the entire line up to the cursor
            line_before_cursor = document.current_line_before_cursor

            # Find matches using fuzzyfinder
            matches = fuzzyfinder(line_before_cursor, strings)

            # Yield Completion items for each match, replacing the entire line
            for m in matches:
                # -len(line_before_cursor) will replace the whole line before the cursor
                yield Completion(m, start_position=-len(line_before_cursor))

    user_input = prompt(f'Enter {field}: ', completer=FuzzyCompleter())
    return user_input

#with open('ledger.csv','r') as ledger_file:
#    ledger = csv.reader(ledger_file)
#    for row in ledger:
#        if row[0] != 'Date':
#            vendors.add(row[9])
#vendor = fuzzy_autocomplete_prompt('vendor',vendors)
