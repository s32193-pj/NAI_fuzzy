import argparse
import os
import sys
from PIL import Image
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzzy


# parsing environmental variables
def parsing_arguments():
    parser = argparse.ArgumentParser(
        prog='Image Edge Detector',
        description='Uses fuzzy logic to detect edges in image',
        suggest_on_error=True
    )

    parser.add_argument('filename', help='path and filename of image to analyze')
    parser.add_argument("-s", "--save", help="save output to file if set true", action='store_true')
    parser.add_argument('-d', '--display', help="display analyzed image", action='store_true')
    parser.add_argument('-g', '--greyscale', help="display greyscale image", action='store_true')
    parser.add_argument('-c', '--colour', help="display colour image", action='store_true')
    parser.add_argument('-r', '--gradient', help="display gradient", action='store_true')
    args = parser.parse_args()

    return args


#load image
def load_image_file(image_path):
    extensions = ['.jpg', '.jpeg', '.png']
    try:
        image = Image.open(image_path)
    except IOError:
        file_extension = os.path.splitext(image_path)[1].lower()
        if file_extension not in extensions:
            sys.exit("\nInvalid extension. Supported extensions: {}".format(extensions))
        sys.exit("\nCould not open image file: {}".format(image_path))
    return image


# detecting edges
def fuzzy_edges(image,sx=0.1, sy=0.1, n_points=101):
    greyImg = image.convert('L')
    i = np.array(greyImg, dtype=float) / 255.0

    # create gradient filters
    gx = np.array([[-1, 1]])
    gy = np.transpose(gx)
    ix = ndimage.convolve(i, gx, mode='nearest')
    iy = ndimage.convolve(i, gy, mode='nearest')

    # fuzzification
    mu_x = fuzzy.gaussmf(ix, 0, sx)
    mu_y = fuzzy.gaussmf(iy, 0, sy)

    # Rules
    # Rule1
    r_white = np.fmin(mu_x, mu_y)
    # Rule2
    r_black = np.fmax(1 - mu_x, 1 - mu_y)

    # Output
    z = np.linspace(0, 1, n_points)
    white = fuzzy.trimf(z, [0.1, 1, 1])
    black = fuzzy.trimf(z, [0, 0, 0.7])

    # Implikacja (min) + agregacja (max), dla wszystkich pikseli naraz
    agg = np.fmax(np.fmin(r_white[..., None], white),
                  np.fmin(r_black[..., None], black))

    # Defuzzify using weight center method
    ieval = (agg * z).sum(axis=-1) / agg.sum(axis=-1)
    return [ieval,ix,iy,greyImg]

#save edgy image
def save_edgy_image(edgy_image):

    Image.fromarray((edgy_image * 255).astype(np.uint8)).save("output.png")

#display chosen
def display_image(args,img,data_set):


    # plot image gradients
    plt.ion()

    if args.gradient:
        # Ix
        plt.figure()
        plt.imshow(data_set[1], cmap='gray')
        plt.title('Ix')
        plt.show()

        # Iy
        plt.figure()
        plt.imshow(data_set[2], cmap='gray')
        plt.title('Iy')
        plt.show()

    if args.display:
        # display fuzzy_edges
        plt.figure()
        plt.imshow(data_set[0], cmap='gray')
        plt.title('Ieval')
        plt.show()

    if args.colour:
        # display colour
        plt.figure()
        plt.imshow(img)
        plt.title('Colour image')
        plt.show()

    if args.greyscale:
        plt.figure()
        plt.imshow(data_set[3], cmap='gray')
        plt.title('Greyscale image')
        plt.show()
        # display plotted
    plt.ioff()
    plt.show()


def main():
    args = parsing_arguments()
    image = load_image_file(args.filename)
    data_set = fuzzy_edges(image)
    if args.save:
        save_edgy_image(data_set[0])
    display_image(args,image, data_set)


if __name__ == '__main__':
    main()
