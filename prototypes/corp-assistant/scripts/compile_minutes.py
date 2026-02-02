import asyncio
import logging
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.settings import PROMPTS_DIR, settings
from src.utils import md_to_pdf

MEETING_MINUTES_PROMPT = (PROMPTS_DIR / "meeting_minutes_prompt.md").read_text(encoding="utf-8")

transcripts_dir = Path.cwd() / "transcripts"


async def generate_meeting_minutes(transcription: str) -> str:
    """Генерирует протокол совещания по его транскрибации.

    :param transcription: Транскрибация совещания.
    :returns: Составленный протокол в Markdown формате.
    """

    model = ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3,
    )
    prompt = ChatPromptTemplate.from_template(MEETING_MINUTES_PROMPT)
    chain = prompt | model | StrOutputParser()
    return await chain.ainvoke({"transcription": transcription})


async def main() -> None:
    transcripts = [
        file_path.read_text(encoding="utf-8")
        for file_path in transcripts_dir.iterdir()
    ]
    full_transcription = "\n".join(transcripts)
    md_content = await generate_meeting_minutes(full_transcription)
    md_content = md_content.replace("```", "").replace("markdown", "")
    pdf_file = md_to_pdf(md_content)
    Path("../30.01.2026 11.pdf").write_bytes(pdf_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
