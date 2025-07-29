import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Allow all origins for simplicity, but you can restrict this in production
CORS(app)

# Configure yt-dlp options
YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True, # Ensures we only process single videos unless it's a slideshow
}

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_BASE) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            # --- Result structure ---
            result = {
                'title': info_dict.get('title'),
                'thumbnail': info_dict.get('thumbnail'),
                'duration': info_dict.get('duration'),
                'formats': [],
                'mp3_url': None,
                'image_urls': []
            }

            # --- Check for image slideshow ---
            if 'entries' in info_dict:
                # This is likely an image slideshow (treated as a playlist by yt-dlp)
                for entry in info_dict['entries']:
                    if entry.get('url') and 'image' in entry.get('url', ''):
                         result['image_urls'].append(entry['url'])
                # Use the first entry's info for title/thumbnail if top-level is missing
                if not result['title']:
                    result['title'] = info_dict['entries'][0].get('title', 'TikTok Image Post')
                if not result['thumbnail']:
                    result['thumbnail'] = info_dict['entries'][0].get('thumbnail')
            else:
                # --- This is a video post ---
                video_formats = []
                audio_formats = []

                for f in info_dict.get('formats', []):
                    # Filter for video formats that have both video and audio
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        resolution = f.get('height')
                        if resolution:
                            # Create a user-friendly quality label
                            quality_label = f"{resolution}p"
                            if f.get('fps', 0) > 30:
                                quality_label += str(f.get('fps'))
                            
                            video_formats.append({
                                'quality': quality_label,
                                'format_id': f.get('format_id'),
                                'url': f.get('url'),
                                'filesize': f.get('filesize')
                            })
                    
                    # Find the best audio-only format for MP3
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                         audio_formats.append(f)
                
                # Sort video formats by resolution (height) in descending order
                result['formats'] = sorted(video_formats, key=lambda x: int(x['quality'].split('p')[0]), reverse=True)

                # Find the best quality audio for the MP3 link (highest bitrate)
                if audio_formats:
                    best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
                    result['mp3_url'] = best_audio.get('url')


            return jsonify(result)

    except yt_dlp.utils.DownloadError as e:
        app.logger.error(f"yt-dlp error: {e}")
        return jsonify({'error': 'Failed to process TikTok URL. It might be private, invalid, or removed.'}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    # Use Gunicorn for production, this is for local dev
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)