import cv2
import easygui
import matplotlib.pyplot as plt
import numpy as np


def read_in_image():
    """
    Function to read in a user selected image
    :return: returns the damaged image selected by the user
    """
    easygui.msgbox("Welcome to Timur's photo restoration. Please select a damaged image you would like to restore.",
                   title="Photo Restoration App",
                   ok_button="Select Image")

    return cv2.imread(easygui.fileopenbox())


def process_faded(img):
    """
    Function that holds nested functions used to restore the faded image
    :param img: original faded image that requires restoration
    :return: fixed and restored image
    """
    def find_edges():
        """
        Function that locates edges in the image, this will be used
        so that we can locate the ROI (faded region)
        :return: copy of the grayscale image with detected edges
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Highlight the edges in the image
        lower_threshold = 70
        edge_gray = cv2.Canny(gray, lower_threshold, 200)

        # Creating a copy of the gray image
        return edge_gray.copy()

    def find_and_draw_contours(edge):
        """
        Function that detects and draws contours on the image with detected edges
        :param edge: grayscale image with highlighted edges
        :return: canvas with contours drawn on
        """
        h, w, d = img.shape

        # Find contours in the gray image
        contours, hierarchy = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Creating a blank canvas same size of the original image where I'll draw contours
        blank_for_contours = np.zeros((h, w, d), np.uint8)

        # Drawing the contours in red color on the blank canvas
        cv2.drawContours(blank_for_contours, contours, -1, (0, 0, 255), 2)

        # lines = cv2.HoughLinesP(edge_gray, 1, np.pi/180, 2, None, 30, 1)
        # horizontal = cv2.HoughLinesP(edge_gray, 1, np.pi/90, 100, minLineLength=80, maxLineGap=5)
        # vertical = cv2.HoughLinesP(edge_gray, 1, np.pi/45, 100, minLineLength=80, maxLineGap=5)

        return blank_for_contours

    def find_intersecting_points_of_contours(blank_contours):
        """
        Function that locates the intersecting points of contours
        :param blank_contours: canvas with drawn on contours
        :return: canvas with detected contours in the intersection
        """
        # Lines which represent the thickness of the edge of the damaged area
        horizontal_damaged_line = (60, 1)
        vertical_damaged_line = (1, 60)

        # Creating a rectangular kernel
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, horizontal_damaged_line)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, vertical_damaged_line)

        # Applying horizontal and vertical kernels to find horizontal/vertical straight edges
        detect_horizontal = cv2.morphologyEx(blank_contours, cv2.MORPH_OPEN, horizontal_kernel)
        detect_vertical = cv2.morphologyEx(blank_contours, cv2.MORPH_OPEN, vertical_kernel)

        # Applying bitwise and operator to find the intersection of the vertical and horizontal edges
        intersection = cv2.bitwise_and(detect_horizontal, detect_vertical)
        intersection = cv2.cvtColor(intersection, cv2.COLOR_BGR2GRAY)

        # Detecting contours in the intersection
        contours = cv2.findContours(intersection, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]

        return contours

    def find_coordinates_of_faded_region(contours):
        """
        Function that locates the coordinates of the ROI (faded area)
        :param contours: contours found in the image
        :return: coordinates of the ROI
        """
        # Getting the image shape
        h, w, d = img.shape

        # Looping through the contours to detect insecting points which will be our faded region
        intersection_coordinates = []
        for item in contours:
            horizontal = item[0][0][0]
            vertical = item[0][0][1]

            intersection_coordinates.append((horizontal, vertical))

        # Coordinate points which represent the location of the faded region
        x1y1 = (w, h)
        x2y2 = (0, 0)

        # Looping over the intersection coordinates (4 corners of a rectangle)
        for point in intersection_coordinates:
            horizontal, vertical = point[0], point[1]

            # Finding the most top left outer and bottom right outer coordinates
            if horizontal + vertical < x1y1[0] + x1y1[1]: x1y1 = (horizontal, vertical)
            if horizontal + vertical > x2y2[0] + x2y2[1]: x2y2 = (horizontal, vertical)

        return x1y1, x2y2

    def cropping_faded_region(top_left, bottom_right):
        """
        Function that crops the faded region given 2 coordinates, top left and bottom right of the boundary
        :param top_left: x1,y1 coordinates of the ROI
        :param bottom_right: x2,.y2 coordinates of the ROI
        :return: blank canvas the size and depth of the original colored image
        :return: cropped image at the faded region
        """
        # Getting a copy of the original image
        img_crop = img.copy()

        # Cropping original image at the coordinates that denote the faded region
        img_crop = img_crop[top_left[1]: bottom_right[1], top_left[0]: bottom_right[0]]

        # Getting the dimensions of the cropped image
        cropped_h, cropped_w, cropped_d = img_crop.shape

        # Creating a blank canvas the size of the cropped image
        return np.zeros((cropped_h, cropped_w, 3), np.uint8), img_crop

    def fixing_color_of_faded_region(blank_canvas, img_crop):
        """
        Function that fixes the faded region by modifying the color value
        :param blank_canvas: empty canvas the size of the original image
        :param img_crop: cropped image
        :return: image after subtracting the modified canvas
        """
        # Creating a blank canvas and adding 30 pixels to it
        blank_canvas = blank_canvas + 30

        # Subtracting the black modified canvas from the cropped image
        return cv2.subtract(img_crop, blank_canvas)

    def restoring_faded_region_with_new(darkened_img, top_left, bottom_right):
        """
        Function that restores the faded region in the image
        :param original image that has been darkened:
        :param top_left x1,y1 coordinate of the faded region:
        :param bottom_right x2, y2 coordinate of the faded region:
        :return: Returns the image that was inpainted by a mask
        """
        h, w, d = img.shape

        # Creating a copy of original image
        restored_img = img.copy()

        # Inserting the darkened image into the original image at the coordinates where the faded region is
        restored_img[top_left[1]: bottom_right[1], top_left[0]:bottom_right[0]] = darkened_img

        # creating a mask same size of the original image
        border_blend_mask = np.zeros((h, w, 3), np.uint8)

        # Drawing a rectangle on the empty black canvas in white which will be used to inpaint the image
        cv2.rectangle(border_blend_mask, top_left, bottom_right, (255, 255, 255), 4)

        # Converting the mask to grayscale
        border_mask = cv2.cvtColor(border_blend_mask, cv2.COLOR_BGR2GRAY)

        return cv2.inpaint(restored_img, border_mask, 3, cv2.INPAINT_TELEA)

    # Find edges in the image
    edges = find_edges()

    # Draw contours on the image with edges
    canvas = find_and_draw_contours(edges)

    # Find the intersection points of the contours
    contour_region = find_intersecting_points_of_contours(canvas)

    # Find the coordinates of the faded rectangle
    point_a, point_b = find_coordinates_of_faded_region(contour_region)

    # Crop the faded region from the original image so that we can work on it
    black_mask, cropped_region = cropping_faded_region(point_a, point_b)

    # Fix the color of the faded region
    modified_img = fixing_color_of_faded_region(black_mask, cropped_region)

    # Add the restored cropped image back into the original and blend edges
    restored_img = restoring_faded_region_with_new(modified_img, point_a, point_b)

    return restored_img


def process_damaged(img):
    """
    Function that restores the damage in an image
    :param img
    :return: denoised image
    """

    # Arguments for the function to remove noise from the image
    filter_strength = 8
    color_components = 10
    template_window_size = 7
    search_window_size = 21

    # Denoise the image
    denoised = cv2.fastNlMeansDenoisingColored(img, None, filter_strength, color_components, template_window_size, search_window_size)

    return cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)



def find_highest_peaks_of_colors(img):
    """
    Function to find the highest x value of a color channel (brightness of it, 255 being the brightest),
    this way we know which algorithm to select for the image
    :param img:
    :return: highest value of a color channel
    """

    color_values = []
    colors = []

    # Create a histogram of each seperate color channel
    # This will allow us to see which color channels are prevalent in the image we're restoring
    [color_values.append(cv2.calcHist([img], [j], None, [256], [0, 256])) for j in range(0, 3)]

    # Appending each ravelled histogram to an array
    colors.append(color_values[0].ravel())
    colors.append(color_values[1].ravel())
    colors.append(color_values[2].ravel())

    indices = list(range(0, 256))

    set_arr = []
    for i in range(0, 3):
        zipped = (zip(colors[i], indices))
        sorted_set = sorted(zipped, reverse=True)
        set_arr.append(sorted_set)

    # Get the BGR values separately
    b = [(i, j) for j, i in set_arr[0]]
    g = [(i, j) for j, i in set_arr[1]]
    r = [(i, j) for j, i in set_arr[2]]

    # Index denoting the highest peak in the histogram
    b_index = b[0][0]
    g_index = g[0][0]
    r_index = r[0][0]

    # BGR highest color values in an image (we want to find the brightest index)
    color_peaks = [b_index, g_index, r_index]
    color_peaks.sort()

    # Variable to store the brightest color channel (255 being the highest)
    highest_val = 0

    # Loop through the color peaks and find the highest value out of the color channels
    for i in range(0, len(color_peaks)):
        if color_peaks[i] > highest_val:
            highest_val = color_peaks[i]
    return highest_val


def display_img(img):
    """
    Function to display the newly restored image
    """
    cv2.imwrite('restoredImage.jpg', img)
    cv2.imshow('Your Newly Restored Image', img)
    cv2.waitKey(0)

# Read in a user selected image and find the brightest occuring value
img = read_in_image()
highest = find_highest_peaks_of_colors(img)

brightness_threshold = 100

# Check if majority of the image is dark (I'm using a threshold of 100 to check if an image is dark)
if highest > brightness_threshold:
    img = process_damaged(img)
else:
    img = process_faded(img)

# Display the restored image
display_img(img)





