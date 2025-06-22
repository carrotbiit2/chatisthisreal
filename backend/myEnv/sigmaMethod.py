import cv2
from runModel import runModel
import random
from tqdm import tqdm

def runVideo(videoPath,numFrames):
    frames=[]
    capture=cv2.VideoCapture(videoPath)
    while True:
        ret, frame = capture.read()#ret is True if a frame was read
        if not ret:
            break#No more frames, exit the loop
        frames.append(frame)#Save the frame in our list
    capture.release()
    randomFrames=random.sample(frames,numFrames)
    
    avgAiScore=0
    for frame in tqdm(randomFrames):
        cv2.imwrite("tempFrame.png",frame)
        avgAiScore+=runModel("tempFrame.png")
    return avgAiScore/numFrames