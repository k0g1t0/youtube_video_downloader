from pytubefix import YouTube  # import the YouTube class from the pytubefix library for downloading YouTube videos
from pytubefix.cli import on_progress  # import the on_progress callback to track download progress
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip  # import the necessary tools for video editing
import os  # import the os module for file operations like renaming and deleting files
import re  # import the re module for regular expression operations

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', filename)  # remove characters that are not allowed in filenames

def download_stream(stream: object, output_path='./') -> str:
    try:
        return stream.download(output_path=output_path)  # download the desired stream and save it in the specified path
    except Exception as e:
        print(f"failed to download: {e}")  # if download not successful print the relative error
        return None

def download_and_merge(url: str):
    try:
        # create a YouTube object with the provided URL and set the progress callback
        yt = YouTube(url, on_progress_callback=on_progress)

        # rename and sanitize the filename
        final_filename = f"{sanitize_filename(yt.title)}.mp4"

        # check if the file already exists
        if os.path.exists(final_filename):
            print(f"{final_filename} already exist")
            return

        # filter for the highest resolution video stream available
        video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
        if not video_stream:
            print("no video stream found")
            return

        # filter for the highest bitrate audio stream available
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
        if not audio_stream:
            print("no audio stream found")
            return

        # download the video and audio streams using the download_stream() function
        video_filename = download_stream(video_stream)
        audio_filename = download_stream(audio_stream)

        if not video_filename or not audio_filename:
            print("failed to download streams")
            return

        # temporary filenames for the downloaded video and audio
        video_tmp = "temp_video.mp4"
        audio_tmp = "temp_audio.mp4"

        # rename the downloaded files to temporary names for processing
        os.rename(video_filename, video_tmp)
        os.rename(audio_filename, audio_tmp)

        # load the video and audio clips using moviepy
        with VideoFileClip(video_tmp) as video_clip, AudioFileClip(audio_tmp) as audio_clip:
            # combine the audio with the video clip
            video_clip.audio = CompositeAudioClip([audio_clip])  # set the audio of the video clip

            # write the final video file with the combined audio
            video_clip.write_videofile(final_filename)

        # remove the temporary files after processing
        os.remove(video_tmp)
        os.remove(audio_tmp)

    except Exception as e:
        print(f"error: {e}")
