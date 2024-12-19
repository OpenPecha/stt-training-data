import os
import re

import pandas as pd

# Define the CloudFront base URL
CLOUDFRONT_URL = "https://d38pmlk0v88drf.cloudfront.net/wav16k/"

# Regular expression to extract segment information from the log file
SEGMENT_PATTERN = re.compile(
    r"Segment (\d+)\nTime: ([\d.]+)s - ([\d.]+)s \(duration: ([\d.]+)s\)\nFilename: (.+)\nTranscription: (.+)"
)


def get_log_file(folder):
    """
    Find the log file in the given folder that starts with 'segments_log'.

    args:
    folder (str): Path to the folder where the log file is stored.

    Returns:
    str: The path to the log file.
    """
    log_files = [f for f in os.listdir(folder) if f.startswith("segments_log")]
    if not log_files:
        raise FileNotFoundError(f"No log file found in {folder}.")
    return os.path.join(folder, log_files[0])


def read_log_file(log_file_path):
    """
    Read the contents of the log file.

    args:
    log_file_path (str): Path to the log file.

    Returns:
    str: The content of the log file.
    """
    with open(log_file_path, encoding="utf-8") as log:
        return log.read()


def extract_segments(log_content):
    """
    Extract audio segment information from the log content using a regular expression.

    args:
    log_content (str): Content of the log file.

    Returns:
    list: A list of tuples containing segment information.
    """
    return SEGMENT_PATTERN.findall(log_content)


def construct_audio_url(filename):
    """
    Construct the full audio URL based on the filename.

    args:
    filename (str): The filename of the audio segment.

    Returns:
    str: The full URL to access the audio file.
    """
    return f"{CLOUDFRONT_URL}{filename}"


def process_segments(segments):
    """
    Process each audio segment, extract the necessary data, and store it in a list.

    args:
    segments (list): List of tuples containing segment information.

    Returns:
    list: A list of processed data with each entry containing [filename, dept, audio_url, duration, transcription].
    """
    data = []

    for segment in segments:
        segment_id, start_time, end_time, duration, filename, transcription = segment

        # Extract department code (e.g., TT from 'STT_TT_D001_0001_0_to_3000.wav')
        dept = filename.split("_")[1]

        # Construct the audio URL
        audio_url = construct_audio_url(filename)

        # Convert the duration from string to float (in seconds)
        duration_in_seconds = float(duration)

        # Append processed data to the list
        data.append(
            [filename, dept, audio_url, duration_in_seconds, transcription.strip()]
        )

    return data


def save_to_csv(data, output_csv):
    """
    Save the processed data into a CSV file.

    args:
    data (list): The processed data to be saved.
    output_csv (str): Path to the output CSV file.

    Returns:
    None
    """
    df = pd.DataFrame(
        data,
        columns=[
            "file_name",
            "dept",
            "audio_url",
            "audio_duration_in_seconds",
            "transcript",
        ],
    )
    df = df.sort_values(by="file_name")  # Sort by file_name in ascending order
    df.to_csv(output_csv, index=False)
    print(f"CSV file '{output_csv}' created successfully.")


def process_audio_folders(audio_folders, output_csv):
    """
    Process the audio folders, extract segment information from the logs, and save the data to a CSV.

    args:
    audio_folders (list): List of paths to audio folders.
    output_csv (str): Path to the output CSV file.

    """
    data = []

    for folder in audio_folders:
        try:
            log_file_path = get_log_file(folder)
            log_content = read_log_file(log_file_path)
            segments = extract_segments(log_content)
            data.extend(process_segments(segments))
        except Exception as e:
            print(f"Error processing folder '{folder}': {str(e)}")

    # Save the collected data to a CSV file
    save_to_csv(data, output_csv)


def main():
    """
    Main function to process audio folders and generate the CSV file.
    """
    audio_folders = [
        "data/split_segments/135 A-Menag Dzö_1",
        "data/split_segments/135 B-Menag Dzö-2",
        "data/split_segments/137 A-Menag Dzö-3",
        "data/split_segments/137 B-Menag Dzö-4",
        "data/split_segments/138 A-Menag Dzö-5",
        "data/split_segments/138 B-Menag Dzö-6",
        "data/split_segments/139 A-Menag Dzo-7",
        "data/split_segments/139 B-Menag Dzo-8",
        "data/split_segments/140 A-Menag Dzö_9",
        "data/split_segments/140 B-Menag Dzo_10",
        "data/split_segments/141 A-Menag Dzo-11",
        "data/split_segments/Lamrim Dutsi Nyingpo_A_1",
        "data/split_segments/Lamrim Dutsi Nyingpo_A_2",
        "data/split_segments/Lamrim Dutsi Nyingpo_A_3",
    ]  # Update with actual folder paths
    output_csv = "data/drupchen_training_data.csv"

    # Process the audio folders and save the results to a CSV
    process_audio_folders(audio_folders, output_csv)


if __name__ == "__main__":
    main()
