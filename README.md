# Image Processing Assignment: Transformation
Timur Sultanov

### Description:
This program's goal is to restore faded and damaged images supplied by the user. I couldn't find an algorithm to suit both images for the simple fact that both images have completely different defects. The faded image has a clear border depicting the transition between the faded and non faded region whereas the damaged image does not.

### Algorithm for the faded image:
In order to fix the faded image, the following operations are performed:

**1.** Image is read in and converted to grayscale.<br />
**2.**. Edges are located in the image.<br />
**3.** A blank canvas is created, contours are then found and drawn onto it with the help of the edged image.<br />
**4.** Intersecting points are located on the contour canvas.<br />
**5.** Program loops over the intersecting points and discovers the outer most points to ensure entire ROI is captured.<br />
**6.** The faded region is cropped via the newly found coordinates.<br />
**7.** The faded region's color is adjusted to match the non faded background.<br />
**8.** Newly restored cropped region is inserted back into the original image and inpainted to remove marks of an edit.<br />
**9.** Image is written and displayed.

### Algorithm for the damaged image:

**1.** Image is read in.<br />
**2.** Arguments are created to remove the noise but retain as much information as possible.<br />
**3.** Image is converted to grayscale.<br />
**4.** Image is written and displayed.<br />

### Research:
The first problem which I had was identifying edges so that I could crop the faded region from the image. I looked into various ways of achieving this and one that proved successful was the canny edge detector. "It takes as input a gray scale image, and produces as output an image showing the positions of tracked intensity discontinuities."[1] Once I read how it works I was able to apply it to my program.

Working with the damaged image was a bit tricky since I wasn't sure what I could have actually done to produce meaningful results. After exploring various functions and experimenting with them, I came across a function that removed noise from an image. I googled 'opencv denoisation' and looked at google images to see if I could find something remotely similar to my image. After seeing a sample image 'geeksforgeeks' had done, the image restoration seemed somewhat like my image. I read their article "Python | Denoising of colored images using opencv"[2] after which I tried to apply the same function on my image and the result it outputted looked like an improved version of the original image.

Another problem which I encountered was determining how I would come up with an algorithm to determine which restoration function to run the image against. First I looked into converting both images into grayscale and then displaying regular histograms to determine the difference but both images had a mixture of dark and light pixels. I looked into analysing the RGB color channels and mapping them to a histogram to see what color channels were prevalent in each image so that I could find something different between the 2 images. I read about "Multi-dimensional Histograms"[3] where I learned it's possible to map each color channel onto the same histogram so that they would overlap and I could compare them.

This is the approach I used and found that for the damaged image, the pixel intensity distribution was more towards the lighter side (closer to 255) for the brightest color channels and for the faded image, it was generally under 100.<br />

### Before: Faded Image <br />
![Before: Faded Image](/Assets/Faded.jpg)

### After: Faded Image <br />
![Before: Faded Image](/Restored_Faded.jpg)

### Before: Damaged Image <br />
![Before: Damaged Image](/Assets/Damaged.jpg)

### After: Damaged Image <br />
![Before: Damaged Image](/Restored_Damaged.jpg)

References:

1. Canny Edge Detector [Internet]. homepages.inf.ed.ac.uk 2003 [cited 2021 Oct 31]. Available from: https://homepages.inf.ed.ac.uk/rbf/HIPR2/canny.htm<br />
2. Python | Denoising of colored images using opencv [Internet]. geeksforgeeks.org 2019 [cited 2021 Oct 31]. Available from: https://www.geeksforgeeks.org/python-denoising-of-colored-images-using-opencv/<br />
3. Clever Girl: A Guide to Utilizing Color Histograms for Computer Vision and Image Search Engines [Internet]. pyimagesearch.com 2014 [cited 2021 Oct 31]. Available from:<br /> https://www.pyimagesearch.com/2014/01/22/clever-girl-a-guide-to-utilizing-color-histograms-for-computer-vision-and-image-search-engines/<br />
