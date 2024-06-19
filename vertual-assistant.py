import os
import subprocess
import speech_recognition as sr
import openai
from gtts import gTTS
import traceback

# Set your OpenAI API key
openai.api_key = ""

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        print("You said:", query)
        return query
    except sr.UnknownValueError:
        print("Sorry, I could not understand your audio.")
        return ""
    except sr.RequestError as e:
        print(f"Sorry, I could not request results from Google Speech Recognition service; {e}")
        return ""

# Function to generate avatar response (using OpenAI GPT-3.5-turbo)
def generate_avatar_response(query):
    try:
        # Debug: print the query being sent
        print(f"Sending query to OpenAI: {query}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )
        
        # Debug: print the raw API response
        print(f"OpenAI response: {response}")
        
        # Ensure the response content is correctly parsed
        response_content = response.choices[0].message['content'].strip()
        
        # Debug: print the parsed response content
        print(f"Parsed response content: {response_content}")
        
        return response_content
    except Exception as e:
        print(f"Error generating response from OpenAI: {e}")
        return "Sorry, I'm having trouble generating a response right now."

# Function to convert text to speech
def text_to_speech(text, filename="response.mp3"):
    tts = gTTS(text=text, lang="en",tld="co.za")
    tts.save(filename)
    return filename

# Function to create lip-synced video with Wav2Lip
def create_lip_synced_video(source_image_path, audio_path, output_video_path):
    checkpoint_path = "checkpoints/wav2lip_gan.pth"
    try:
        print(f"Loading model from {checkpoint_path}...")
        # Check if the checkpoint file is valid
        with open(checkpoint_path, 'rb') as f:
            magic_number = f.read(10)
            print(f"Checkpoint magic number: {magic_number}")
        
        command = [
            'python', 'inference.py',
            '--checkpoint_path', checkpoint_path,
            '--face', source_image_path,
            '--audio', audio_path,
            '--outfile', output_video_path
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating lip-synced video: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"General error: {e}")
        traceback.print_exc()

# Main loop for the video chat system
while True:
    # Listen for user query
    query = recognize_speech()

    # Generate avatar response
    response = generate_avatar_response(query)

    # Convert response to speech
    response_audio = text_to_speech(response)

    # Specify paths for avatar image and output video
    source_image_path = "Queen_Elizabeth_II_of_New_Zealand.jpg"
    output_video_path = "output_video.mp4"

    # Create lip-synced video
    create_lip_synced_video(source_image_path, response_audio, output_video_path)

    # Play response audio
    os.system("mpg321 " + response_audio)

    # Break the loop if the query is empty 
    if not query:
        break

