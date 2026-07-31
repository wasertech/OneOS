import os
from time import sleep
from typing import Any, Dict, List, Optional, Tuple, Union
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

class InputOutputAsyncCallbackHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        _n = self.get_txt_file_count() + 1
        _id = f"{serialized['id'][-1]}-{_n}"
        prompt = prompts[0]
        self.save_input(_id, prompt)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        if hasattr(response, "generations"):
            if hasattr(response.generations[0][0], "text"):
                answer = response.generations[0][0].text
                if answer: self.save_output(answer)
    
    def get_txt_file_count(self) -> int:
        directory = 'data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        txt_files = [file for file in os.listdir(directory) if file.endswith('.txt') and not file.endswith('_output.txt')]
        return len(txt_files)
        
    def save_input(self, _id: str, prompt: str) -> None:
        #print(f"Saving input {_id}...")
        with open(f"data/{_id}.txt", 'w') as f:
            f.write(f"{prompt}")
    
    def get_last_txt_file(self) -> str:
        sleep(0.1)
        directory = 'data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        txt_files = [file for file in os.listdir(directory) if file.endswith('.txt') and not file.endswith('_output.txt')]
        sorted_files = sorted(txt_files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        return sorted_files[0]
    
    def save_output(self, answer: str) -> None:
        _f = self.get_last_txt_file()
        _nf = _f.replace('.txt', '_output.txt')
        #print(f"Saving output {_nf}...")
        with open(f"data/{_nf}", 'w') as f:
            f.write(f"{answer}")
