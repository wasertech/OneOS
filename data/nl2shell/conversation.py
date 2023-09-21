
class Conversation:
    conversation = []
    
    def __init__(self, agent, locutor, env):
        self.system = str(agent)
        self.locutor = locutor
        self.env = env

    def add_message(self, message: dict):
        self.conversation.append(message)
    
    def __str__(self):
        '''Returns the conversation history as string.'''
        return "\n".join([f"Human: {h.get('message')}" if h.get('role') else "Assistant: {h.get('message')}" for h in self.conversation[:-2]])

    def format_instruction(self):
        '''Returns the instruction as string.'''
        return []
    
    def format_prompt(self):
        '''Returns the prompt as string.'''
        return []