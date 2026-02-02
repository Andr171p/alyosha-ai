from pathlib import Path

from pydub import AudioSegment
from pydub.utils import make_chunks

segment_duration_ms = 20 * 60 * 1000

output_dir = Path.cwd() / "chunks"
output_dir.mkdir(exist_ok=True)
file_path = "../30.01.2026 11.m4a"

audio = AudioSegment.from_file(file_path)
chunks = make_chunks(audio, segment_duration_ms)
for i, chunk in enumerate(chunks):
    chunk_file = output_dir / f"{Path(file_path).stem}-{i}.mp3"
    chunk.export(chunk_file, format="mp3")
