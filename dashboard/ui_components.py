"""
SURAKSHA-NET UI/UX Component Library
Reusable responsive cards, chat bubbles, badges, alerts, and navigation components.
"""

import streamlit as st
import html
from typing import Optional, Dict, Any, List

def inject_custom_css():
    """Injects modern, responsive, high-contrast tactical styling and floating elements."""
    st.markdown("""
    <style>
        /* Base typography and theme */
        .stApp {
            background-color: #0b0f19;
            color: #e6edf3;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* Top Header Styling */
        .suraksha-header {
            background: linear-gradient(135deg, #101c2e 0%, #172a45 50%, #0d2238 100%);
            padding: 20px 24px;
            border-radius: 10px;
            border-left: 6px solid #ff9900;
            border-top: 1px solid #1f3a5f;
            border-right: 1px solid #1f3a5f;
            border-bottom: 1px solid #1f3a5f;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.4);
        }

        /* Simulation Banner */
        .sim-banner {
            background: linear-gradient(90deg, #2d1804 0%, #3e2206 100%);
            border: 1px solid #d29922;
            color: #f0883e;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 2px 8px rgba(210, 153, 34, 0.15);
        }

        /* Emergency Active Banner */
        .emergency-banner {
            background: linear-gradient(90deg, #5c1414 0%, #7a1a1a 100%);
            border: 2px solid #f85149;
            color: #ffffff;
            padding: 14px 20px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 18px;
            animation: pulse-danger 1.6s infinite;
            box-shadow: 0 4px 16px rgba(248, 81, 73, 0.4);
        }

        @keyframes pulse-danger {
            0% { box-shadow: 0 0 0 0 rgba(248, 81, 73, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(248, 81, 73, 0); }
            100% { box-shadow: 0 0 0 0 rgba(248, 81, 73, 0); }
        }

        /* Status Badges */
        .badge-safe {
            background-color: #0e4429;
            color: #3fb950;
            padding: 5px 14px;
            border-radius: 14px;
            font-weight: 700;
            font-size: 12px;
            border: 1px solid #238636;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .badge-warning {
            background-color: #4d2d00;
            color: #d29922;
            padding: 5px 14px;
            border-radius: 14px;
            font-weight: 700;
            font-size: 12px;
            border: 1px solid #9e6a03;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .badge-emergency {
            background-color: #6e1010;
            color: #ff7b72;
            padding: 5px 14px;
            border-radius: 14px;
            font-weight: 800;
            font-size: 12px;
            border: 1px solid #da3633;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            animation: pulse-badge 1.4s infinite;
        }

        @keyframes pulse-badge {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }

        /* Modern Card Containers */
        .tactical-card {
            background-color: #121824;
            border: 1px solid #242c3d;
            border-radius: 10px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            transition: border-color 0.2s ease, transform 0.2s ease;
        }
        .tactical-card:hover {
            border-color: #3b4861;
            transform: translateY(-1px);
        }

        /* Quick Action Cards */
        .quick-action-btn {
            background: #182234;
            border: 1px solid #2a374e;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .quick-action-btn:hover {
            background: #202d44;
            border-color: #388bfd;
        }

        /* Gemini / WhatsApp Style Chat Bubbles */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 14px;
            margin-top: 10px;
            margin-bottom: 20px;
        }

        .chat-bubble-user {
            align-self: flex-end;
            background: linear-gradient(135deg, #0d3826 0%, #155734 100%);
            border: 1px solid #238636;
            color: #e6edf3;
            padding: 12px 18px;
            border-radius: 16px 16px 2px 16px;
            max-width: 82%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-size: 14.5px;
            line-height: 1.5;
        }

        .chat-bubble-assistant {
            align-self: flex-start;
            background: linear-gradient(135deg, #131c2e 0%, #18243b 100%);
            border: 1px solid #2f3e5b;
            color: #e6edf3;
            padding: 14px 20px;
            border-radius: 16px 16px 16px 2px;
            max-width: 86%;
            box-shadow: 0 3px 10px rgba(0,0,0,0.35);
            font-size: 14.5px;
            line-height: 1.55;
        }

        .chat-meta {
            font-size: 11px;
            color: #8b949e;
            margin-top: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-ai-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: #1c2a42;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10.5px;
            color: #58a6ff;
            border: 1px solid #388bfd33;
        }

        /* Guided Tour Box */
        .guide-box {
            background: linear-gradient(135deg, #162438 0%, #1c304d 100%);
            border: 1px solid #388bfd;
            border-radius: 10px;
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(56, 139, 253, 0.2);
        }

        /* Floating Pill Button */
        .floating-chat-pill {
            position: fixed;
            bottom: 24px;
            right: 28px;
            background: linear-gradient(135deg, #1f6feb 0%, #238636 100%);
            color: #ffffff !important;
            padding: 12px 20px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 14px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.5);
            z-index: 999999;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 2px solid #58a6ff;
            text-decoration: none !important;
            transition: all 0.25s ease;
        }
        .floating-chat-pill:hover {
            transform: scale(1.06) translateY(-2px);
            box-shadow: 0 8px 24px rgba(88, 166, 255, 0.5);
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str = "SURAKSHA-NET", subtitle: str = "Smart Soldier Rescue, Survival & Telemetry Command"):
    """Renders the top tactical command header."""
    st.markdown(f"""
    <div class="suraksha-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; font-size: 26px; color: #ffffff; letter-spacing: 0.5px;">🛡️ {html.escape(title)}</h1>
                <p style="margin: 4px 0 0 0; color: #8b949e; font-size: 13.5px;">
                    {html.escape(subtitle)}
                </p>
            </div>
            <div style="margin-top: 8px;">
                <span class="badge-safe">SYSTEM READY</span>
                <span style="color: #8b949e; font-size: 12px; margin-left: 10px;">TACTICAL NODE TBOC-01</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_simulation_disclaimer():
    """Renders the required simulation mode disclaimer banner."""
    st.markdown("""
    <div class="sim-banner">
        <span style="font-size: 18px;">⚠️</span>
        <div>
            <strong>SIMULATION MODE — NOT CONNECTED TO REAL FIELD DEVICES</strong><br/>
            <span style="font-weight: 400; font-size: 12px; color: #c9d1d9;">
                All soldier vitals, blast impact readings, GPS coordinates, and mesh routing paths are emulated in software for testing and demonstration purposes.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_emergency_banner(emergency_count: int, emergency_summary: str = ""):
    """Renders a prominent top emergency alert if any casualties are active."""
    if emergency_count > 0:
        st.markdown(f"""
        <div class="emergency-banner">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    🚨 <strong>CRITICAL COMBAT CASUALTY ALERT: {emergency_count} PERSONNEL IN EMERGENCY STATE</strong>
                    <div style="font-size: 13px; font-weight: 400; margin-top: 2px;">
                        {html.escape(emergency_summary or "Immediate automated triage beacon active. Check Personnel Monitoring & Incident Log.")}
                    </div>
                </div>
                <div style="font-size: 12px; background: rgba(0,0,0,0.3); padding: 4px 10px; border-radius: 4px; margin-top: 6px;">
                    PRIORITY 1 TACTICAL ACTION REQUIRED
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_floating_chat_pill():
    """Renders the floating launcher badge at the bottom-right of the viewport."""
    st.markdown("""
    <a href="#ask-suraksha-ai" class="floating-chat-pill" title="Click or navigate to AI Assistant in sidebar">
        <span>🤖</span>
        <span>Ask SURAKSHA AI</span>
    </a>
    """, unsafe_allow_html=True)


def render_voice_support_widget():
    """
    Renders an HTML5 Web Speech API voice input widget with fallback.
    Supports voice-to-text in browser and text-to-speech feedback.
    """
    st.markdown("""
    <div style="background: #101622; border: 1px solid #232d3f; border-radius: 8px; padding: 12px 16px; margin: 10px 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">🎙️</span>
                <strong>Voice Assistant Input (Web Speech API)</strong>
            </div>
            <span style="font-size: 11px; color: #8b949e;">Chrome / Edge / Safari Supported</span>
        </div>
        <p style="font-size: 12.5px; color: #8b949e; margin: 6px 0 10px 0;">
            Click <em>Start Listening</em> to speak your question in English or Tenglish. Your browser will transcribe speech directly into the input.
        </p>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button id="voice-start-btn" onclick="startSurakshaVoice()" style="background: #1f6feb; border: none; color: white; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600;">
                🎤 Start Listening
            </button>
            <button id="voice-stop-btn" onclick="stopSurakshaVoice()" style="background: #30363d; border: 1px solid #484f58; color: white; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px;">
                ⏹️ Stop
            </button>
            <button id="voice-speak-btn" onclick="speakLastResponse()" style="background: #238636; border: none; color: white; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px;">
                🔊 Read Last Answer (TTS)
            </button>
        </div>
        <div id="voice-status" style="margin-top: 8px; font-size: 12px; color: #58a6ff;"></div>
        <div id="voice-transcript" style="margin-top: 4px; font-size: 13px; color: #7ee787; font-style: italic;"></div>
    </div>

    <script>
        var recognition;
        var isListening = false;

        function startSurakshaVoice() {
            var statusDiv = document.getElementById('voice-status');
            var transcriptDiv = document.getElementById('voice-transcript');

            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                statusDiv.innerHTML = "⚠️ Speech Recognition is not supported by this browser. Please use standard text input.";
                statusDiv.style.color = "#f85149";
                return;
            }

            try {
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-IN'; // Optimized for Indian English & Tenglish accents

                recognition.onstart = function() {
                    isListening = true;
                    statusDiv.innerHTML = "🔴 Listening... Speak now (English / Tenglish).";
                    statusDiv.style.color = "#f0883e";
                };

                recognition.onresult = function(event) {
                    var current = event.resultIndex;
                    var transcript = event.results[current][0].transcript;
                    transcriptDiv.innerHTML = "Heard: \\"" + transcript + "\\"";

                    // Try putting text into streamlit chat input if available
                    var textAreas = window.parent.document.querySelectorAll('textarea, input[type="text"]');
                    for (var i = 0; i < textAreas.length; i++) {
                        if (textAreas[i].placeholder && textAreas[i].placeholder.toLowerCase().includes('ask')) {
                            textAreas[i].value = transcript;
                            textAreas[i].dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                    }
                };

                recognition.onerror = function(event) {
                    statusDiv.innerHTML = "⚠️ Mic error: " + event.error + ". Check browser mic permissions.";
                    statusDiv.style.color = "#f85149";
                    isListening = false;
                };

                recognition.onend = function() {
                    isListening = false;
                    statusDiv.innerHTML = "✅ Finished listening. You can now press Send or Ask AI.";
                    statusDiv.style.color = "#3fb950";
                };

                recognition.start();
            } catch (err) {
                statusDiv.innerHTML = "⚠️ Mic initialization error: " + err.message;
                statusDiv.style.color = "#f85149";
            }
        }

        function stopSurakshaVoice() {
            if (recognition && isListening) {
                recognition.stop();
            }
        }

        function speakLastResponse() {
            if (!window.speechSynthesis) {
                alert("Text-to-speech is not supported by this browser.");
                return;
            }
            // Find the last assistant response text
            var assistantBubbles = window.parent.document.querySelectorAll('.chat-bubble-assistant');
            var textToSpeak = "SURAKSHA AI assistant is ready.";
            if (assistantBubbles.length > 0) {
                textToSpeak = assistantBubbles[assistantBubbles.length - 1].innerText;
            }
            var utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    </script>
    """, unsafe_allow_html=True)
