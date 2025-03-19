import numpy as np
import simpleaudio as sa
import random
import threading
import time
from transformers import pipeline

SAMPLE_RATE = 44100

NOTE_FREQUENCIES = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
    'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99
}

EMOTION_SCALES = {
    'happy': ['C4', 'D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5'],
    'sad': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'],
    'angry': ['D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5'],
    'relaxed': ['C4', 'D4', 'F4', 'G4', 'A4', 'C5', 'F5'],
    'excited': ['C4', 'D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5'],
    'mysterious': ['D4', 'F4', 'G4', 'A4', 'C5', 'E5', 'G5']
}

generator = pipeline("text-generation", model="gpt2")

def generate_ai_notes(emotion):
    prompt = f"Generate a {emotion} melody using musical notes:"
    output = generator(
        prompt,
        max_length=50,
        num_return_sequences=1,
        truncation=True,
        pad_token_id=50256
    )[0]['generated_text']

    notes = []
    scale = EMOTION_SCALES.get(emotion, list(NOTE_FREQUENCIES.keys()))
    
    for word in output.split():
        if word in scale:
            duration = random.uniform(0.3, 0.8)
            notes.append((word, duration))

    if not notes:
        notes = generate_random_notes(scale)

    return notes

def generate_random_notes(scale):
    return [(random.choice(scale), random.uniform(0.3, 0.8)) for _ in range(8)]

def generate_note(frequency, duration, amplitude=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)

    fade_out = np.linspace(1, 0, int(SAMPLE_RATE * 0.01))
    wave[-len(fade_out):] *= fade_out

    wave = (wave * 32767).astype(np.int16)
    return wave

def play_tune(notes):
    try:
        song = np.concatenate(
            [generate_note(NOTE_FREQUENCIES[note], duration) if note in NOTE_FREQUENCIES
             else np.zeros(int(SAMPLE_RATE * duration), dtype=np.int16)
             for note, duration in notes]
        )

        play_obj = sa.play_buffer(song, 1, 2, SAMPLE_RATE)
        time.sleep(0.1)  # Add small delay to avoid buffer locking
        play_obj.wait_done()

    except Exception as e:
        print(f"⚠️ Error during playback: {e}")

    finally:
        sa.stop_all()  # Clear audio buffer to avoid locking issues

