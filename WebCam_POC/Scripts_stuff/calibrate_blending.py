''' 
Calibrate the blending onto an image. 
    script format : arg_1 = image_path 

'''


import numpy as np 
import cv2
import sys 
import argparse
import os 

if len(sys.argv) < 1:
    print("give image path as argument \n")
    exit(0)

img = cv2.imread(sys.argv[1])
HEIGHT, WIDTH = img.shape[:2]
print(HEIGHT, WIDTH, img.shape)

# defining x1, x2, x3, x4
points = np.array([[ 10, 10], [10, HEIGHT - 10], 
    [100, 10], [100, HEIGHT - 10]])

circle_selected = 0
clean  = False 
reset = False
while True:
    canvas = img.copy()


    key = cv2.waitKey(1)
    
    ########################## keys and command define part #################################
    if key == 27:
        break

    if key == 32:
        circle_selected = (circle_selected + 1) if circle_selected < 3 else 0
    
    if key == ord ('q') or key == ord('w') or key == ord('e') or key == ord('r'):
        if key == ord('q') and points[circle_selected, 0] > 0:
            points[circle_selected, 0] -= 1
        elif key == ord('w') and points[circle_selected, 1] > 0:
            points[circle_selected, 1] -= 1
        elif key == ord('e') and points[circle_selected, 1] < HEIGHT:
            points[circle_selected, 1] += 1
        elif key == ord('r') and points[circle_selected, 0] < WIDTH:
            points[circle_selected, 0] += 1
    
    if key == ord('c') or key == ord('x'):
        if key == ord('c'):
            clean = True
        else:
            reset = True
    


    #########################################################################################
    
   
    

    #################################### final drawing part #################################
    x_min = np.min(points[:2, 0])
    x_max = np.max(points[2:, 0])

    # generating the blended area 

    blended_area = np.linspace(0,1, x_max - x_min)
    blended_area = np.tile( blended_area, (3, HEIGHT, 1) )
    blended_area = np.moveaxis(blended_area, 0, -1)

    blended_canvas = np.ones (canvas.shape).astype(np.float32)
    blended_canvas[:, x_min : x_max] = blended_area

    ################################## calculation ##########################################
    if clean:

        m32 = (points[3, 1] - points[2, 1]) / (points[3, 0] - points[2, 0])
        b32 = points[3, 1] - m32 * points[3,0]

        m01 = (points[1, 1] - points[0, 1]) / (points[1, 0] - points[0, 0])
        b01 = points[1, 1] - m32 * points[1,0]

        for y in range(blended_canvas.shape[0]):
            for x in range(blended_canvas.shape[1]):
                if y > m32 * x + b32:
                    blended_canvas[y, x, :] = [1, 1, 1]
                if y < m01 * x + b01:
                    blended_canvas[y, x, :] = [1, 1, 1]
                
        clean = False


    canvas = cv2.multiply (canvas.astype(np.float32), blended_canvas).astype(np.uint8)

    # drawing the lines 
    cv2.line (canvas, points[0], points[1], (0, 0, 255), 1)
    cv2.line (canvas, points[2], points[3], (0, 0, 255), 1)

    # drawing the circles
    for i in range(4):
        if i == circle_selected:
            cv2.circle (canvas, points[i], 5, (255, 255, 0), 3)
        else:
            cv2.circle (canvas, points[i], 5, (0, 255, 0), 2)
    ######################################################################################
    # display the canvas
    cv2.imshow("canvas", canvas)

cv2.destroyAllWindows()

