''' 
Calibrate the blending onto an image. 
    script format : arg_1 = image_path 



    CONTROLS: 
        Quit                    : Esc
        translation             : 'q' : left | 'w' : up | 'e' : down | 'r' : right 
        change point            : space 
        clean blending          : 'c'
        get out of clean blend  : Esc


'''


import numpy as np 
import cv2
import sys 
import argparse
import os 

PIXEL_STEP = 5


def parse_yml(yml_path, img_list_len):
    fs = cv2.FileStorage (yml_path, cv2.FILE_STORAGE_READ)
    # reading the attributes 
    attr = dict() 

    canvas_size = fs.getNode('CANVAS SIZE').mat()[:,0].tolist()
    attr['canvas_size'] = canvas_size

    for i in range(img_list_len):
        x = "img{}".format(i)
        for s in ["_rotate_center", "_rotate", "_scale", "offset"]:
            y = x + s
            if s in ["_rotate", "offset"]:
                attr[y] = fs.getNode(y).mat()[:,0].tolist()
                
            else:
                attr[y] = fs.getNode(y).real()
    return attr


def parse_name():
    if len(sys.argv) < 2:
        print("give image path as argument \n")
        exit(0)
    
    # reading image into a list 
    image_paths = sys.argv[1].split(',')
    image_list = []
    image_name_list = []
    for each_path in image_paths:
        
        if os.path.exists(each_path) == False:
            print("invalid path : {}".format(each_path))
            exit(0)
        img = cv2.imread(each_path)
        if type(img) == type(None):
            print("could not read image from path : {} ".format(each_path))
            exit(0)
        image_list.append(img)
        image_name_list.append(each_path.split('/')[-1])

    if os.path.exists(sys.argv[2]) == False:
        print("invalid YML path used : {}".format(sys.argv[2]))
        exit(0)

    yml_dict = parse_yml (sys.argv[2], len(image_list))

    return image_list, image_name_list, yml_dict

def generate_canvases(image_array, yml_data):
    canvases = np.zeros(( image_array.shape[0], HEIGHT, WIDTH, image_array.shape[-1])).astype(np.uint8)
    for i in range(canvases.shape[0]):

        strx = "img{}".format(i)
        # rotation 
        rotate_center = yml_data[strx + "_rotate"]
        rotate_angle = yml_data[strx + "_rotate_center"]
        scale = yml_data[strx + "_scale"]
        
        # rotate image 
        rot_matrix = cv2.getRotationMatrix2D(rotate_center, rotate_angle, scale)
        rotated_image = cv2.warpAffine(image_array[i].copy(), rot_matrix, yml_data['canvas_size'])

        # translation 
        offset = yml_data[strx + "offset"]
        canvases[i, offset[1] : , offset[0] : , : ] = rotated_image[0: HEIGHT - offset[1], 0 : WIDTH - offset[0], :].copy()

    return canvases


if __name__ == "__main__":
    image_list, image_name_list, yml_data = parse_name()
    WIDTH, HEIGHT = yml_data['canvas_size'] 
    print(HEIGHT, WIDTH)
    print("image_names : {}".format(image_name_list))
    image_array = np.array(image_list)
    image_canvases = generate_canvases (image_array, yml_data)

    # defining x1, x2, x3, x4
    points = np.array([[ 10, 10], [10, HEIGHT - 10], 
        [100, 10], [100, HEIGHT - 10]])

    circle_selected = 0
    clean  = False 
    add_blend_region = True

    blends_dict = dict()
    for name in image_name_list:
        blends_dict[name] = list()

    while True:
        
        key = cv2.waitKey(1)
        
        canvas = np.zeros((HEIGHT, WIDTH, 3)).astype(np.uint8)
        for i in range(image_canvases.shape[0]):
            canvas = cv2.add(image_canvases[i], canvas)   

        if key == ord('a'): # Add new set of canvas 
            add_blend_region = True

        if add_blend_region:
            os.system('clear')
            print("Enter the image you want to add blending for : Press the corresponding number")
            print("\n=============================================================================\n")
            for i, _name in enumerate(image_name_list):
                print("{} : {}".format(i, _name))
            print("\n=============================================================================\n")
            choice = int(input())
            add_blend_region = False
            

        ########################## keys and command define part #################################
        if key == 27:
            break

        if key == 32:
            circle_selected = (circle_selected + 1) if circle_selected < 3 else 0
        
        if key == ord ('q') or key == ord('w') or key == ord('e') or key == ord('r'):
            if key == ord('q') and points[circle_selected, 0] > 0:
                points[circle_selected, 0] -= PIXEL_STEP
            elif key == ord('w') and points[circle_selected, 1] > 0:
                points[circle_selected, 1] -= PIXEL_STEP
            elif key == ord('e') and points[circle_selected, 1] < HEIGHT:
                points[circle_selected, 1] += PIXEL_STEP
            elif key == ord('r') and points[circle_selected, 0] < WIDTH:
                points[circle_selected, 0] += PIXEL_STEP
        
        if key == ord('c'):
            clean = True
        


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
            b01 = points[1, 1] - m01 * points[1,0]
            

            for y in range(blended_canvas.shape[0]):
                for x in range(blended_canvas.shape[1]):
                    if y < m32 * x + b32:
                        blended_canvas[y, x, :] = [1, 1, 1]
                    if y > m01 * x + b01:
                        blended_canvas[y, x, :] = [1, 1, 1]
            
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

        if clean:
            if (cv2.waitKey(0) == 27): # press x
                    clean = False


    cv2.destroyAllWindows()

