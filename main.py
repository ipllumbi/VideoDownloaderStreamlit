import streamlit as st
import os
import yt_dlp

def download_video(video_url, download_path='downloads'):
    """
    Download a video from a given URL using yt-dlp.

    Args:
        video_url (str): The URL of the video to download.
        download_path (str): The directory where the video will be saved. Default is 'downloads'.
    """
    # Set up options for yt-dlp
    ydl_opts = {
        'format': 'best',  # Download the best quality
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',  # Save the video in specified folder
    }

    # Create a yt-dlp object and download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)
        video_filename = ydl.prepare_filename(result)
        ydl.download([video_url])

    return video_filename


option = st.selectbox(
    "Select platform?",
    ("Youtube", "Facebook"),
)

st.write("Downloading from:", option)

video_url = st.text_input("Video Url", "")
st.write("Current video to download", video_url)

if st.button("Process Video"):
    if video_url:
        with st.spinner('Processing video...'):
            try:
                # Download the video
                video_path = download_video(video_url)
                st.success(f"Processing completed! The video is saved at: {video_path}")

                with open(video_path, 'rb') as video_file:
                    st.download_button(
                        label="Download Video",
                        data=video_file,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid video URL.")