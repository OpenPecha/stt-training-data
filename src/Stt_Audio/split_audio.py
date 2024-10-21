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
    # Remove any characters that might cause issues in filenames
    clean_text = re.sub(r'[\\/*?:"<>|]', "", text)
    # Truncate to max_length characters
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


def split_audio_file(
    input_audio_path, csv_path, output_dir="data/Lamrim Dutsi Nyingpo_A_1"
):
    """
    Split a large audio file into segments based on timing information from a CSV file.

    args:
    input_audio_path (str): Path to the input MP3 file
    csv_path (str): Path to the CSV file containing timing information
    output_dir (str): Directory where the output segments will be saved
    Returns:
        None
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verify input files exist
    input_audio_path = Path(input_audio_path)
    csv_path = Path(csv_path)

    if not input_audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_audio_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Read the CSV file without headers
    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(
        csv_path,
        header=None,
        names=["start_time", "end_time", "duration", "transcription"],
    )

    # Load the audio file
    print(f"Loading audio file: {input_audio_path}")
    try:
        audio = AudioSegment.from_mp3(str(input_audio_path))
    except Exception as e:
        print(f"Error loading audio file: {str(e)}")
        print("Please verify that the audio file is a valid MP3 file.")
        raise

    # Create a log file for transcriptions
    log_file = output_dir / "segments_log.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Segment Log\n")
        f.write("===========\n\n")

    # Process each row in the CSV
    total_segments = len(df)
    for index, row in df.iterrows():
        try:
            # Extract timing information
            start_time = int(row["start_time"])
            end_time = int(row["end_time"])
            duration = int(row["duration"])
            transcription = row["transcription"]

            # Show progress
            print(
                f"\nProcessing segment {index + 1} of {total_segments} ({(index + 1)/total_segments*100:.1f}%):"  # noqa
            )
            print(
                f"Time range: {start_time/1000:.2f}s - {end_time/1000:.2f}s (duration: {duration/1000:.2f}s)"  # noqa
            )
            print(f"Transcription: {transcription}")

            # Extract the audio segment
            segment = audio[start_time:end_time]

            # Generate output filename in the new format: STT_TT_D001_0001_0_to_3000
            segment_number = (
                f"{index+1:04d}"  # noqa # Format as 4-digit number with leading zeros
            )
            time_range = format_time(start_time, end_time)
            output_filename = (
                output_dir / f"STT_TT_D002_{segment_number}_{time_range}.wav"
            )

            # Export the segment
            print(f"Saving segment to: {output_filename}")
            segment.export(str(output_filename), format="mp3")

            # Log the segment information
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Segment {index+1:04d}\n")  # noqa
                f.write(
                    f"Time: {start_time/1000:.2f}s - {end_time/1000:.2f}s (duration: {duration/1000:.2f}s)\n"  # noqa
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
    # Example usage - update these paths to match your files
    input_audio = "data/STT Input/135 A-Menag Dzö_1.mp3"
    csv_file = "data/STT Input/135 A-Menag Dzö_1.csv"

    try:
        split_audio_file(input_audio, csv_file)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
