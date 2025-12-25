require('dotenv').config();
const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/processed', express.static(path.join(__dirname, 'processed')));

// Multer setup
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname);
    }
});
const upload = multer({ storage: storage });

// ------------------------------
// Image Processing Endpoint
// ------------------------------
app.post('/api/process', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: 'No image uploaded' });

        const { width, height, rotate, flip, format, quality, brightness, contrast, saturation, sharpness, aiBackground } = req.body;

        let image = sharp(req.file.path);

        // Resize
        if (width || height) image = image.resize(width ? parseInt(width) : null, height ? parseInt(height) : null);

        // Rotate
        if (rotate) image = image.rotate(parseInt(rotate));

        // Flip
        if (flip === 'horizontal') image = image.flip();
        if (flip === 'vertical') image = image.flop();

        // Enhancement
        image = image.modulate({
            brightness: brightness ? parseFloat(brightness) : 1,
            saturation: saturation ? parseFloat(saturation) : 1
        }).linear(contrast ? parseFloat(contrast) : 1, 0);

        if (sharpness) image = image.sharpen(parseFloat(sharpness));

        // Format & quality
        let outputFormat = format || 'png';
        if (outputFormat === 'jpeg' || outputFormat === 'jpg') {
            image = image.jpeg({ quality: quality ? parseInt(quality) : 80 });
        } else if (outputFormat === 'webp') {
            image = image.webp({ quality: quality ? parseInt(quality) : 80 });
        } else {
            image = image.png({ quality: quality ? parseInt(quality) : 80 });
        }

        const outputFile = path.join('processed', Date.now() + '-' + req.file.originalname);
        await image.toFile(outputFile);

        // AI Background Removal (placeholder)
        if (aiBackground === 'true') {
            // Example: Call Gemini or Groq API
            // const aiResult = await axios.post('YOUR_AI_API_URL', { image: fs.createReadStream(outputFile) }, { headers: { Authorization: `Bearer ${process.env.GEMINI_API_KEY}` } });
            // For now, we just return processed image
        }

        res.json({ url: `/${outputFile}` });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Processing failed' });
    }
});

// Health check
app.get('/', (req, res) => {
    res.send('Reality Image Tool Backend is running');
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
