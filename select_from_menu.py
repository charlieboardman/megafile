import questionary

def select_from_menu(menu_options_path,prompt):
    with open(menu_options_path, 'r') as options_file:
        
        menu_items = [menu_item.strip('\n') for menu_item in options_file.readlines() if not menu_item.startswith('#')]
        
        question = [
            {
                'type': 'list',
                'name': 'choice',
                'message': f'{prompt}:',
                'choices': menu_items
                }
            ]
        
        menu_item = questionary.prompt(question)
        
        return menu_item['choice']