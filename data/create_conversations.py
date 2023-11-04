from data_manager import Conversations, Conversation, User, Agent, SystemPrompt, Environment, Tools, Tool

if __name__ == '__main__':

    system = SystemPrompt()
    Conversation(
        [
            Conversation([

            ],
            system=system)
        ]
    )


    def load_data():
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding="utf8") as f:
                return json.load(f)
        else:
            return []

    choices = {
        'add': "Create a new conversation",
        'exit': "Exit",
    }
    _choices_map = {v.lower(): k for k, v in choices.items()}

    _choices = [c for c in choices.values()]

    def get_choice(choice, map):
        return map[choice]

    def get_observation(action, action_input):
        from client.chains.tools.python import get_tool as get_python_tool
        from client.chains.tools.search import get_tool as get_search_tool
        from client.chains.tools.shell import get_tool as get_bash_tool
        
        if action == 'Search':
            search_tool = get_search_tool()[0]
            return search_tool.run(action_input)
        elif action == 'final_answer':
            return None
        elif action == 'Bash':
            bash_tool = get_bash_tool()[0]
            return bash_tool.run(action_input)
        elif action == 'Python':
            python_tool = get_python_tool()[0]
            return python_tool.run(action_input)
        else:
            return None

    conversations = load_data()

    print("Welcome to the Assistant Console!")

    print(f"There are {len(conversations)} conversations in the database.")

    choice = questionary.select(
        "What would you like to do?",
        choices=_choices).ask().lower()

    while get_choice(choice, _choices_map) != "exit":
        system_message = questionary.text("System: ").ask()
        instruction_message = questionary.text("Instruction: ").ask()
        conversation = []

        tool_names = ['Search', 'Bash', 'Python', 'final_answer']

        # Add messages to conversation until user wants to exit
        add_message_choices = {
            'add': "Add message",
            'exit': "End conversation",
        }
        _add_message_choices_map = {v.lower(): k for k, v in add_message_choices.items()}
        _add_message_choices = [c for c in add_message_choices.values()]
        add_message_choice = "add message"

        while get_choice(add_message_choice, _add_message_choices_map) != "exit":
            first_role = "human"
            first_message = questionary.text("Human: ").ask()
            conversation.append({'role': first_role, 'message': first_message})

            assistant_reply = {
                'role': 'assistant',
                'scratchpad': []
            }
            assistant_action = assistant_action_input = ""

            while assistant_action != "final_answer":
                assistant_thought = questionary.text("(Assistant) Thought: ").ask()
                assistant_action = questionary.select(
                    "(Assistant) Action: ",
                    choices=tool_names
                ).ask()
                assistant_action_input = questionary.text("(Assistant) Action Input: ").ask()
                assistant_observation = get_observation(assistant_action, assistant_action_input)
                if assistant_observation and assistant_action != 'final_answer':
                    assistant_reply['scratchpad'].append({
                        'thought': assistant_thought,
                        'action': assistant_action,
                        'action_input': assistant_action_input,
                        'observation': assistant_observation
                    })
                else:
                    assistant_reply['scratchpad'].append({
                        'thought': assistant_thought,
                        'action': assistant_action,
                        'action_input': assistant_action_input,
                    })
            
            assistant_reply['message'] = assistant_action_input
            conversation.append(assistant_reply)

            # Continue conversation?
            add_message_choice = questionary.select(
                "What would you like to do?",
                choices=_add_message_choices
            ).ask().lower()
        
        conversations.append({
            'system': system_message,
            'instruction': instruction_message,
            'conversation': conversation,
            'tools': tool_names
        })
        # Create a new conversation or exit?
        choice = questionary.select(
        "What would you like to do?",
        choices=_choices).ask().lower()
    
    def save_data(data):
        with open('data.json', 'w', encoding="utf8") as f:
            json.dump(data, f)
    
    print("Saving data...")

    save_data(conversations)

    print("Done. Goodbye!")

        

