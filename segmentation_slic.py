#from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage import segmentation
import matplotlib.pyplot as plt
import imageio

import cv2
import numpy as np
from IPython.display import HTML

# Load Video
video_path = "/Users/timschroder/Documents/Uni/Bachelorarbeit/Data.nosync/DHF1K_25/002.AVI"
gif_save_path = "/Users/timschroder/Documents/Uni/Bachelorarbeit/Color_Segmentation/Code/Visualisierung/fly/TEST.gif"

def main():
    n_frames = 25
    n_segments = 1500
    compactness = 80
    labels, markes_boundries = segment_video(video_path, n_frames, n_segments, compactness)
    save_gif(markes_boundries, gif_save_path)
    
def segment_video(path, n_frames, n_segments, compactness):
    markes_boundries = []
    superpixels = []
    labels = []

    vidcap = cv2.VideoCapture(path) 
    success,image = vidcap.read()
    count = 0
    
    while success and count < n_frames:
        
        #SLIC
        label = segmentation.slic(image, compactness=compactness, n_segments=n_segments, convert2lab = True)
        labels.append(label)
        
        # Yellow Grid Boundries
        marked = mark_boundaries(image, label) 
        markes_boundries.append(marked)
    
        # Label to RGB Boundries
        #out = color.label2rgb(label, image, kind='avg') #commment if not needed
        #superpixels.append(out)
        
        # next frame
        success, image = vidcap.read() 
        count += 1
        print('finished %s frames' % count)
        
    return labels, markes_boundries #,superpixels
    
def save_gif(img_list, gif_save_path):
    
    img_list = np.asarray(img_list)
    int_images = []
    for i in range (0, len(img_list)):
        data = img_list[i]
        #info = np.iinfo(data.dtype) # Get the information of the incoming image type
        data = data.astype(np.float64) / np.amax(data) # normalize the data to 0 - 1
        data = 255 * data # Now scale by 255
        int_img = data.astype(np.uint8)
        int_images.append(int_img)
                          
    imageio.mimsave(gif_save_path, int_images,fps=10)
    #HTML(gif_save_path)
   

main()