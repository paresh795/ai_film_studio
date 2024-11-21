def extract_json_from_markdown(markdown_text: str) -> str:
    """Extract JSON content from markdown code block."""
    if markdown_text.startswith('```json\n'):
        markdown_text = markdown_text[7:]
    if markdown_text.endswith('\n```'):
        markdown_text = markdown_text[:-4]
    return markdown_text.strip() 