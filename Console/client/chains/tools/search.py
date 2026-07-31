from langchain.tools import Tool, DuckDuckGoSearchRun

engine = DuckDuckGoSearchRun()

def get_tool():
    return [
            Tool(
                name="Search",
                func=engine.run,
                description="useful when you need more context to answer a question; you should use targeted search terms"
                )
        ]