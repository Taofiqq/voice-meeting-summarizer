from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

@app.route('/')
def index():
    return "Voice Meeting Summarizer is running!"

@app.route('/join-conference', methods=['POST'])
def join_conference():
    """Handle incoming calls and add them to conference"""
    logger.info("========= Conference Joined =========")
    response = VoiceResponse()
    
    # Create a dial element
    dial = Dial()
    
    dial.conference(
        'MeetingRoom',
        startConferenceOnEnter=True,      # Correct attribute name
        endConferenceOnExit=False,        # Correct attribute name
        record=True,
        recordingStatusCallback='https://voice-meeting-summarizer.onrender.com/recording-callback',
        recordingStatusCallbackEvent='in-progress completed',
        recordingStatusCallbackMethod='POST',
        statusCallback='https://voice-meeting-summarizer.onrender.com/conference-status',
        statusCallbackEvent='start end join leave',
        statusCallbackMethod='POST',
        waitUrl='http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical',
        beep=True,
        muted=False
    )
    
    logger.info("Generated TwiML: %s", str(response))

    
    response.append(dial)
    return Response(str(response), mimetype='text/xml')

@app.route('/recording-callback', methods=['POST'])
def recording_callback():
    """Handle recording status callbacks"""
    
    logger.info("========= Recording Callback Received =========")
    
    # Log all incoming data from Twilio
    logger.info(f"All callback data: {request.values.to_dict()}")
    
    recording_url = request.values.get('RecordingUrl')
    recording_sid = request.values.get('RecordingSid')
    recording_status = request.values.get('RecordingStatus')  # Added this
    
    logger.info(f"Recording Status: {recording_status}")
    logger.info(f"Recording URL: {recording_url}")
    logger.info(f"Recording SID: {recording_sid}")
    
    # More detailed logging
    if recording_url:
        logger.info("Recording URL received successfully")
    else:
        logger.warning("No recording URL in callback")
        
    logger.info("========= Recording Callback Completed =========")
    
    return "OK"

@app.route('/conference-status', methods=['POST'])
def conference_status():
    """Handle conference status callbacks"""
    logger.info("========= Conference Status =========")
    conference_sid = request.values.get('ConferenceSid')
    event_type = request.values.get('StatusCallbackEvent')
    
    logger.info("=== conference id====", conference_sid)
    logger.info(" ===event type ===", event_type)
    
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5005))