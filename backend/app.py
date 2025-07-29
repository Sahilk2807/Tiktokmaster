import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
}

def get_quality_label(height):
    """Generates a user-friendly quality label."""
    if height >= 2160:
        return f"{height}p 4K"
    if height >= 1440:
        return f"{height}p 2K"
    if height >= 1080:
        return f"{height}p Full HD"
    if height >= 720:
        return f"{height}p HD"
    return f"{height}p"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_BASE) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            result = {
                'title': info_dict.get('title'),
                'thumbnail': info_dict.get('thumbnail'),
                'duration': info_dict.get('duration'),
                'mp3_url': None,
                'formats': [],
                'image_urls': []
            }

            if 'entries' in info_dict:
                for entry in info_dict['entries']:
                    if entry.get('url'):
                        result['image_urls'].append(entry['url'])
                if not result['title']:
                    result['title'] = info_dict.get('title', 'TikTok Image Post')
                if not result['thumbnail']:
                    result['thumbnail'] = info_dict['entries'][0].get('thumbnail')
            else:
                processed_formats = {}
                audio_formats = []

                for f in info_dict.get('formats', []):
                    # Process video formats
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height'):
                        height = f.get('height')
                        # If we already have this quality, keep the one with larger filesize
                        if height in processed_formats:
                            if f.get('filesize', 0) and f['filesize'] > processed_formats[height].get('filesize', 0):
                                processed_formats[height] = f
                        else:
                            processed_formats[height] = f
                    
                    # Collect audio formats
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                         audio_formats.append(f)

                # Create clean format list for frontend
                video_formats = []
                for height, f_data in processed_formats.items():
                    video_formats.append({
                        'label': get_quality_label(height),
                        'quality': f"{height}p",
                        'url': f_data.get('url'),
                        'filesize': f_data.get('filesize')
                    })
                
                # Sort from best to worst quality
                result['formats'] = sorted(video_formats, key=lambda x: int(x['quality'].replace('p', '')), reverse=True)

                if audio_formats:
                    best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
                    result['mp3_url'] = best_audio.get('url')

            return jsonify(result)

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to process TikTok URL. It might be private, invalid, or removed.'}), 500

@app.route('/proxy', methods=['GET'])
def proxy_download():
    """Proxies a download to force 'Content-Disposition: attachment'."""
    url = request.args.get('url')
    if not url:
        return "URL parameter is missing.", 400

    try:
        # Unquote the URL to handle encoded characters
        decoded_url = unquote(url)
        
        # Make a streaming request to the video URL
        r = requests.get(decoded_url, stream=True)
        r.raise_for_status()  # Raise an exception for bad status codes

        # Get the filename from the URL path
        filename = decoded_url.split('/')[-1].split('?')[0] or "video.mp4"

        # Stream the response back to the client
        return Response(r.iter_content(chunk_size=8192),
                        content_type=r.headers.get('Content-Type', 'application/octet-stream'),
                        headers={'Content-Disposition': f'attachment; filename="{filename}"'})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Proxy request failed: {e}")
        return f"Failed to fetch the content from the provided URL. It might have expired. Error: {e}", 502 # Bad Gateway
    except Exception as e:
        app.logger.error(f"An unexpected proxy error occurred: {e}")
        return "An internal server error occurred in the proxy.", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)