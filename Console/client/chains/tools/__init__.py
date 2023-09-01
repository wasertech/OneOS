
def get_all_tools():
    from .python import get_tool as get_python_tool
    from .search import get_tool as get_search_tool
    from .wikipedia import get_tool as get_wikipedia_tool
    from .shell import get_tool as get_shell_tool
    
    tools = []
    
    tools += get_python_tool()
    tools += get_search_tool()
    tools += get_wikipedia_tool()
    tools += get_shell_tool()
    
    return tools