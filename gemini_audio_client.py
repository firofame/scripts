# gemini_audio_client.py

import asyncio
import os
import numpy as np
from google import genai
from google.genai.types import (Content, LiveConnectConfig, Part,
                                PrebuiltVoiceConfig, SpeechConfig,
                                VoiceConfig)
from tqdm.asyncio import tqdm
from pydub import AudioSegment
from typing import Callable, Tuple, Optional

# --- API-SPECIFIC CONFIGURATION ---
MODEL_NAME = "models/gemini-2.5-flash-native-audio-preview-09-2025"
VOICE_NAME = "Charon"
DEFAULT_SAMPLE_RATE = 24000

# --- INITIALIZE THE CLIENT AND CONFIG ---
try:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config = LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=SpeechConfig(
            voice_config=VoiceConfig(
                prebuilt_voice_config=PrebuiltVoiceConfig(voice_name=VOICE_NAME)
            )
        ),
    )
except KeyError:
    print("FATAL: GEMINI_API_KEY environment variable not set.")
    client = None
    config = None

async def fetch_audio_data(prompt_text: str) -> np.ndarray | None:
    """
    Connects to the Gemini API with a given prompt and fetches the audio.
    Returns a NumPy array of the audio data on success, or None on failure.
    """
    if not client:
        print("API client is not initialized. Cannot fetch audio.")
        return None
        
    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=config) as session:
            await session.send_client_content(
                turns=Content(role="user", parts=[Part(text=prompt_text)])
            )

            audio_data_chunks = []
            async for message in session.receive():
                if message.server_content.model_turn and message.server_content.model_turn.parts:
                    for part in message.server_content.model_turn.parts:
                        if part.inline_data:
                            audio_data_chunks.append(np.frombuffer(part.inline_data.data, dtype=np.int16))

            if audio_data_chunks:
                return np.concatenate(audio_data_chunks)
            else:
                return None
    except Exception as e:
        print(f"An exception occurred during the API call: {e}")
        return None

# --- HIGH-LEVEL BATCH PROCESSING LOGIC ---

LineProcessorFn = Callable[[str, int], Optional[Tuple[str, str]]]

async def _process_task(prompt: str, output_path: str, semaphore, pbar_stats):
    """Internal worker to process a single audio generation task."""
    identifier = output_path
    async with semaphore:
        pbar_stats['active'] += 1
        try:
            audio_array = await fetch_audio_data(prompt)
            if audio_array is not None:
                # Convert numpy array to an AudioSegment
                audio_segment = AudioSegment(
                    audio_array.tobytes(),
                    frame_rate=DEFAULT_SAMPLE_RATE,
                    sample_width=audio_array.dtype.itemsize,
                    channels=1
                )
                # Export as MP3
                audio_segment.export(output_path, format="mp3", bitrate="64k")
                pbar_stats['success'] += 1
            else:
                tqdm.write(f"✗ FAILED: {identifier} (API returned None)")
                pbar_stats['failed'] += 1
        except Exception as e:
            tqdm.write(f"✗ UNEXPECTED FAILED: {identifier}. Error: {e}")
            pbar_stats['failed'] += 1
        finally:
            pbar_stats['active'] -= 1

async def process_text_file_concurrently(
    input_file: str,
    system_prompt: str,
    line_processor_fn: LineProcessorFn,
    concurrency_limit: int = 100,
):
    """
    Reads lines from an input file and generates audio concurrently.

    Args:
        input_file: Path to the text file to process.
        system_prompt: The base prompt to prepend to each line's text.
        line_processor_fn: A callback function that takes (line, index) and
                           returns a tuple of (text_for_prompt, output_filepath).
                           It can return None to skip a line.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
        return

    tasks_to_run = []
    dirs_to_create = set()
    for i, line in enumerate(lines):
        processed = line_processor_fn(line, i)
        if not processed:
            continue
        
        text_for_prompt, output_path = processed
        if not os.path.exists(output_path):
            full_prompt = f"{system_prompt}{text_for_prompt}"
            tasks_to_run.append((full_prompt, output_path))
            # Ensure the parent directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                dirs_to_create.add(output_dir)

    if not tasks_to_run:
        print("All audio files already exist. Nothing to do.")
        return

    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)

    print(f"Total lines: {len(lines)} | To generate: {len(tasks_to_run)}")
    print(f"Concurrency: {concurrency_limit}")
    
    semaphore = asyncio.Semaphore(concurrency_limit)
    pbar_stats = {'active': 0, 'success': 0, 'failed': 0}
    
    tasks = [_process_task(prompt, path, semaphore, pbar_stats) for prompt, path in tasks_to_run]
    
    try:
        with tqdm(total=len(tasks_to_run), desc="Generating Audio", unit="file") as pbar:
            for future in asyncio.as_completed(tasks):
                pbar.set_postfix(pbar_stats, refresh=True)
                await future
                pbar.update(1)
            pbar.set_postfix(pbar_stats, refresh=True)

    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down gracefully...")
    finally:
        print("\n--- Generation Summary ---")
        print(f"✓ Successful: {pbar_stats['success']}")
        print(f"✗ Failed:     {pbar_stats['failed']}")
        print("--------------------------")

# --- Self-Test Block ---
async def _test_fetch():
    print("--- Running API Self-Test ---")
    test_prompt = "Hello, world. This is a test of the audio generation system."
    audio = await fetch_audio_data(test_prompt)
    if audio is not None:
        print(f"SUCCESS: Fetched audio data with shape {audio.shape} and dtype {audio.dtype}.")
        print("Generic API client appears to be working correctly.")
    else:
        print("FAILURE: Could not fetch audio data.")

if __name__ == "__main__":
    asyncio.run(_test_fetch())