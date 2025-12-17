/**
 * Voice Recording Module for PocketPortal Web Interface
 * =====================================================
 * 
 * Provides voice recording capabilities using Web Audio API.
 * Features:
 * - Record audio from microphone
 * - Real-time visualization
 * - Send to server for transcription
 * - Playback controls
 * 
 * Usage:
 *   const recorder = new VoiceRecorder();
 *   await recorder.init();
 *   await recorder.startRecording();
 *   const audioBlob = await recorder.stopRecording();
 *   const transcription = await recorder.sendForTranscription(audioBlob);
 */

class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.audioContext = null;
        this.analyser = null;
        this.visualizationCallback = null;
    }

    /**
     * Initialize audio recording
     */
    async init() {
        try {
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                } 
            });

            // Setup MediaRecorder
            const mimeType = this._getSupportedMimeType();
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: mimeType,
                audioBitsPerSecond: 128000
            });

            // Setup audio visualization
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            const source = this.audioContext.createMediaStreamSource(this.stream);
            source.connect(this.analyser);
            this.analyser.fftSize = 256;

            // Handle audio data
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            console.log('✅ Voice recorder initialized');
            console.log(`📝 Using MIME type: ${mimeType}`);
            
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize recorder:', error);
            throw new Error(`Microphone access denied or not available: ${error.message}`);
        }
    }

    /**
     * Get supported audio MIME type
     */
    _getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/mp4',
            'audio/mpeg'
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }

        return 'audio/webm'; // Fallback
    }

    /**
     * Start recording
     */
    async startRecording() {
        if (this.isRecording) {
            console.warn('⚠️ Already recording');
            return;
        }

        this.audioChunks = [];
        
        try {
            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            console.log('🎤 Recording started');

            // Start visualization if callback provided
            if (this.visualizationCallback) {
                this._visualize();
            }
        } catch (error) {
            console.error('❌ Failed to start recording:', error);
            throw error;
        }
    }

    /**
     * Stop recording and return audio blob
     */
    async stopRecording() {
        if (!this.isRecording) {
            console.warn('⚠️ Not recording');
            return null;
        }

        return new Promise((resolve, reject) => {
            this.mediaRecorder.onstop = () => {
                try {
                    const mimeType = this.mediaRecorder.mimeType;
                    const audioBlob = new Blob(this.audioChunks, { type: mimeType });
                    
                    this.isRecording = false;
                    console.log('🛑 Recording stopped');
                    console.log(`📦 Audio blob size: ${(audioBlob.size / 1024).toFixed(2)} KB`);
                    
                    resolve(audioBlob);
                } catch (error) {
                    reject(error);
                }
            };

            this.mediaRecorder.stop();
        });
    }

    /**
     * Send audio to server for transcription
     */
    async sendForTranscription(audioBlob, wsConnection) {
        try {
            console.log('📤 Sending audio for transcription...');

            // Convert blob to base64
            const base64Audio = await this._blobToBase64(audioBlob);

            // Send via WebSocket
            wsConnection.send(JSON.stringify({
                type: 'voice',
                audio: base64Audio,
                format: audioBlob.type
            }));

            console.log('✅ Audio sent to server');
        } catch (error) {
            console.error('❌ Failed to send audio:', error);
            throw error;
        }
    }

    /**
     * Convert blob to base64
     */
    _blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * Set visualization callback
     */
    setVisualizationCallback(callback) {
        this.visualizationCallback = callback;
    }

    /**
     * Visualize audio levels
     */
    _visualize() {
        if (!this.isRecording || !this.visualizationCallback) {
            return;
        }

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteFrequencyData(dataArray);

        // Calculate average volume
        const average = dataArray.reduce((a, b) => a + b) / bufferLength;
        const normalized = average / 255; // 0-1 range

        this.visualizationCallback(normalized);

        requestAnimationFrame(() => this._visualize());
    }

    /**
     * Create audio player for playback
     */
    createAudioPlayer(audioBlob) {
        const audio = new Audio();
        audio.src = URL.createObjectURL(audioBlob);
        audio.controls = true;
        return audio;
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        console.log('🧹 Voice recorder cleaned up');
    }
}


/**
 * Voice UI Controller
 * Handles UI interactions for voice recording
 */
class VoiceUIController {
    constructor(wsConnection) {
        this.recorder = new VoiceRecorder();
        this.wsConnection = wsConnection;
        this.recordButton = null;
        this.statusIndicator = null;
        this.visualizer = null;
    }

    /**
     * Initialize voice UI
     */
    async init(recordButtonId, statusIndicatorId, visualizerId) {
        this.recordButton = document.getElementById(recordButtonId);
        this.statusIndicator = document.getElementById(statusIndicatorId);
        this.visualizer = document.getElementById(visualizerId);

        try {
            await this.recorder.init();
            this._setupRecordButton();
            this._setupVisualization();
            this._updateStatus('ready', '🎤 Ready to record');
        } catch (error) {
            this._updateStatus('error', `❌ ${error.message}`);
            this.recordButton.disabled = true;
        }
    }

    /**
     * Setup record button
     */
    _setupRecordButton() {
        this.recordButton.addEventListener('click', async () => {
            if (!this.recorder.isRecording) {
                await this._startRecording();
            } else {
                await this._stopRecording();
            }
        });
    }

    /**
     * Start recording
     */
    async _startRecording() {
        try {
            await this.recorder.startRecording();
            this.recordButton.textContent = '🛑 Stop Recording';
            this.recordButton.classList.add('recording');
            this._updateStatus('recording', '🎤 Recording...');
        } catch (error) {
            this._updateStatus('error', `❌ ${error.message}`);
        }
    }

    /**
     * Stop recording and send
     */
    async _stopRecording() {
        try {
            this.recordButton.disabled = true;
            this._updateStatus('processing', '⏳ Processing...');

            const audioBlob = await this.recorder.stopRecording();
            
            if (audioBlob) {
                // Send for transcription
                await this.recorder.sendForTranscription(audioBlob, this.wsConnection);
                this._updateStatus('sent', '✅ Sent for transcription');
            }

            this.recordButton.textContent = '🎤 Record Voice';
            this.recordButton.classList.remove('recording');
            this.recordButton.disabled = false;

            // Reset status after 2 seconds
            setTimeout(() => {
                this._updateStatus('ready', '🎤 Ready to record');
            }, 2000);

        } catch (error) {
            this._updateStatus('error', `❌ ${error.message}`);
            this.recordButton.disabled = false;
        }
    }

    /**
     * Setup audio visualization
     */
    _setupVisualization() {
        if (!this.visualizer) return;

        this.recorder.setVisualizationCallback((level) => {
            // Update visualizer height/color based on audio level
            const height = Math.max(3, level * 100);
            this.visualizer.style.height = `${height}%`;
            
            // Color gradient from green to red
            const hue = 120 - (level * 60); // 120 = green, 60 = yellow, 0 = red
            this.visualizer.style.backgroundColor = `hsl(${hue}, 70%, 50%)`;
        });
    }

    /**
     * Update status indicator
     */
    _updateStatus(state, message) {
        if (!this.statusIndicator) return;

        this.statusIndicator.textContent = message;
        this.statusIndicator.className = `status status-${state}`;
    }

    /**
     * Cleanup
     */
    cleanup() {
        this.recorder.cleanup();
    }
}


// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VoiceRecorder, VoiceUIController };
}
