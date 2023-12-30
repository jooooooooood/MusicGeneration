import json
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import torch


def generate_audio(genres):
    # Set the path to the directory containing the ffmpeg executable
    ffmpeg_path = r'C:\Users\mclar\Downloads\ffmpeg\ffmpeg\bin\ffmpeg.exe'

    model = MusicGen.get_pretrained("facebook/musicgen-medium", device='cuda')
    model.set_generation_params(duration=2)

    print_gpu_usage()

    print(genres)
    print("A song with influences that includes " + ', '.join(genres))
    
    description = "A song with influences that includes " + ', '.join(genres)

    wav = model.generate([description])

    for idx, one_wav in enumerate(wav):
        song = audio_write(f'static/audio/test_{idx}', one_wav.cpu(), model.sample_rate, strategy="loudness")
    
    return song


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