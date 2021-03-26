import os
import moviepy.editor as mp
archivos = [x[:-4] for x in os.listdir() if x[-4:] == '.gif']
print(archivos)
for archivo in archivos:
    print('Transformando', {archivo})
    clip = mp.VideoFileClip(f"{archivo}.gif")
    clip.write_videofile(f"{archivo}.mp4")
