import asyncio
import logging
from pathlib import Path

import aiofiles

from src.integrations import salute_speech

logger = logging.getLogger(__name__)

chunks_dir = Path.cwd() / "chunks"
output_dir = Path.cwd() / "transcripts"
output_dir.mkdir(exist_ok=True)


async def main() -> None:
    for file_path in chunks_dir.iterdir():
        async with aiofiles.open(file_path, mode="rb") as file:
            data = await file.read()
            logger.info(
                "Start transcribing for audio `%s`, file size %s mb",
                file_path.name, round(len(data) / 1_000_000, 2)
            )
            md_text = await salute_speech.recognize_async(data, audio_encoding="MP3")
        md_file = output_dir / f"{file_path.stem}.md"
        md_file.write_text(md_text, encoding="utf-8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
