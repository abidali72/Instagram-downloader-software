import React, { useState, useEffect, useRef } from 'react';
import { Download, Link, Loader2, PlayCircle, AlertCircle, History, Pause, Play, Trash2, CheckCircle } from 'lucide-react';

function App() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [metadata, setMetadata] = useState(null);
    const [error, setError] = useState(null);
    const [selectedQuality, setSelectedQuality] = useState(null);
    const [downloading, setDownloading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [history, setHistory] = useState([]);
    const [isPaused, setIsPaused] = useState(false);

    // Refs for tracking download state
    const abortControllerRef = useRef(null);
    const downloadedBytesRef = useRef(0);
    const totalBytesRef = useRef(0);

    // Load history from localStorage
    useEffect(() => {
        const savedHistory = localStorage.getItem('download_history');
        if (savedHistory) {
            setHistory(JSON.parse(savedHistory));
        }
    }, []);

    const saveToHistory = (item) => {
        const newHistory = [item, ...history.filter(h => h.id !== item.id)].slice(0, 10);
        setHistory(newHistory);
        localStorage.setItem('download_history', JSON.stringify(newHistory));
    };

    const clearHistory = () => {
        setHistory([]);
        localStorage.removeItem('download_history');
    };

    const fetchMetadata = async () => {
        setLoading(true);
        setError(null);
        setMetadata(null);
        try {
            const response = await fetch('/api/v1/metadata', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch metadata');
            }

            const data = await response.json();
            setMetadata(data);
            if (data.qualities && data.qualities.length > 0) {
                setSelectedQuality(data.qualities[0].url);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const startDownload = async () => {
        if (!selectedQuality) return;

        setDownloading(true);
        setIsPaused(false);
        setProgress(0);
        downloadedBytesRef.current = 0;

        await performDownload(selectedQuality);
    };

    const performDownload = async (targetUrl, startByte = 0) => {
        abortControllerRef.current = new AbortController();

        try {
            const headers = {};
            if (startByte > 0) {
                headers['Range'] = `bytes=${startByte}-`;
            }

            const response = await fetch(`/api/v1/download?url=${encodeURIComponent(targetUrl)}`, {
                headers,
                signal: abortControllerRef.current.signal
            });

            if (!response.ok && response.status !== 206) {
                throw new Error('Download failed to start');
            }

            const reader = response.body.getReader();
            const contentLength = +response.headers.get('Content-Length');
            totalBytesRef.current = (startByte > 0) ? downloadedBytesRef.current + contentLength : contentLength;

            let receivedBytes = startByte;

            // We'll collect chunks to create a blob at the end
            // Note: In a real "save location" scenario, we'd use FileSystemAccessAPI or stream to disk
            // Here we simulate the streaming and progress.
            const chunks = [];

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                chunks.push(value);
                receivedBytes += value.length;
                downloadedBytesRef.current = receivedBytes;

                if (totalBytesRef.current) {
                    setProgress(Math.round((receivedBytes / totalBytesRef.current) * 100));
                }
            }

            // If we finished successfully
            const blob = new Blob(chunks);
            const downloadLink = document.createElement('a');
            downloadLink.href = URL.createObjectURL(blob);
            downloadLink.download = metadata.title.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.mp4';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);

            saveToHistory({
                id: metadata.id,
                title: metadata.title,
                thumbnail: metadata.thumbnail,
                date: new Date().toLocaleDateString(),
                platform: metadata.platform
            });

            setDownloading(false);
        } catch (err) {
            if (err.name === 'AbortError') {
                console.log('Download paused/aborted');
            } else {
                setError(err.message);
                setDownloading(false);
            }
        }
    };

    const handlePause = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setIsPaused(true);
        }
    };

    const handleResume = () => {
        setIsPaused(false);
        performDownload(selectedQuality, downloadedBytesRef.current);
    };

    return (
        <div className="container" style={{ maxWidth: '900px' }}>
            <h1>Legal Video Downloader</h1>
            <p className="subtitle">Download videos from authorized platforms only</p>

            {error && (
                <div className="error-msg">
                    <AlertCircle size={18} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
                    {error}
                </div>
            )}

            <div className="input-group">
                <input
                    type="text"
                    placeholder="Paste video URL (Pexels, Pixabay, or direct MP4 link)..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={loading || downloading}
                />
                <button onClick={fetchMetadata} disabled={!url || loading || (downloading && !isPaused)}>
                    {loading ? <Loader2 className="animate-spin" size={20} /> : <Link size={20} />}
                    {loading ? 'Fetching...' : 'Get Video'}
                </button>
            </div>

            {metadata && (
                <div className="metadata-card">
                    <img src={metadata.thumbnail} alt="Thumbnail" className="thumbnail" />
                    <div className="info">
                        <div>
                            <div className="title">{metadata.title}</div>
                            <div className="duration">
                                <PlayCircle size={14} style={{ marginRight: '4px' }} />
                                {metadata.duration > 0 ? `${Math.round(metadata.duration)}s • ` : ''}{metadata.platform}
                            </div>
                        </div>

                        {metadata.qualities.length > 0 ? (
                            <>
                                <div className="quality-selector">
                                    <select
                                        value={selectedQuality}
                                        onChange={(e) => setSelectedQuality(e.target.value)}
                                        disabled={downloading}
                                    >
                                        {metadata.qualities.map((q, idx) => (
                                            <option key={idx} value={q.url}>{q.label}</option>
                                        ))}
                                    </select>
                                </div>

                                <button
                                    onClick={startDownload}
                                    disabled={downloading}
                                    style={{ marginTop: '1rem', width: '100%' }}
                                >
                                    <Download size={20} />
                                    {downloading ? 'Downloading...' : 'Start Download'}
                                </button>
                            </>
                        ) : (
                            <div className="instructions" style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                                <p style={{ color: 'var(--text-main)', fontWeight: '600', marginBottom: '0.5rem' }}>How to Download from Instagram:</p>
                                <ol style={{ paddingLeft: '1.2rem' }}>
                                    <li>Open the Reel/Post in your browser.</li>
                                    <li>Right-click and select <strong>Inspect</strong> (or press F12).</li>
                                    <li>Go to the <strong>Network</strong> tab and filter by <strong>Media</strong>.</li>
                                    <li>Play the video; a <code>.mp4</code> link will appear.</li>
                                    <li>Right-click that link, select <strong>Copy URL</strong>, and paste it here.</li>
                                </ol>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {downloading && (
                <div className="progress-container">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.8rem', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                            {isPaused ? 'Paused' : `Downloading... ${progress}%`}
                        </span>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            {isPaused ? (
                                <button onClick={handleResume} className="btn-small" style={{ padding: '0.4rem 1rem' }}>
                                    <Play size={16} /> Resume
                                </button>
                            ) : (
                                <button onClick={handlePause} className="btn-small" style={{ padding: '0.4rem 1rem', background: 'var(--warning)' }}>
                                    <Pause size={16} /> Pause
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="progress-bar">
                        <div className={`progress-fill ${isPaused ? 'paused' : ''}`} style={{ width: `${progress}%` }}></div>
                    </div>
                </div>
            )}

            {history.length > 0 && (
                <div className="history-section">
                    <div className="history-title">
                        <History size={20} /> Recent Downloads
                        <button
                            onClick={clearHistory}
                            style={{ marginLeft: 'auto', background: 'transparent', color: 'var(--text-muted)', padding: '0.5rem' }}
                        >
                            <Trash2 size={16} />
                        </button>
                    </div>
                    <div className="history-list">
                        {history.map((item, idx) => (
                            <div key={idx} className="history-item">
                                <img src={item.thumbnail} alt="Preview" />
                                <div className="history-info">
                                    <div className="title">{item.title}</div>
                                    <div className="meta">{item.date} • {item.platform}</div>
                                </div>
                                <CheckCircle size={18} color="var(--success)" />
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
