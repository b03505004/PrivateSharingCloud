import socket
import requests
import cv2
import numpy as np
import pyaudio
import wave
import time
import moviepy.editor as mp
HOST = 'localhost'
PORT = 8787
ADDR = (HOST,PORT)
BUFSIZE = 4096
videofile = "./static/walk.mp4"



print("-----! 使用q键关闭 !-----")
video_fps = 30
# -------------------------audio-----------------------------
FORMAT = pyaudio.paInt32 
CHANNELS = 1
RATE = 44100
CHUNK = int(RATE/video_fps)
WAVE_OUTPUT_FILENAME = "audio.wav"
audio = pyaudio.PyAudio()
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
frames = []
#stream.start_stream()
cap = cv2.VideoCapture(0)
out = cv2.VideoWriter('video.mp4',cv2.VideoWriter_fourcc(*'MP4V'), video_fps, (int(cap.get(3)),int(cap.get(4))))
# -------------------------video-----------------------------

try:
    #分別錄製聲音與影片
    while(True):
        # audio
        data = stream.read(CHUNK)
        frames.append(data)
        # video
        ret, frame = cap.read()
        if ret == True:
            out.write(frame)
            cv2.imshow('frame',frame)
        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    stream.stop_stream()
    stream.close()
    audio.terminate()
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    cap.release()
    out.release()
    cv2.destroyAllWindows()

except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    audio.terminate()
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    cap.release()
    out.release()
    cv2.destroyAllWindows()

audio = mp.AudioFileClip("audio.wav")
video = mp.VideoFileClip("video.mp4")

print(video.duration, audio.duration)
#將音訊視訊欓結合
audio = audio.set_start((video.duration-audio.duration))
final = video.set_audio(audio)
final.write_videofile("combined.mp4")



bytesvid = open("combined.mp4", 'rb').read()
print ("视频大小(位元组):", len(bytesvid))
print("请输入存活时间(秒):")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#讓使用者輸入影片存活時間與告知使用者影片ID
ttl = input()
client.send(str.encode(ttl))
client.send(bytesvid)
time.sleep(3)
client.send(str.encode("DONE"))
print('finished')
time.sleep(3)
ID = client.recv(4096)
print('Your video ID:', ID.decode())
print('可至视频浏览页面观赏!!')
client.close()
