from client.chains.parsers import (
    # column_csv,
    markdown_json,
)

def get_output_parser():
    return markdown_json.MarkdownOutputParser()
