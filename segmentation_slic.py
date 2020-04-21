  
#from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage import segmentation
import matplotlib.pyplot as plt
import imageio

import cv2
import numpy as np
from IPython.display import HTML

# Load Video
video_path = "/Users/timschroder/Documents/Uni/Bachelorarbeit/project_data/DHF1K_25/002.AVI"
gif_save_path = "/Users/timschroder/Documents/Uni/Bachelorarbeit/Color_Segmentation/Code/Visualisierung/fly/TEST20.gif"

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
         standard_labels = standardise_labels_timeline(labels, start_at_end = True, count_offset = 1000)
         marked_merged = merge_background(standard_labels, images)
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
   
def standardise_labels_timeline(images_list, start_at_end = True, count_offset = 1000):
    """
    Replace labels on similar images to allow tracking over time

    :param images_list: a list of segmented and lablled images as numpy arrays
    :param start_at_end: relabels the images beginning at the end of the list
    :param count_offset: an int greater than the total number of expected labels in a single image
    :returns: a list of relablled images as numpy arrays
    """
    images = list(images_list)
    if start_at_end:
        images.reverse()

    # Relabel all images to ensure there are no duplicates
    for image in images:
        for label in np.unique(image):
            if label > 0:
                count_offset += 1
                image[image == label] = count_offset

    # Ensure labels are propagated through image timeline
    for i, image in enumerate(images):
        labels = get_labelled_centers(image)

        # Apply labels to all subsequent images
        for j in range(i, len(images)):
            images[j] = replace_image_point_labels(images[j], labels)

    if start_at_end:
        images.reverse()

    return images

def get_labelled_centers(image):
    """
    Builds a list of labels and their centers

    :param image: a segmented and labelled image as a numpy array
    :returns: a list of label, co-ordinate tuples
    """
    from skimage.measure import regionprops

    # Find all labelled areas, disable caching so properties are only calculated if required
    rps = regionprops(image, cache = False)

    return [(r.label, r.centroid) for r in rps]


def replace_image_point_labels(image, labels):
    """
    Replace the labelled at a list of points with new labels

    :param image: a segmented and lablled image as a numpy array
    :param labels: a list of label, co-ordinate tuples
    :returns: a relabelled image as a numpy array
    """
    img = image.copy()
    for label, point in labels:
        row, col = point
        # Find the existing label at the point
        index = img[int(row), int(col)]
        # Replace the existing label with new, excluding background
        if index > 0:
            img[img == index] = label

    return img

main()
