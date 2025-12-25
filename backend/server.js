const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const UPLOAD_DIR = 'uploads';
const PROCESSED_DIR = 'processed';

if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
if (!fs.existsSync(PROCESSED_DIR)) fs.mkdirSync(PROCESSED_DIR);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});

const upload = multer({ storage });

// ------------------------
// Basic processing + AI placeholder
// ------------------------
app.post('/api/process', upload.single('image'), async (req, res) => {
  try {
    const { width, height, format, brightness, contrast, saturation, sharpness, removeBg } = req.body;
    const inputPath = req.file.path;
    const outputFilename = `${Date.now()}.${format || 'png'}`;
    const outputPath = path.join(PROCESSED_DIR, outputFilename);

    let image = sharp(inputPath);

    // Resize
    if (width || height) image = image.resize(width ? parseInt(width) : null, height ? parseInt(height) : null);

    // Enhancement (brightness/contrast/saturation/sharpness)
    if (brightness || contrast || saturation) {
      image = image.modulate({
        brightness: brightness ? parseFloat(brightness) : 1,
        saturation: saturation ? parseFloat(saturation) : 1,
      });
    }
    if (sharpness) image = image.sharpen(parseFloat(sharpness));

    // Format
    image = image.toFormat(format || 'png');

    await image.toFile(outputPath);
    fs.unlinkSync(inputPath);

    // Placeholder for AI background removal if removeBg=true
    // Here you can call Gemini/Groq APIs and replace processed image

    res.json({ url: `/${PROCESSED_DIR}/${outputFilename}` });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Image processing failed.' });
  }
});

// Serve processed images
app.use(`/${PROCESSED_DIR}`, express.static(path.join(__dirname, PROCESSED_DIR)));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
