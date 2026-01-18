import asyncio
import logging
from pathlib import Path

from src.integrations import salute_speech
from src.services import minutes


"""async def main() -> None:
    file_path = "audio_2026-01-16_15-50-07.ogg"
    print(file_path.split(".")[-1])
    path = Path(file_path)
    audio_data = path.read_bytes()
    segment_transcriptions = []
    for audio_segment in minutes_of_meetings.split_audio_on_segments(audio_data, "m4a"):
        segment_transcription = await salute_speech.recognize_async(
            audio_data=audio_segment.data,
            audio_encoding="PCM_S16LE",
            max_speakers_count=10,
        )
        segment_transcriptions.append(segment_transcription)
    audio_transcription = "\n".join(segment_transcriptions)
    minutes_of_meeting = await minutes_of_meetings.generate(audio_transcription)
    print(minutes_of_meeting)
    with open("Протокол совещания.md", "w", encoding="utf-8") as file:
        file.write(minutes_of_meeting)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())"""

from src.core.schemas import DocumentExt

for ext in list(DocumentExt):
    print(ext)
