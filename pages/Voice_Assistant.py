import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
import pandas as pd
import threading
import json
import io
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

st.set_page_config(layout="wide", page_title="AI Voice Assistant", page_icon="🎙️")

# Inject Tailwind CSS, Google Fonts, and Custom CSS overrides
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        /* Background with soft animated mesh gradient effect */
        .stApp {
            background-color: #f0f4f8 !important;
            background-image: 
                radial-gradient(at 40% 20%, hsla(228,100%,74%,0.15) 0px, transparent 50%),
                radial-gradient(at 80% 0%, hsla(189,100%,56%,0.15) 0px, transparent 50%),
                radial-gradient(at 0% 50%, hsla(355,100%,93%,0.15) 0px, transparent 50%),
                radial-gradient(at 80% 50%, hsla(340,100%,76%,0.15) 0px, transparent 50%),
                radial-gradient(at 0% 100%, hsla(22,100%,77%,0.15) 0px, transparent 50%),
                radial-gradient(at 80% 100%, hsla(242,100%,70%,0.15) 0px, transparent 50%),
                radial-gradient(at 0% 0%, hsla(343,100%,76%,0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }
        
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
        .text-gradient {
            background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Glassmorphism Cards */
        [data-testid="stPlotlyChart"], [data-testid="stDataFrame"], [data-testid="stMetric"], .stTabs [data-baseweb="tab-list"], .bg-white.rounded-xl.shadow-md {
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-radius: 24px !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.6) !important;
        }
        
        /* Clean up Streamlit default UI elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(148, 163, 184, 0.5);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(100, 116, 139, 0.8);
        }
        
        /* Fade-in Animation */
        .block-container {
            animation: fadeIn 0.8s ease-out;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please add it to your .env file.")
    st.stop()

st.markdown("""
<div class="mb-4 text-center">
    <h1 class="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight mb-3">
        <span class="text-gradient">Real-Time</span> Voice Assistant
    </h1>
    <p class="text-gray-500 text-lg max-w-2xl mx-auto">
        Talk continuously to the AI. It will listen, query data dynamically, and respond using its voice.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Internal API Server for Tool Execution ---
try:
    df_global = pd.read_csv("cleaned_df.csv")
except:
    df_global = pd.DataFrame()

class PandasRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

    def do_POST(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            code = data.get('code', '')
            
            # Execute code safely
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            try:
                exec_globals = {'df': df_global, 'pd': pd}
                exec(code, exec_globals)
                result = redirected_output.getvalue()
                if not result.strip():
                    result = "Execution completed without printing any output. Please use print() in your code."
            except Exception as e:
                result = f"Error: {str(e)}"
            finally:
                sys.stdout = old_stdout
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'result': result}).encode())

@st.cache_resource
def start_local_server():
    for port in range(8082, 8092):
        try:
            httpd = HTTPServer(('127.0.0.1', port), PandasRequestHandler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            return port
        except OSError:
            continue
    return None

api_port = start_local_server()

@st.cache_data
def get_data_context():
    context = f"""
    You are an AI Voice Assistant for an E-Commerce dashboard.
    You have access to a dataset containing {len(df_global)} orders.
    The dataset columns are: {', '.join(df_global.columns)}.
    
    You have a tool available called `execute_pandas_code`. When the user asks deep analytical questions (e.g. "what is the first order date?", "what is the average customer age?"), you MUST use this tool to write Python code using the `df` pandas dataframe to find the exact answer.
    IMPORTANT: You must use `print()` in your Python code to return the result to yourself!
    
    After getting the result, answer the user clearly, conversationally, and naturally using your voice.
    """
    return context

system_instruction = get_data_context()
safe_instruction = system_instruction.replace("`", "'").replace("\n", " ")

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background: transparent;
        }}
        .mic-btn {{
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        .mic-btn:hover {{
            transform: scale(1.05);
        }}
        .mic-btn:active {{
            transform: scale(0.95);
        }}
        .recording {{
            animation: pulse-red 1.5s infinite;
        }}
        @keyframes pulse-red {{
            0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }}
            70% {{ box-shadow: 0 0 0 25px rgba(239, 68, 68, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
        }}
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-[400px] m-0">

    <div class="bg-white p-10 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center w-full max-w-lg">
        <button id="micBtn" class="mic-btn w-32 h-32 rounded-full bg-blue-600 hover:bg-blue-700 text-white border-none cursor-pointer text-5xl shadow-lg flex items-center justify-center outline-none focus:outline-none mb-8">
            🎙️
        </button>
        <div id="status" class="text-xl font-semibold text-gray-800 mb-2">Click to Start Conversation</div>
        <div id="log" class="text-sm font-medium text-blue-500 h-6"></div>
    </div>

    <script>
        const API_KEY = "{api_key}";
        const API_PORT = "{api_port}";
        // Use v1beta for standard API key connections
        const WS_URL = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${{API_KEY}}`;
        const systemInstructionText = `{safe_instruction}`;
        
        let ws = null;
        let audioContext = null;
        let scriptProcessor = null;
        let micStream = null;
        let isRecording = false;
        
        const micBtn = document.getElementById('micBtn');
        const statusText = document.getElementById('status');
        const logText = document.getElementById('log');

        function base64Encode(buffer) {{
            let binary = '';
            let bytes = new Uint8Array(buffer);
            for (let i = 0; i < bytes.byteLength; i++) {{
                binary += String.fromCharCode(bytes[i]);
            }}
            return window.btoa(binary);
        }}

        async function startConversation() {{
            try {{
                statusText.innerText = 'Connecting to AI...';
                logText.innerText = '';
                ws = new WebSocket(WS_URL);
                
                ws.onopen = async () => {{
                    statusText.innerText = 'Connected! Initializing...';
                    
                    // Send initial config setup
                    const configMessage = {{
                        setup: {{
                            model: "models/gemini-3.1-flash-live-preview",
                            generationConfig: {{
                                responseModalities: ["AUDIO"]
                            }},
                            tools: [{{
                                functionDeclarations: [{{
                                    name: "execute_pandas_code",
                                    description: "Execute Python code to query the pandas dataframe 'df'. Use this to answer deep analytical questions. You MUST PRINT the final answer using print().",
                                    parameters: {{
                                        type: "OBJECT",
                                        properties: {{
                                            code: {{ type: "STRING", description: "Python code to execute. The dataframe is named 'df'. Use print() to output the result." }}
                                        }},
                                        required: ["code"]
                                    }}
                                }}]
                            }}],
                            systemInstruction: {{
                                parts: [{{ text: systemInstructionText }}]
                            }}
                        }}
                    }};
                    ws.send(JSON.stringify(configMessage));
                    
                    // Setup Audio Input
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
                    micStream = await navigator.mediaDevices.getUserMedia({{ audio: {{ channelCount: 1, sampleRate: 16000 }} }});
                    
                    const source = audioContext.createMediaStreamSource(micStream);
                    scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
                    
                    scriptProcessor.onaudioprocess = (e) => {{
                        const inputData = e.inputBuffer.getChannelData(0);
                        // Convert float32 to int16
                        const pcmData = new Int16Array(inputData.length);
                        for (let i = 0; i < inputData.length; i++) {{
                            let s = Math.max(-1, Math.min(1, inputData[i]));
                            pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                        }}
                        
                        if (ws.readyState === WebSocket.OPEN) {{
                            const audioMessage = {{
                                realtimeInput: {{
                                    audio: {{
                                        mimeType: "audio/pcm;rate=16000",
                                        data: base64Encode(pcmData.buffer)
                                    }}
                                }}
                            }};
                            ws.send(JSON.stringify(audioMessage));
                        }}
                    }};
                    
                    // We connect to a gain node with 0 volume to avoid feedback loop but keep process running
                    const zeroGain = audioContext.createGain();
                    zeroGain.gain.value = 0;
                    source.connect(scriptProcessor);
                    scriptProcessor.connect(zeroGain);
                    zeroGain.connect(audioContext.destination);
                    
                    isRecording = true;
                    micBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                    micBtn.classList.add('bg-red-500', 'hover:bg-red-600', 'recording');
                    statusText.innerText = 'Listening... Start speaking!';
                }};
                
                ws.onmessage = async (event) => {{
                    let msgText = event.data;
                    if (event.data instanceof Blob) {{
                        msgText = await event.data.text();
                    }}
                    
                    const msg = JSON.parse(msgText);
                    
                    if (msg.toolCall) {{
                        const call = msg.toolCall.functionCalls[0];
                        if (call.name === "execute_pandas_code") {{
                            logText.innerText = 'AI is analyzing data...';
                            const code = call.args.code;
                            
                            try {{
                                const response = await fetch(`http://127.0.0.1:${{API_PORT}}/execute`, {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json' }},
                                    body: JSON.stringify({{ code: code }})
                                }});
                                const data = await response.json();
                                
                                const toolResponse = {{
                                    toolResponse: {{
                                        functionResponses: [{{
                                            id: call.id,
                                            name: call.name,
                                            response: {{ result: data.result }}
                                        }}]
                                    }}
                                }};
                                ws.send(JSON.stringify(toolResponse));
                                logText.innerText = 'Analysis complete. Speaking...';
                            }} catch (err) {{
                                console.error('Tool execution error:', err);
                                const errorResponse = {{
                                    toolResponse: {{
                                        functionResponses: [{{
                                            id: call.id,
                                            name: call.name,
                                            response: {{ error: err.toString() }}
                                        }}]
                                    }}
                                }};
                                ws.send(JSON.stringify(errorResponse));
                            }}
                        }}
                    }}
                    
                    if (msg.serverContent && msg.serverContent.modelTurn) {{
                        const parts = msg.serverContent.modelTurn.parts;
                        for (const part of parts) {{
                            if (part.inlineData && part.inlineData.data) {{
                                logText.innerText = 'AI is speaking...';
                                playAudioBase64(part.inlineData.data);
                            }}
                        }}
                    }}
                }};
                
                ws.onclose = (event) => {{
                    stopConversation();
                    statusText.innerText = `Connection closed. Click to restart.`;
                    console.error('WebSocket Closed:', event.code, event.reason);
                }};
                
                ws.onerror = (e) => {{
                    console.error(e);
                    stopConversation();
                    statusText.innerText = 'Connection error.';
                }};
                
            }} catch(e) {{
                console.error(e);
                statusText.innerText = 'Error accessing microphone.';
            }}
        }}
        
        let audioQueue = [];
        let isPlaying = false;
        
        async function playAudioBase64(base64Data) {{
            const binaryString = window.atob(base64Data);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {{
                bytes[i] = binaryString.charCodeAt(i);
            }}
            
            const pcm16 = new Int16Array(bytes.buffer);
            const audioBuffer = audioContext.createBuffer(1, pcm16.length, 24000);
            const channelData = audioBuffer.getChannelData(0);
            for(let i = 0; i < pcm16.length; i++) {{
                channelData[i] = pcm16[i] / 32768.0;
            }}
            
            audioQueue.push(audioBuffer);
            if(!isPlaying) {{
                playNextInQueue();
            }}
        }}
        
        function playNextInQueue() {{
            if (audioQueue.length === 0) {{
                isPlaying = false;
                logText.innerText = 'Listening...';
                return;
            }}
            isPlaying = true;
            const buffer = audioQueue.shift();
            const source = audioContext.createBufferSource();
            source.buffer = buffer;
            source.connect(audioContext.destination);
            source.onended = playNextInQueue;
            source.start();
        }}

        function stopConversation() {{
            if (ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{ clientContent: {{ turnComplete: true }} }}));
                ws.close();
            }}
            if (scriptProcessor) {{
                scriptProcessor.disconnect();
            }}
            if (micStream) {{
                micStream.getTracks().forEach(track => track.stop());
            }}
            if (audioContext && audioContext.state !== 'closed') {{
                audioContext.close();
            }}
            isRecording = false;
            micBtn.classList.remove('bg-red-500', 'hover:bg-red-600', 'recording');
            micBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
            statusText.innerText = 'Click to Start Conversation';
            logText.innerText = '';
            audioQueue = [];
            isPlaying = false;
        }}

        micBtn.addEventListener('click', () => {{
            if (isRecording) {{
                stopConversation();
            }} else {{
                startConversation();
            }}
        }});
    </script>
</body>
</html>
"""

components.html(html_code, height=600)
