import json
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

def generate_audio():
    # Set the path to the directory containing the ffmpeg executable
    ffmpeg_path = r'C:\Users\mclar\Downloads\ffmpeg\ffmpeg\bin\ffmpeg.exe'

    model = MusicGen.get_pretrained("facebook/musicgen-medium", device='cuda')
    model.set_generation_params(duration=30)


# In your generate_audio function:
    with open('top_genres.json', 'r') as f:
        descriptions = json.load(f)

    print(descriptions)

    print_gpu_usage()

    print(["A " + descriptions[0] + " song with " + descriptions[1] + " and " + descriptions[2] + " influence"])

    wav = model.generate(["A " + descriptions[0] + " song with " + descriptions[1] + " and " + descriptions[2] + " influence"])

    for idx, one_wav in enumerate(wav):
        song = audio_write(f'static/audio/test_{idx}', one_wav.cpu(), model.sample_rate, strategy="loudness")
    
    return song

import torch

def print_gpu_usage():
    if torch.cuda.is_available():
        print('GPU Usage:')
        for i in range(torch.cuda.device_count()):
            current_device = torch.cuda.device(i)
            memory_allocated = torch.cuda.memory_allocated(i) / 1e9  # Convert bytes to GB
            memory_cached = torch.cuda.memory_reserved(i) / 1e9  # Convert bytes to GB
            print(f'Device {i}: {current_device}, Memory Allocated: {memory_allocated}GB, Memory Cached: {memory_cached}GB')
    else:
        print('No GPU available.')