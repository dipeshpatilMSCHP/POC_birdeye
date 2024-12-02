import numpy as np
import cv2
import matplotlib.pyplot as plt


img1 = cv2.imread('/home/dipesh/projects/Demo/perspective-trasnform/cpp-files/seamlessStiching/dump/front-transformed_img.jpg')
img2 = cv2.imread('/home/dipesh/projects/Demo/perspective-trasnform/cpp-files/seamlessStiching/dump/sidee.jpg')

# reading the file for info 
fs = cv2.FileStorage ('/home/dipesh/projects/Demo/perspective-trasnform/python/scripts/dumped_data/calibrate.yml', cv2.FILE_STORAGE_READ)


# rotating the image 2 
center = fs.getNode('img2_rotate_center').mat()
print(center)
center = center[:,0]

# rotation angle 
angle = fs.getNode ('img2_rotate').real()

# scale 
scale = fs.getNode('img2_scale').real()

# get rotation matrix and rotate the image 2
rot_mat = cv2.getRotationMatrix2D (center, angle, scale)
rotated_img2 = cv2.warpAffine (img2, rot_mat, (1280, 720))

# extracting the offsets
img2_x_offset = int(fs.getNode('img2_x_offsets').real())
img2_y_offset = int(fs.getNode('img2_y_offsets').real())


x0 = 450 
x1 = 625


# generating the masks
mask_img_1 = np.ones((720, 1280, 3))
mask_img_2 = np.ones((720, 1280, 3))

# generating the image 1 alpha blend 
img1_alpha = np.linspace(1,0, x1 - x0)
img1_alpha = np.tile(img1_alpha, (3,720, 1))
img1_alpha = np.moveaxis (img1_alpha, 0, -1)

# generating the image 2 alpha blend
img2_alpha = np.linspace(0,1, x1 - x0)
img2_alpha = np.tile(img2_alpha, (3,720, 1))
img2_alpha = np.moveaxis (img2_alpha, 0, -1)

mask_img_1[:, x0:x1, :] = mask_img_1[:, x0:x1, :] * img1_alpha
mask_img_2[:, x0:x1, :] = mask_img_2[:, x0:x1, :] * img2_alpha

_mask_img_2 = mask_img_2.copy()

# readying the image 1 and image 2
canvas_img1 = np.zeros((720, 1280, 3)).astype(np.uint8)
canvas_img1[100: img1.shape[0] + 100,: img1.shape[1],:] = img1

canvas_img2 = np.zeros((720, 1280, 3)).astype(np.uint8)
canvas_img2[img2_y_offset:, img2_x_offset : ,:] = rotated_img2 [0:720 - img2_y_offset, 0:1280 - img2_x_offset, :]

point1 = [x1, 0] # (630, 0)
point2 = [x0, 720] # (450, 0)


calculate_params = True
while (1):

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
    # point 1 controls 
    if key == ord('w') or key == ord('e') or key == ord('r') or key == ord('t'):
        if key == ord('w') and point1[0] > 0:
            point1[0] -= 1
        elif key == ord('e') and point1[1] > 0:
            point1[1] -= 1
        elif key == ord('r') and point1[1] < 720:
            point1[1] += 1
        elif key == ord('t') and point1[0] < 1280:
            point1[0] += 1
        calculate_params = True

    # point 2 control 
    if key == ord('u') or key == ord('i') or key == ord('o') or key == ord('p'):
        if key == ord('u') and point2[0] > 0:
            point2[0] -= 1
        elif key == ord('i') and point2[1] > 0:
            point2[1] -= 1
        elif key == ord('o') and point2[1] < 720:
            point2[1] += 1
        elif key == ord('p') and point2[0] < 1280:
            point2[0] += 1
        calculate_params = True

    if calculate_params:
        print("point_1 : {} | point_2 : {}".format(point1, point2))
        m = (point2[1] - point1[1]) /  (point2[0] - point1[0])
        b = point2[1] - m * point2[0]
    
        mask_img_2 = _mask_img_2.copy()
        for i in range(mask_img_2.shape[0]):
            for j in range(mask_img_2.shape[1]):
                if i > (m * j + b):
                    mask_img_2[i,j,:] = [1,1,1]

        _canvas_img_1 = canvas_img1.copy()
        _canvas_img_2 = canvas_img2.copy()

        _canvas_img_1 = (_canvas_img_1 * mask_img_1).astype(_canvas_img_1.dtype)
        _canvas_img_2 = (_canvas_img_2 * mask_img_2).astype(_canvas_img_2.dtype)
        calculate_params = False

        final_canvas = cv2.add (_canvas_img_1, _canvas_img_2)
    cv2.circle(final_canvas, point1, 5, (255, 0, 0), 1)
    cv2.circle(final_canvas, point2, 5, (0, 255, 0), 1)
    
    cv2.imshow("final canvas", final_canvas)
    
cv2.destroyAllWindows()