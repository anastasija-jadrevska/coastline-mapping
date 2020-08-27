import gdal
import numpy as np
import cv2
import glob
from scipy import ndimage

# collect names of all images

images = []
for name in glob.glob("/Users/Documents/Data/*.tif"):
    images.append(name)

# test image
# images.append("image_62.tif")

# set a name for saved images
nfnb= '/Users/Documents/Output/edge_'


def read_img(filename):
    # read an image
    img_r = cv2.imread(filename, 0)
    img = img_r.astype(np.uint8)

    # read it as a GeoTiff to collect geodata
    img_m = gdal.Open(filename)
    img_array = img_m.ReadAsArray()

    # create a NO DATA mask
    img_mask = (img_array == 0)
    return img, img_mask, img_m


def get_binary(img_in):

    q = 10
    blur = cv2.bilateralFilter(image, q, q*2, q/2)

    (thresh, binary) = cv2.threshold(blur, 128, 255, (cv2.THRESH_BINARY + cv2.THRESH_OTSU))


def delete_b(img):

    # split into components
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=4)

    # remove background
    sizes = stats[1:, -1]
    nb_components = nb_components - 1

    # find the largest component
    max_size = sizes[1]
    for i in range(2, nb_components):
        if sizes[i] > max_size:
            max_size = sizes[i]

    # set to optimal min size
    min_size = max_size * 0.6

    img2 = np.zeros(output.shape)
    # for every component in the image check if it larger than set minimum size
    for i in range(0, nb_components):
        if sizes[i] > min_size:
            img2[output == i + 1] = 1
    return img2


def remove_mask(img, mask, val):

    y = 0
    img = img.astype('f4')
    for booly in mask:
        index = 0
        for bool in booly:
            if bool:
                img[y][index] = val
            index += 1
        y += 1

    return img


# compare edges on original and inverted image to find a common line (coastline)
def find_edge(edge1, edge2):
    # counter 1
    y = 0
    for entry in edge1:
        # counter 2
        x = 0
        for other in entry:
            # keep only entries that match in both arrays
            if other != edge2[y][x]:
                edge2[y][x] = 0
            x += 1
        y += 1
    return edge2


def save_img(final, count, geo_file):
    # get driver
    driver_tiff = gdal.GetDriverByName("GTiff")

    # set the file name
    nfn = nfnb + str(count) + '.tif'

    # create GeoTiff
    nds = driver_tiff.Create(nfn, xsize=geo_file.RasterXSize, ysize=geo_file.RasterYSize, bands=1,
                             eType=gdal.GDT_UInt16)
    nds.SetGeoTransform(geo_file.GetGeoTransform())
    nds.SetProjection(geo_file.GetProjection())

    # copy output to the created file
    bandn = nds.GetRasterBand(1).ReadAsArray()
    bandn = final
    nds.GetRasterBand(1).WriteArray(bandn)

    # set no data to remove background
    nds.GetRasterBand(1).SetNoDataValue(0)
    nds = None


count = 0
for fn in images:
    print(fn)
    print("------------------------")
    # read in the image
    (image, mask, geo_file) = read_img(fn)

    # get binary image
    binary = get_binary(image).astype(np.uint8)

    # remove small white misclassified fields
    binary_w = delete_b(binary).astype(np.uint8)

    # add no data field around
    new_b = remove_mask(binary_w, mask, 1).astype(np.uint8)

    # reverse the image
    reverse = (~new_b.astype(bool)).astype(np.uint8)

    # remove misclassified black fields
    new_clean = delete_b(reverse).astype(np.uint8)

    # add no data
    temp = remove_mask(new_clean, mask, 1).astype(np.uint8)

    # reverse it back to original
    binary_clean = (~temp.astype(bool)).astype(np.uint8)

    # extract the boundary
    boundary = binary_clean - ndimage.morphology.binary_dilation(binary_clean)

    # do a morphologic close
    kernel = np.ones((3, 3))
    final = cv2.morphologyEx(boundary, cv2.MORPH_CLOSE, kernel)

    # save the image
    save_img(final, count, geo_file)

    count += 1
    print('Loop' + str(count))


print("Finished")



