'''
    Script or program to calibrate the images overlap. can calibrate 2 images at a time. out of 2, one is considered stationary, reference. 

    usage : this script <images path seperated with commas> <yml info save path> <image_2_side {default : right }
        first image path should be one with that is constant. 

    images it takes is after bird eyed view images. 
    
'''


import numpy as np 
import cv2
import sys 
import argparse
import os 

HEIGHT = 720
WIDTH = 1280
STEP = int(1)
SCALE_STEP = float(0.01)



for i in range(len(sys.argv)):
    print("{} -> {}".format(i, sys.argv[i]))

exit(0)

# reading the image and files
front_transformed = cv2.imread (sys.argv[1])
side_transformed = cv2.imread(sys.argv[2])
save_file_path = sys.argv[3]
side = sys.argv[4] if len(sys.argv) > 4 else "right"
fs = cv2.FileStorage(save_file_path, cv2.FILE_STORAGE_WRITE)


center_img2_rotation = [0,0]
angle = 0
side_off = 0

scale_img2 = float(1)
scale_img1 = float(1)

# offsets [x,y]
img1_offsets = [0,0]
img2_offsets = [0,0]

front_img_resized = np.zeros((HEIGHT, WIDTH, 3)).astype(front_transformed.dtype)
front_img_resized[0:front_transformed.shape[0], 0 : front_transformed.shape[1], :] = front_transformed

print_info = True
while 1:


    canvas_img2 = np.zeros((HEIGHT, WIDTH, 3)).astype(front_transformed.dtype)
    canvas_img1 = np.zeros((HEIGHT, WIDTH, 3)).astype(front_transformed.dtype)

    # below code will show the center of rotation for image 2 part 
    circle_img = side_transformed.copy()
    cv2.circle (circle_img, center_img2_rotation, 5, (255,0,0), 2)

    # below will rotate the image 2 with chosen center and at given scale. 
    rotation_matrix = cv2.getRotationMatrix2D(center_img2_rotation, angle, scale_img2)
    rotated_image = cv2.warpAffine(side_transformed, rotation_matrix, (WIDTH, HEIGHT))


    key = cv2.waitKey(1)
    if key == 27:
        break


    # moving the circle
    if key == ord('u') or key == ord('i') or key == ord('o') or key == ord('p'):
        if key == ord('i') and center_img2_rotation[1] > 0:
            center_img2_rotation[1] -= STEP
        elif key == ord('o') and center_img2_rotation[1] < side_transformed.shape[0]:
            center_img2_rotation[1] += STEP
        elif key == ord('p') and center_img2_rotation[0] < side_transformed.shape[1]:
            center_img2_rotation[0] += STEP
        elif key == ord('u') and center_img2_rotation[0] > 0:
            center_img2_rotation[0] -= STEP

        print_info = True
 

    # rotating and scaling of the second image. 
    if key == ord('n') or key == ord('m') or key == ord('=') or key == ord('-'):
        if key == ord('n'):
            angle -= STEP
        elif key == ord('m'):
            angle += STEP
        elif key == ord('='):
            scale_img2 += SCALE_STEP
        elif key == ord('-'):
            scale_img2 -= SCALE_STEP

        print_info = True

    # movement of second image 
    if key == ord('a') or key == ord('s') or key == ord('d') or key == ord('f'):
        if key == ord('s') and img2_offsets[1] > 0:
            img2_offsets[1] -= 1
        elif key == ord('d'):
            img2_offsets[1] += 1
        elif key == ord('a') and img2_offsets[0] > 0:
            img2_offsets[0] -= 1
        elif key == ord('f'):
            img2_offsets[0] += 1
        print_info = True

    canvas_img2[img2_offsets[1]:, img2_offsets[0] :, : ] = rotated_image[0: HEIGHT - img2_offsets[1], 0: WIDTH - img2_offsets[0], :]


    # movement of image 1
    if key == ord('q') or key == ord('w') or key == ord('e') or key == ord('r') or key == ord('1') or key == ord('2'):
        if key == ord('w') and img1_offsets[1] > 0:
            img1_offsets[1] -= 1
        elif key == ord('e'):
            img1_offsets[1] += 1
        elif key == ord('q') and img1_offsets[0] > 0:
            img1_offsets[0] -= 1
        elif key == ord('r'):
            img1_offsets[0] += 1
        elif key == ord('1') and scale_img1 > 0:
            scale_img1 -= SCALE_STEP
        elif key == ord('2') and scale_img1 < 1:
            scale_img1 += SCALE_STEP
        print_info = True
    
    scaled_img1 = cv2.resize(front_img_resized, None, fx=scale_img1, fy=scale_img1)
    rescale_img1 = np.zeros((HEIGHT, WIDTH, 3)).astype(scaled_img1.dtype)
    
    rescale_img1[0: scaled_img1.shape[0], 0 : scaled_img1.shape[1], :] = scaled_img1
    canvas_img1[img1_offsets[1]:, img1_offsets[0] :, : ] = rescale_img1[0: HEIGHT - img1_offsets[1], 0: WIDTH - img1_offsets[0], :]


    final = cv2.add (canvas_img1, canvas_img2)
    cv2.imshow("circle coordinate", circle_img)
    cv2.imshow("final canvas ", final)


    
    if print_info:
        print("center : {} | angle : {} | scale img2 : {} | scale img 1 : {}".format(center_img2_rotation, angle, scale_img2, scale_img1))
        print_info = False


# saving information of image 1 
fs.write ("canvas_size", np.array([HEIGHT, WIDTH]))
# image 1 offsets in canvas 
fs.write("image1_offsets", np.array(img1_offsets))
fs.write("image1_scale", scale_img1)

# image 2 params 
fs.write("image2_offsets", np.array(img2_offsets))
fs.write("image2_scale", scale_img2)
fs.write("image2_rotate_angle", angle)
fs.write("image2_rotate_center", np.array(center_img2_rotation))
fs.write("image2_side", 1 if side == 'right' else 0)
fs.release()

cv2.destroyAllWindows()
