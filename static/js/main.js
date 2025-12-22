// Reality Bender Tools - Main JavaScript

function showLoader() {
    document.getElementById('loader').classList.remove('hidden');
}

function hideLoader() {
    document.getElementById('loader').classList.add('hidden');
}

// Background Remover
document.getElementById('bgForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoader();
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/remove-bg', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'no_background.png';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const data = await response.json();
            alert('Error: ' + (data.error || 'Processing failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoader();
        this.reset();
    }
});

// AI Translator
document.getElementById('transForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoader();
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/translate', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('transResult');
        const textElement = resultDiv.querySelector('p');
        
        if (data.success) {
            textElement.textContent = data.text;
            resultDiv.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Translation failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoader();
    }
});

// Passport Photo
document.getElementById('passportForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoader();
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/passport', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'passport_photo.jpg';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const data = await response.json();
            alert('Error: ' + (data.error || 'Processing failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoader();
        this.reset();
    }
});

// Meme Generator
document.getElementById('memeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoader();
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/meme', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'meme.jpg';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const data = await response.json();
            alert('Error: ' + (data.error || 'Processing failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoader();
        this.reset();
    }
});

// Social Media Resizer
document.getElementById('resizeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoader();
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/resize', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.download = 'resized_image.jpg';
            a.href = url;
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const data = await response.json();
            alert('Error: ' + (data.error || 'Processing failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoader();
        this.reset();
    }
});

// Text Analyzer (Groq AI)
document.getElementById('textForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoader();
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/text-analyze', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('textResult');
        const textElement = resultDiv.querySelector('p');
        
        if (data.success) {
            textElement.textContent = data.analysis;
            resultDiv.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Analysis failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoader();
    }
});
