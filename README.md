# 📸 Instagram & Video Downloader

A professional, high-performance web application designed for downloading videos from various platforms including Instagram, Pexels, and Pixabay. Built with a modern **React** frontend and a robust **FastAPI** backend.

![Project Preview](https://img.shields.io/badge/Status-Active-brightgreen)
![Tech Stack](https://img.shields.io/badge/Tech-React%20%7C%20FastAPI%20%7C%20Vite-blue)

## ✨ Features

- **Multi-Platform Support**: Download videos from Instagram (via direct media links), Pexels, and Pixabay.
- **Quality Selection**: Choose from various available resolutions and formats.
- **Download History**: Keep track of your recent downloads locally.
- **Real-time Progress**: Monitor your download progress with a sleek UI.
- **Pause/Resume**: Full control over your downloads with pause and resume functionality.
- **Premium Design**: Modern, responsive, and aesthetic user interface with dark mode support.
- **Rate Limiting**: Integrated backend protection to prevent abuse.

## 🚀 Tech Stack

### Frontend
- **React.js**: For a dynamic and responsive UI.
- **Vite**: Ultra-fast build tool and development server.
- **Lucide React**: For beautiful, consistent iconography.
- **Vanilla CSS**: Custom-crafted styles for a premium look and feel.

### Backend
- **FastAPI**: High-performance Python framework for building APIs.
- **Pydantic**: Data validation and settings management.
- **SlowAPI**: Rate limiting to ensure service stability.
- **HTTPX**: Asynchronous HTTP client for fetching metadata and streaming content.

## 🛠️ Installation & Setup

### Prerequisites
- Node.js (v16+)
- Python (v3.9+)

### 1. Clone the Repository
```bash
git clone https://github.com/abidali72/Instagram-downloader-software.git
cd Instagram-downloader-software
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
DEBUG=True
PEXELS_API_KEY=your_pexels_key
PIXABAY_API_KEY=your_pixabay_key
RATE_LIMIT_PER_MINUTE=10
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

## 🏃 Running the Application

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Start Frontend
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`.

## 🔒 Security & Privacy

- All API keys and sensitive details are managed via environment variables.
- `.env` files are excluded from version control to ensure security.
- The application uses secure streaming to handle file transfers.

## 📜 License

This project is for educational purposes. Please ensure you have the right to download and use the content from the respective platforms.

---

Made with ❤️ by [Abid Ali](https://github.com/abidali72)
