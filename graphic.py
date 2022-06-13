from PIL import Image
from moviepy.editor import concatenate_videoclips, AudioFileClip, ImageSequenceClip, ImageClip
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import shutil
import glob
import os
import cv2

fig = plt.figure()
fig.patch.set_facecolor('xkcd:black')

padding = 21

path = 'images'

    
for name in glob.glob("*.tif")[1:]:
    # Creating images path
    if not os.path.exists(path):
        os.mkdir(path)
        
    
    image = np.asarray(Image.open(name))
    height, width, _ = image.shape
    canvas = np.pad(image, ((padding, padding), (0, 0), (0, 0)), 'constant')

    scale = 2
    image_big = cv2.resize(image, (width, height * scale))
    image_big = image_big - np.min(image_big)
    image_big = image_big / np.max(image_big)
    height, width, _ = image_big.shape
    x = np.arange(0, width)

    images = []

    for i in tqdm(range(height)):
        plt.imshow(canvas, origin='lower')
        y = image_big[i, :, 2]
        y = 20 * y + i / scale + padding
        plt.plot(x, y, color='white')
        plt.axis('off')

        image_file = f"{path}/{str(i).zfill(4)}.png"
        plt.savefig(image_file, bbox_inches='tight', dpi=250)
        images.append(image_file)
        plt.clf()

    mp3_audio = name.replace("tif", 'mp3')
    print(mp3_audio)
    audioclip = AudioFileClip(f"{mp3_audio}")

    first = ImageClip(images[0])
    first = first.set_duration(0.41)

    last = ImageClip(images[-1])
    last = last.set_duration(0.57)

    sequence = ImageSequenceClip(images, fps=len(images) / (audioclip.duration - 0.41 - 0.57))

    clip = concatenate_videoclips([first, sequence, last]).set_audio(audioclip)

    name = mp3_audio.replace("mp3", "mp4")
    print(name)
    clip.write_videofile(f"{name}")
    shutil.rmtree(path)



    

