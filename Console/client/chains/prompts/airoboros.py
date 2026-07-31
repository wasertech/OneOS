"""
Airoboros prompt templates.
"""

JSON_FUNC_INSTRUCTIONS = """\
As an AI assistant, \
please select the most suitable \
function and parameters \
from the list of available functions below, \
based on the user's input. \
Provide your response in JSON format.\
"""

JSON_FUNC = f"""\
{JSON_FUNC_INSTRUCTIONS}

Input: {{query}}

Available functions:
{{functions}}
"""
