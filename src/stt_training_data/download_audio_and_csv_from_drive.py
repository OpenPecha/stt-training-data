import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate_google_drive():
    """
    Authenticate and return a GoogleDrive instance.
    """
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("data/client_secrets.json")
    gauth.LocalWebserverAuth()  # Creates local webserver for authentication
    return GoogleDrive(gauth)


def download_files_from_folder(drive, folder_id, output_dir):
    """
    Download all MP3 and CSV files from a specified Google Drive folder.

    Args:
        drive (GoogleDrive): An authenticated GoogleDrive instance.
        folder_id (str): The ID of the folder in Google Drive from which to download files.
        output_dir (str): The local directory where the downloaded files will be saved.

    Returns:
        None
    """
    file_list = drive.ListFile(
        {"q": f"'{folder_id}' in parents and trashed=false"}
    ).GetList()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in file_list:
        file_name = file["title"]

        if file_name.endswith(".mp3") or file_name.endswith(".csv"):
            print(f"Downloading {file_name}...")
            file.GetContentFile(os.path.join(output_dir, file_name))


if __name__ == "__main__":
    # Set the folder ID and output directory
    FOLDER_ID = "1ChX5UQJI4Umvo0mpNPJgmMB0CEs_NEYx"
    OUTPUT_DIR = "./downloaded_files"

    # Authenticate and create a GoogleDrive instance
    drive = authenticate_google_drive()

    # Download files from the specified folder
    download_files_from_folder(drive, FOLDER_ID, OUTPUT_DIR)

    print("Download complete. Files saved to", OUTPUT_DIR)
