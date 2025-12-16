from pathlib import Path

from markitdown import MarkItDown

from ..core import DocumentWorkflowStructure


def convert_ms_word_to_markdown(workflow_structure: DocumentWorkflowStructure) -> None:
    md = MarkItDown()
    result = md.convert(workflow_structure.input_file)
    Path(...).write_text(result.text_content, encoding="utf-8")
