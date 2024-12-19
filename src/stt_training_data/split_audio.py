import re
from pathlib import Path

import pandas as pd
from pydub import AudioSegment

# Explicitly set the FFmpeg paths for macOS
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffmpeg = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"


def clean_filename(text, max_length=50):
    """
    Create a clean filename from Tibetan text.
    Truncates the text and removes any characters that might cause issues in filenames.
    args:
        text (str): The input text to be sanitized.
        max_length (int): The maximum length of the output filename. Defaults to 50 characters.

    Returns:
        str: A cleaned and truncated version of the input text that is safe for use as a filename.
    """
    clean_text = re.sub(r'[\\/*?:"<>|]', "", text)
    clean_text = clean_text[:max_length]
    return clean_text


def format_time(start_ms, end_ms):
    """Format the time range for the filename
    args:
        start_ms (int): The start time in milliseconds.
        end_ms (int): The end time in milliseconds.
    Returns:
        str: A formatted string representing the time range in the format 'start_ms_to_end_ms'.
    """
    return f"{start_ms}_to_{end_ms}"


def split_audio_files_in_folder(input_dir, output_dir="data/split_segments"):
    """
    Split multiple audio files into segments based on their corresponding CSV files.

    args:
        input_dir (str): Directory containing audio and CSV files with matching filenames.
        output_dir (str): Directory where the output segments will be saved.
    Returns:
        None
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all MP3 files in the directory
    audio_files = list(input_dir.glob("*.mp3"))

    for idx, audio_file in enumerate(audio_files):
        prefix = f"STT_TT_D{idx+1:03d}"
        csv_file = input_dir / f"{audio_file.stem}.csv"
        if not csv_file.exists():
            print(f"CSV file not found for {audio_file.name}, skipping...")
            continue

        try:
            print(f"Processing: {audio_file.name} with {csv_file.name}")
            split_audio_file(audio_file, csv_file, output_dir / audio_file.stem, prefix)
        except Exception as e:
            print(f"Error processing {audio_file.name}: {str(e)}")


def split_audio_file(input_audio_path, csv_path, output_dir, prefix):
    """
    Split a large audio file into segments based on timing information from a CSV file.

    args:
        input_audio_path (str): Path to the input MP3 file
        csv_path (str): Path to the CSV file containing timing information
        output_dir (str): Directory where the output segments will be saved
        prefix (str): Prefix for the output filenames
    Returns:
        None
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_audio_path = Path(input_audio_path)
    csv_path = Path(csv_path)

    if not input_audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_audio_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(
        csv_path,
        header=None,
        names=["start_time", "end_time", "duration", "transcription"],
    )

    print(f"Loading audio file: {input_audio_path}")
    try:
        audio = AudioSegment.from_mp3(str(input_audio_path))
    except Exception as e:
        print(f"Error loading audio file: {str(e)}")
        raise

    log_file = output_dir / "segments_log.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Segment Log\n")
        f.write("===========\n\n")

    total_segments = len(df)
    for index, row in df.iterrows():
        try:
            start_time = int(row["start_time"])
            end_time = int(row["end_time"])
            duration = int(row["duration"])
            transcription = row["transcription"]

            print(
                f"\nProcessing segment {index + 1} of {total_segments} ({(index + 1)/total_segments*100:.1f}%):"
            )
            print(
                f"Time range: {start_time/1000:.2f}s - {end_time/1000:.2f}s (duration: {duration/1000:.2f}s)"
            )
            print(f"Transcription: {transcription}")

            segment = audio[start_time:end_time]

            segment_number = f"{index+1:04d}"
            time_range = format_time(start_time, end_time)
            output_filename = output_dir / f"{prefix}_{segment_number}_{time_range}.wav"

            print(f"Saving segment to: {output_filename}")
            segment.export(str(output_filename), format="mp3")

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Segment {index+1:04d}\n")
                f.write(
                    f"Time: {start_time/1000:.2f}s - {end_time/1000:.2f}s (duration: {duration/1000:.2f}s)\n"
                )
                f.write(f"Filename: {output_filename.name}\n")
                f.write(f"Transcription: {transcription}\n")
                f.write("-" * 80 + "\n\n")

        except Exception as e:
            print(f"Error processing segment {index + 1}: {str(e)}")
            continue

    print("\nAudio splitting completed!")
    print(f"A detailed log has been saved to: {log_file}")


def main():
    input_dir = "downloaded_files"
    try:
        split_audio_files_in_folder(input_dir)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
