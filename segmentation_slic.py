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
gif_save_path = "/Users/timschroder/Documents/Uni/Bachelorarbeit/Color_Segmentation/Code/Visualisierung/fly/TEST2.gif"

def main():
    n_frames = 10
    n_segments = 1000
    compactness = 80
    merge_bg = True #Set True to merge Background pixels to 0
    labels, marked_boundries = segment_video(video_path, n_frames, n_segments, compactness, merge_bg)
    save_gif(marked_boundries, gif_save_path)
    
def segment_video(path, n_frames, n_segments, compactness, merge_bg):
    marked_boundries = []
    superpixels = []
    labels = []
    images = []

    vidcap = cv2.VideoCapture(path) 
    success,image = vidcap.read()
    count = 0
    
    while success and count < n_frames:
        
        images.append(image)
        #SLIC
        label = segmentation.slic(image, compactness=compactness, n_segments=n_segments, convert2lab = True)
        labels.append(label)
        
        # Yellow Grid Boundries
        marked = mark_boundaries(image, label) 
        marked_boundries.append(marked)
    
        # Label to RGB Boundries
        #out = color.label2rgb(label, image, kind='avg') #commment if not needed
        #superpixels.append(out)
        
        # next frame
        success, image = vidcap.read() 
        count += 1
        print('SLIC segmentation - frame %s' % count)
        
    


    if merge_bg:
         marked_merged = merge_background(labels, images)
         return labels, marked_merged
     
    else:
        return labels, marked_boundries #,superpixels
        
         
    
    
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
    
def merge_background(label_list, image_list):
    st = np.array(label_list)+1 #shift '0'-label to 1
    back_label = []
    
    
    for t in range (0,len(st)-1):
        back_pixel = np.ones(st[t].shape)
        print('merge background - frame %s' % t)
        for i in range(0,len(np.unique(st[t]))-1):
            condition_1 = (st[t] == np.unique(st[t])[i])
            condition_2 = (st[t+1] == np.unique(st[t])[i])
            if np.array_equal(condition_1, condition_2):
                back_pixel[st[t] == np.unique(st[t])[i]] = 0
        
        merged_label = st[t]*back_pixel
        merged_label = np.int64(merged_label)
        marked = mark_boundaries(image_list[t], merged_label)
        back_label.append(marked)
    
    back_label = back_label[:-1]
    return back_label
   

main()
