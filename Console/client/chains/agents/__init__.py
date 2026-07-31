from typing import List, Optional, Tuple, Union, Any
from langchain.chains import LLMChain
from langchain.agents import BaseMultiActionAgent
from langchain.schema import AgentAction, AgentFinish
from Console.client.chains.parsers import get_output_parser
from Console.client.chains.prompts import get_prompt, template
from Console.client.chains.agents.__executor__ import get_executor_from_agent_and_tools

class MultiActionAgent(BaseMultiActionAgent):
    """Custom Multi-Action Agent."""

    @property
    def input_keys(self):
        return ["input"]

    def plan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        output = self.llm_chain.run(
            intermediate_steps=intermediate_steps,
            **kwargs,
        )
        return self.output_parser.parse(output)

    async def aplan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        if len(intermediate_steps) == 0:
            return [
                AgentAction(tool="Search", tool_input=kwargs["input"], log=""),
                AgentAction(tool="RandomWord", tool_input=kwargs["input"], log=""),
            ]
        else:
            return AgentFinish(return_values={"output": "bar"}, log="")

def get_initialized_agent(llm, prompt, output_parser, tools, verbose=False, agent_kwargs={}):

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    tool_names = [tool.name for tool in tools]
    
    agent = MultiActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        # stop=["\nObservation:"],
        allowed_tools=tool_names,
    )
    return get_executor_from_agent_and_tools(agent=agent, tools=tools, verbose=False, agent_kwargs=agent_kwargs)
