import numpy as np
import cv2
from imutils.object_detection import non_max_suppression
import pytesseract
from PIL import Image
from gingerit.gingerit import GingerIt
import requests
pytesseract.pytesseract.tesseract_cmd = 'D:\\desktop\\gmjvn\\Tesseract-OCR\\tesseract.exe'
def spell(text):
    parser = GingerIt()
    return parser.parse(text)["result"]


def normalizeRed(intensity):
    iI = intensity
    minI = 86
    maxI = 230
    minO = 0
    maxO = 255
    iO = (iI - minI) * (((maxO - minO) / (maxI - minI)) + minO)
    return iO


# Method to process the green band of the image
def normalizeGreen(intensity):
    iI = intensity
    minI = 90
    maxI = 225
    minO = 0
    maxO = 255
    iO = (iI - minI) * (((maxO - minO) / (maxI - minI)) + minO)
    return iO


# Method to process the blue band of the image
def normalizeBlue(intensity):
    iI = intensity
    minI = 100
    maxI = 210
    minO = 0
    maxO = 255
    iO = (iI - minI) * (((maxO - minO) / (maxI - minI)) + minO)
    return iO


def contrastImg(img):
    # Create an image object
    image_object = Image.open(img)

    # Split the red, green and blue bands from the Image
    multi_bands = image_object.split()

    # Apply point operations that does contrast stretching on each color band
    normalized_red_band = multi_bands[0].point(normalizeRed)
    normalized_green_band = multi_bands[1].point(normalizeGreen)
    normalized_blue_band = multi_bands[2].point(normalizeBlue)

    # Create a new image from the contrast stretched red, green and blue brands
    normalized_image = Image.merge("RGB", (normalized_red_band, normalized_green_band, normalized_blue_band))
    normalized_image.save(img)


def descanImg(image):
    # load image
    img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    # adjust contrast
    img = cv2.multiply(img, 1.2)

    # create a kernel for the erode() function
    kernel = np.ones((1, 1), np.uint8)

    # erode() the image to bolden the text
    img = cv2.erode(img, kernel, iterations=1)

    # save the file
    cv2.imwrite(image, img)


def denoiseImg(image):
    img = cv2.imread(image)
    dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    cv2.imwrite(image, dst)

def predictions(prob_score, geo, args):
    (numR, numC) = prob_score.shape[2:4]
    boxes = []
    confidence_val = []
    # loop over rows
    for y in range(0, numR):
        scoresData = prob_score[0, 0, y]
        x0 = geo[0, 0, y]
        x1 = geo[0, 1, y]
        x2 = geo[0, 2, y]
        x3 = geo[0, 3, y]
        anglesData = geo[0, 4, y]

        # loop over the number of columns
        for i in range(0, numC):
            if scoresData[i] < args["min_confidence"]:
                continue

            (offX, offY) = (i * 4.0, y * 4.0)

            # extracting the rotation angle for the prediction and computing the sine and cosine
            angle = anglesData[i]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # using the geo volume to get the dimensions of the bounding box
            h = x0[i] + x2[i]
            w = x1[i] + x3[i]

            # compute start and end for the text pred bbox
            endX = int(offX + (cos * x1[i]) + (sin * x2[i]))
            endY = int(offY - (sin * x1[i]) + (cos * x2[i]))
            startX = int(endX - w)
            startY = int(endY - h)

            boxes.append((startX, startY, endX, endY))
            confidence_val.append(scoresData[i])

    # return bounding boxes and associated confidence_val
    return (boxes, confidence_val)


def convertImageToText(img_path, east_path):
    args = {"image": img_path, "east": east_path, "min_confidence": 0.5, "width": 320, "height": 320}
    image = cv2.imread(args['image'])
    orig = image.copy()
    (origH, origW) = image.shape[:2]
    # b_color = tuple(image[100][50])
    # reformat_Image(img, b_color)
    # image = cv2.imread(args['image'])
    (newW, newH) = (args["width"], args["height"])
    rW = origW / float(newW)
    rH = origH / float(newH)
    new_size = (newW, newH)
    image = cv2.resize(image, (newW, newH))
    cv2.imwrite(img_path, image)
    contrastImg(img_path)
    # binarizeImg(img)
    denoiseImg(img_path)
    descanImg(img_path)
    # deskewImg(img)
    (H, W) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net = cv2.dnn.readNet(args["east"])
    layer_names = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    net.setInput(blob)
    (scores, geometry) = net.forward(layer_names)

    (boxes, confidence_val) = predictions(scores, geometry, args)
    boxes = non_max_suppression(np.array(boxes), probs=confidence_val)
    results = []

    for (start_x, start_y, end_x, end_y) in boxes:
        text_identified = 1
        start_x = int(start_x * rW) - 10
        start_y = int(start_y * rH) - 10
        end_x = int(end_x * rW) + 10
        end_y = int(end_y * rH) + 10
        try:
            r = orig[start_y:end_y, start_x:end_x]
            configuration = "-l eng --oem 1 --psm 8"
            text = pytesseract.image_to_string(r, config=configuration)
            results.append(((start_x, start_y, end_x, end_y), text))
        except:
            continue
    results.sort(key=lambda x: x[0][0])
    final_list = []
    if len(results) == 0:
        print("NO text detected")
    else:
        i = results[0]
        j = 0
        index = i[0][1]
        line = ""
    while len(results) != 0:
        if j == len(results):
            i = results[0]
            j = 0
            index = i[0][1]
            line = ""
        if index - 30 < results[j][0][1] < index + 30:
                line = line + results[j][1] + " "
                results.pop(j)
        else:
            j = j + 1
        if j == len(results):
            if line.strip() != "":
                line = spell(line)
                final_list.append(line)
    print(final_list)
    print("text::", final_list)
    return final_list


def formatImage(url, msg_id):
    img_data = requests.get(url).content
    img_path = "media/" + str(msg_id) + ".jpg"
    with open(img_path, 'wb') as handler:
        handler.write(img_data)
    print("image path::",img_path)
    return img_path
