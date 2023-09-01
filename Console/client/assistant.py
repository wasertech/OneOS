from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown

from client.chains.single_command import SingleCommandAssistant
from client.chains.session import SessionAssistant

class Assistant:
    console = Console()
    error_console = Console(stderr=True, style="bold red")
    
    def log_query(self, query):
        self.console.print(query, style="italic blue", justify="right")
        # Log the user query

    def log_response(self, response):
        self.console.print(response, style="bold white", justify="left")
        # Log the response

    def log_error(self, error):
        self.error_console.print(error, style="bold red", justify="left")
        # Log the error

    def single_command(self, command):
        # Interpret a single command
        assistant = SingleCommandAssistant()
        response = Markdown(assistant(command))
        self.log_response(response)
        return response

    def script_from_file(self, file, args):
        # Interpret a script from file + args
        pass
    
    def script_from_stdin(self, stdin):
        pass
        # Interpret a script from stdin

    def interactive_mode(self):
        # Interactive mode (command loop)
        session = PromptSession(message="User: ")
        assistant = SessionAssistant()
        while True:
            try:
                query = session.prompt()
                if not query:
                    continue
                if query in ["stop", "exit", "quit", "q", ":q", "Q", ":Q", "/quit", "/q", "/stop", "/exit"]:
                    break
                #self.log_query(query)
                response = Markdown(assistant(query))
                self.log_response(response)
            except EOFError:
                break
            except KeyboardInterrupt:
                self.log_error("\nTo exit the program, type 'exit' or 'quit'.")
                continue
    
    def ask_closed_question(self, question="Yes or no?") -> bool:
        # Ask a closed question (yes/no)
        pass

    def listen(self):
        pass
        # Interactive mode (command loop) from Microphone
