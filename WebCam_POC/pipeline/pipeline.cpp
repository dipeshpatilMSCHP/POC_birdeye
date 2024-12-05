/** 
 * cpp pipeline. 
 * takes an image | img1|img2|img3 | matrices | yml file. and gives the birdeye_view. 
 */

#include <opencv4/opencv2/opencv.hpp>
#include <opencv4/opencv2/core.hpp>
#include <iostream>
#include <vector>

class parse_info {

public:
    int total_images;
    std::vector<std::string> naming_convertion{".jpg","_pT.yml"};


    std::string folder_path;                    // main folder path 
    std::vector <std::string> img_paths;        // image path. { not requireed in video script. there will be no images. }
    std::vector <std::string> pTransform_paths; // {perspective transform matrics path}
    std::string master_yml_path;                // master yml path 
    std::vector <cv::Mat> perspective_transform_matrix;


    parse_info (std::string f_path, int images) {folder_path = f_path; total_images = images; 
    generate_paths();
    read_perspective_matrices();
    }

    void generate_paths();
    void read_perspective_matrices();
    void read_info_yml();
};

/**
    populates the path of images, according to naming convertion. 
 */
void parse_info::generate_paths() {

    // generate the images path 
    std::string img_path;
    for (int i = 0; i < total_images;  i++) {
        img_path = folder_path + std::string("img_") + std::to_string(i) + naming_convertion[0];
        img_paths.push_back(img_path);
    }

    // generate the perspective transform part. 
    for (int i = 0; i < total_images;  i++) {
        img_path = folder_path + std::string("img_") + std::to_string(i) + naming_convertion[1];
        pTransform_paths.push_back(img_path);
    }

    master_yml_path = folder_path + std::string("master.yml");
}

// reads the perspective transform matrix. 
void parse_info::read_perspective_matrices() {

    
    cv::FileStorage fs_tmp;
    bool val;
    cv::Mat tmp;
    
    for (int i = 0; i < pTransform_paths.size(); i++) {

        val = fs_tmp.open (pTransform_paths[i] , cv::FileStorage::READ);
        if (val == 0) {
            std::cout << "enable to read matrix from file : " << pTransform_paths[i] << std::endl;
            std::cout << "Terminating program " << std::endl;
            exit(0);
        }
        fs_tmp["mat"] >> tmp;
        perspective_transform_matrix.push_back(tmp);
        fs_tmp.release();
        tmp.release();
    
    }
}


int main(int argc, char* argv[]) {

    if (argc < 2) {
        printf("Invalid number of arguments \n : this script | folder path \n");
        exit(0);
    }
    parse_info parser(argv[1], 3);
    


}