import streamlit as st
import os
import yt_dlp
import json


# Function to show progress
def progress_hook(d, progress_bar):
    if d['status'] == 'downloading':
        percent = int(d["downloaded_bytes"] / d["total_bytes"] * 100)
        rounded_percent = round(percent, 1)  # Round progress percentage to 1 decimal place
        progress_bar.progress(rounded_percent)


def get_video_info(url):
    """
    Get video information (formats, title, etc.) from the URL.

    Args:
        url (str): The URL of the video.

    Returns:
        dict: A dictionary containing video information.
    """
    with yt_dlp.YoutubeDL({'outtmpl': '%(title)s.%(ext)s'}) as ydl:
        result = ydl.extract_info(url, download=False)

    # Filter formats to only include those with audio (i.e., 'acodec' field is not None)
    formats_with_audio = [f for f in result.get('formats', []) if f.get('acodec') != 'none']
    result['formats'] = formats_with_audio

    return result


def download_video(url, download_path='downloads', progress_bar=None, format_id=None):
    """
    Download a video from a given URL using yt-dlp for a specific format.

    Args:
        url (str): The URL of the video to download.
        download_path (str): The directory where the video will be saved. Default is 'downloads'.
        format_id (str): The format ID to download.
    """
    # Ensure the download path exists
    os.makedirs(download_path, exist_ok=True)

    # Set up options for yt-dlp
    ydl_opts = {
        'format': format_id,  # Specify the format ID for the download
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Save the video in specified folder
        'progress_hooks': [lambda d: progress_hook(d, progress_bar)]  # Hook for tracking download progress
    }

    # Create a yt-dlp object and download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)

        video_filename = ydl.prepare_filename(result)  # Get the video filename from the result
        ydl.download([url])  # Start downloading the video

    return video_filename


# Streamlit interface
video_url = st.text_input("Video URL", "https://youtu.be/Ki2ShtMRb9c?si=rQ85gu3Vz4DYNAUe")
st.write("Current video to download:", video_url)

# Initialize session state for storing formats if not already initialized
if 'formats' not in st.session_state:
    st.session_state.formats = []

if st.button("Process Video", use_container_width=True):
    st.session_state.formats = []
    if video_url:
        with st.spinner('Getting video infos...'):
            try:
                # Fetch video information (formats, title, etc.)
                video_info = get_video_info(video_url)
                formats = video_info.get('formats', [])

                # Display available video formats in 4 columns
                st.write("### Available Video Qualities:")

                for i, frmt in enumerate(formats):
                    format_id = frmt.get('format_id', 'N/A')
                    quality = frmt.get('quality', 'N/A')
                    width = frmt.get('width', 'N/A')
                    height = frmt.get('height', 'N/A')
                    fps = frmt.get('fps', 'N/A')
                    tbr = frmt.get('tbr', 'N/A')  # Bitrate
                    ext = frmt.get('ext', 'N/A')  # File extension

                    button_label = f"Quality: {quality} ({width}x{height})"
                    button_key = f"download_{i}_{format_id}"

                    print(button_key)

                    # Store format information with label and key in session state
                    st.session_state.formats.append({
                        'format_id': format_id,
                        'button_label': button_label,
                        'button_key': button_key,
                        'ext': ext
                    })

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid video URL.")

buttons = []
# Create a 4-column grid layout
cols = st.columns(4)

for i, format_info in enumerate(st.session_state.formats):
    with cols[i % 4]:
        buttons.append(st.button(format_info['button_label'], key=format_info['button_key']))

for i, button in enumerate(buttons):
        if button:
            video_path = download_video(video_url, format_id=st.session_state.formats[i]['format_id'], progress_bar=st.progress(0))
            st.success(f"Video downloaded: {video_path}")

            with open(video_path, 'rb') as video_file:
                download_button = st.download_button(
                    label=f"Download {video_path}",
                    use_container_width = True,
                    data=video_file,
                    file_name=os.path.basename(video_path),
                    mime=f"video/{st.session_state.formats[i]['ext']}"
                )

            os.remove(video_path)  # Remove the video after downloading
            st.info("The video file has been deleted after download.")
