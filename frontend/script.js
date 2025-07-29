document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('download-form');
    const urlInput = document.getElementById('tiktok-url');
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error-message');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnIcon = document.getElementById('btn-icon');
    
    // IMPORTANT: Replace this with your deployed backend URL from Render.
    // Example: 'https://your-app-name.onrender.com/download'
    const API_URL = 'https://tiktokmaster-backend.onrender.com/download'; 
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tiktokUrl = urlInput.value.trim();

        if (!tiktokUrl) {
            showError('Please paste a TikTok URL.');
            return;
        }

        // --- UI Reset and Loading State ---
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        btnText.textContent = 'Fetching...';
        btnIcon.innerHTML = `<svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
        
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: tiktokUrl }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Fetch error:', error);
            showError(error.message || 'An unknown error occurred.');
        } finally {
            // --- Reset Button State ---
            loader.classList.add('hidden');
            submitBtn.disabled = false;
            btnText.textContent = 'Fetch';
            btnIcon.innerHTML = `<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>`;
        }
    });

    function displayResults(data) {
        document.getElementById('thumbnail').src = data.thumbnail;
        document.getElementById('thumbnail').alt = data.title;
        document.getElementById('title').textContent = data.title;
        
        const videoSection = document.getElementById('video-section');
        const imageSection = document.getElementById('image-section');
        const imageGrid = document.getElementById('image-grid');

        // --- Handle Image Slideshow ---
        if (data.image_urls && data.image_urls.length > 0) {
            videoSection.classList.add('hidden');
            imageSection.classList.remove('hidden');
            imageGrid.innerHTML = ''; // Clear previous images

            data.image_urls.forEach((imgUrl, index) => {
                const a = document.createElement('a');
                a.href = imgUrl;
                a.target = '_blank';
                a.download = `tiktokmaster_image_${index + 1}.jpeg`;
                a.className = 'relative group';

                const img = document.createElement('img');
                img.src = imgUrl;
                img.alt = `Slide ${index + 1}`;
                img.className = 'w-full h-full object-cover rounded-md aspect-square';

                const downloadOverlay = document.createElement('div');
                downloadOverlay.className = 'absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity';
                downloadOverlay.innerHTML = `<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>`;
                
                a.appendChild(img);
                a.appendChild(downloadOverlay);
                imageGrid.appendChild(a);
            });

        } else { // --- Handle Video ---
            videoSection.classList.remove('hidden');
            imageSection.classList.add('hidden');
            
            const qualitySelect = document.getElementById('quality-select');
            const downloadVideoBtn = document.getElementById('download-video-btn');
            const downloadMp3Btn = document.getElementById('download-mp3-btn');

            qualitySelect.innerHTML = ''; // Clear previous options
            if (data.formats && data.formats.length > 0) {
                data.formats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format.url;
                    option.textContent = `Video - ${format.quality}`;
                    qualitySelect.appendChild(option);
                });
                downloadVideoBtn.href = data.formats[0].url; // Default to best quality
                downloadVideoBtn.classList.remove('hidden');
                qualitySelect.classList.remove('hidden');
            } else {
                 downloadVideoBtn.classList.add('hidden');
                 qualitySelect.classList.add('hidden');
            }


            qualitySelect.addEventListener('change', (e) => {
                downloadVideoBtn.href = e.target.value;
            });
            
            if(data.mp3_url) {
                downloadMp3Btn.href = data.mp3_url;
                downloadMp3Btn.classList.remove('hidden');
            } else {
                downloadMp3Btn.classList.add('hidden');
            }
        }

        // --- Show the results ---
        resultsDiv.classList.remove('hidden');
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
});