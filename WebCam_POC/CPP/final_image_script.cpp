#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

#define STEP_SIZEE 1
#define STEP_SIZE 1


Mat rotateImage(const Mat& src, double angle, double scale, const Mat& center_rotate) {
	
	Point2f center(center_rotate.at<int>(0),center_rotate.at<int>(1));
	Mat rotMat = getRotationMatrix2D(center, angle, scale);

	Mat dst;
	warpAffine(src, dst, rotMat, Size(1280,720));
	return dst;
}

/*Mat blendImages(const Mat& img1, const Mat& img2, const Mat& img3, int off_x1, int off_y1, int off_x2, int off_y2
		int off_x3, int off_y3, int canvas_width, int canvas_height) {

	int w1 = img1.cols;
	int h1 = img1.rows;
	int w2 = img2.cols;
	int h2 = img2.rows;
	int w3 = img3.cols;
	int h3 = img3.rows;

	// Calculate the canvas size to hold both images, considering the offsets
	int c1 = canvas_width;  
	int c2 = canvas_height;  

	// Create an empty canvas with black background
	Mat canvas1(Size(c1, c2), img1.type(), Scalar(0, 0, 0));
	Mat canvas2(Size(c1, c2), img1.type(), Scalar(0, 0, 0));
	Mat canvas3(Size(c1, c2), img1.type(), Scalar(0, 0, 0));

	Mat canvas4(Size(c1, c2), img1.type(), Scalar(0, 0, 0));

	// Place img1 on the canvas at (off_x1, off_y1)
	Mat roi1 = canvas1(Rect(off_x1, off_y1, w1, h1));
	img1.copyTo(roi1);

	// Place img2 on the canvas at (off_x2, off_y2)
	Mat roi2 = canvas2(Rect(off_x2, off_y2, w2, h2));
	img2.copyTo(roi2);

	Mat roi3 = canvas3(Rect(off_x3, off_y3, w3, h3));
	img3.copyTo(roi3);
	
	imwrite("f1.jpg",canvas1);
	imwrite("f2.jpg",canvas2);
	imwrite("f3.jpg",canvas3);
	
	add(canvas1,canvas2,canvas2);
	add(canvas2,canvas3,canvas4);

	return canvas4;
}*/

int main(int argc, char **argv) {

	if(argc < 8){
		cout << "Usage: ./main <img-1> <img-1-trans-mat> <img-2> <img-2-trans-mat> <img-3> <img-3-trans-mat> <coordinates.yml>" << endl;
		return -1;
	}
	
	FileStorage fs(argv[7], FileStorage::READ);

	if (!fs.isOpened()) {
		cerr << "Error: Could not open the file for writing!" << endl;
		return -1;
	}

	Mat nimg1 = imread(argv[1]);
	Mat nimg2 = imread(argv[3]);
	Mat nimg3 = imread(argv[5]);
	
	if (nimg1.empty() || nimg2.empty() || nimg3.empty()) {
		cerr << "Error: Could not open one or more images!" << endl;
		return -1;
	}

	FileStorage transform_1(argv[2], FileStorage::READ);
	FileStorage transform_2(argv[4], FileStorage::READ);
	FileStorage transform_3(argv[6], FileStorage::READ);

	if (!transform_1.isOpened() || !transform_2.isOpened() || !transform_3.isOpened()){
		cerr << "Error: Could not open the file for writing!" << endl;
		return -1;
	}

	Mat t_1, t_2,t_3;
	transform_1["data"] >> t_1;
	transform_2["data"] >> t_2;
	transform_3["data"] >> t_3;
	
	Mat img1;  
	warpPerspective(nimg1, img1, t_1, Size(640,480));
	Mat img2;
      	warpPerspective(nimg2, img2, t_2, Size(640,480));
	Mat img3; 
	warpPerspective(nimg2, img3, t_3, Size(640,480));

	Mat rotated1,rotated2,rotated3;
	Mat re1, re2, re3;
	Mat output;
	
	/* Variables to store angle of rotation */
	int a1 = 0;
	int a2 = 0;
	int a3 = 0;

	/* Variables to store scaling factor for rotation */
	int s1 = 0;
	int s2 = 0;
	int s3 = 0;	
	
	/* Translation coordinates of three images */
	int x1 = 0;
	int y1 = 0;
	int x2 = 0;
	int y2 = 0;
	int x3 = 0;
	int y3 = 0;

	Mat canvas_size;
	fs["CANVAS SIZE"] >> canvas_size;
	int canvas_width = canvas_size.at<int>(0);
	int canvas_height = canvas_size.at<int>(1);

	cout << "Width " << canvas_width << endl;
	cout << "Height " << canvas_height << endl;
	
	/* Rotation angle */
	fs["img0_rotate_angle"] >> a1;
	fs["img1_rotate_angle"] >> a2;
	fs["img2_rotate_angle"] >> a3;

	/* Scaling factor for rotation */
	fs["img0_scale"] >> s1;
	fs["img1_scale"] >> s2;
	fs["img2_scale"] >> s3;
	
	Mat offset1, offset2, offset3;

	fs["img0offset"] >> offset1;
	x1 = offset1.at<int>(0);
	y1 = offset1.at<int>(1);
	cout << "img 1: width " << x1 << " height " << y1 << endl; 

	fs["img1offset"] >> offset2;
	x2 = offset2.at<int>(0);
	y2 = offset2.at<int>(1);

	cout << "img 2: width " << x2 << " height " << y2 << endl; 

	fs["img2offset"] >> offset3;
	x3 = offset3.at<int>(0);
	y3 = offset3.at<int>(1);

	cout << "img 3: width " << x3 << " height " << y3 << endl; 
	
	Mat center_r_1, center_r_2, center_r_3;
	fs["img0_rotate_angle"] >> center_r_1;
	fs["img2_rotate_angle"] >> center_r_2;
	fs["img3_rotate_angle"] >> center_r_3;

	cout << "Rotation angle : Img 1 " << center_r_1 << endl;
	cout << "Rotation angle : Img 2 " << center_r_2 << endl;
	cout << "Rotation angle : Img 3 " << center_r_3 << endl;

	rotated1 = rotateImage(img1, a1, s1, center_r_1); 
	rotated2 = rotateImage(img2, a2, s2, center_r_2); 
	rotated3 = rotateImage(img3, a3, s3, center_r_3); 

	output = blendImages(re1, re2, re3, x1, y1, x2, y2, x3, y3);
	
	imshow("canvas.jpg",blendedCanvas);
	imwrite("output.jpg", blendedCanvas);

	return 0;
}

