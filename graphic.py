from moviepy.editor import concatenate_videoclips, AudioFileClip, ImageSequenceClip, ImageClip
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import argparse
import shutil
import glob
import cv2
import os


parser = argparse.ArgumentParser(description='Crear video a partir de la imagen y audio.')
parser.add_argument('imagen', type=str, help='Imagen usada en la sonificación.')
parser.add_argument('audio', type=str, help='Audio obtenido en la sonificación.')
parser.add_argument('--color', type=str, default='white', help='Color de la curva.')
parser.add_argument('--dpi', type=int, default=100, help='Resolución del video.')

args = parser.parse_args()
name = args.imagen
mp3_audio = args.audio
color = args.color
dpi = args.dpi


# Carpeta donde se guardarán los archivos
path = '__tmp_images__'

if not os.path.exists(path):
    os.mkdir(path)
    
padding = 21

image = np.asarray(Image.open(name))[::-1, :, :]
height, width, _ = image.shape
canvas = np.pad(image, ((padding, padding), (0, 0), (0, 0)), 'constant')

scale = 2
image_big = cv2.resize(image, (width, height * scale))
image_big = image_big - np.min(image_big)
image_big = image_big / np.max(image_big)
height, width, _ = image_big.shape
x = np.arange(0, width)

images = []

# Generación de los frames
fig, ax = plt.subplots(dpi=dpi)
fig.patch.set_facecolor('xkcd:black')
ax.imshow(canvas, origin='lower')
ax.axis('off')
fig.tight_layout()
for i in tqdm(range(height)):
    y = image_big[i, :, 2]
    y = 20 * y + i / scale + padding
    curve = ax.plot(x, y, color=color)
    fig.canvas.draw()
    curve.pop(0).remove()

    buf = fig.canvas.tostring_rgb()
    ncols, nrows = fig.canvas.get_width_height()
    arr = np.fromstring(buf, dtype=np.uint8).reshape(nrows, ncols, 3)
    
    image_file = f"{path}/{str(i).zfill(4)}.png"
    images.append(image_file)
    cv2.imwrite(image_file, cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))

# Generación del video
audioclip = AudioFileClip(mp3_audio)

first = ImageClip(images[0])
first = first.set_duration(0.41)

last = ImageClip(images[-1])
last = last.set_duration(0.57)

sequence = ImageSequenceClip(images, fps=len(images) / (audioclip.duration - 0.41 - 0.57))

clip = concatenate_videoclips([first, sequence, last]).set_audio(audioclip)

name = mp3_audio.replace("mp3", "mp4")
clip.write_videofile(name)
shutil.rmtree(path)