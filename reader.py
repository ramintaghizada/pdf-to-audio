import sys, asyncio, re, subprocess
from pypdf import PdfReader
import edge_tts

VOICE = "en-US-AriaNeural"
MIN_SIZE = 1500      
MAX_SIZE = 5000      
TIMEOUT = 90       
RETRIES = 3
CONCURRENCY = 15

def pick_chunk_size(text, concurrency, MIN_SIZE=1500, MAX_SIZE=5000):
    ideal = len(text) // (concurrency * 3)   
    return max(MIN_SIZE, min(MAX_SIZE, ideal))

def clean(text):
    text = re.sub(r"-\n", "", text)
    text = re.sub(r"\n+", " ", text)
    return text.strip()

def notify(title, message):
    subprocess.run(["notify-send", title, message])

def split_text(text, size=MIN_SIZE):
    size = pick_chunk_size(text, CONCURRENCY)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > size and current:
            chunks.append(current)
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current)
    return chunks

async def synth_chunk(text):
    data = bytearray()
    communicate = edge_tts.Communicate(text, VOICE, rate="+0%")
    async for item in communicate.stream():
        if item["type"] == "audio":
            data.extend(item["data"])
    return bytes(data)

async def process(i, chunk, sem, results, progress, total):
    async with sem:
        for attempt in range(1, RETRIES + 1):
            try:
                results[i] = await asyncio.wait_for(synth_chunk(chunk), TIMEOUT)
                progress[0] += 1
                print(f"{progress[0]}/{total} done")
                return
            except Exception as e:
                print(f"Chunk {i + 1} failed (attempt {attempt}): {e}")
                await asyncio.sleep(2 * attempt)
                if attempt == RETRIES:
                    raise

async def main(pdf_path, out_path):
    reader = PdfReader(pdf_path)
    text = " ".join(clean(p.extract_text() or "") for p in reader.pages)
    chunks = split_text(text)
    total = len(chunks)
    print(f"{total} chunks to convert")

    sem = asyncio.Semaphore(CONCURRENCY)
    results = [None] * total
    progress = [0]

    try:
        await asyncio.gather(
            *(process(i, c, sem, results, progress, total) for i, c in enumerate(chunks))
        )
    except Exception as e:
        notify("PDF Reader", f"Failed: {e}")
        raise

    with open(out_path, "wb") as f:
        for part in results:       
            f.write(part)

    print("Saved:", out_path)
    notify("PDF Reader", f"Audio is ready: {out_path}")
    subprocess.run(["ffplay", "-nodisp", "-autoexit", out_path])

asyncio.run(main(sys.argv[1], "output.mp3"))