import cv2
import easyocr

def preProcessImage(image,flag):
    #converting image to grayscale
    processedImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #noise reduction using blur
    if flag:
        processedImage = cv2.GaussianBlur(processedImage, (5, 5), 0)

    #image negative
    processedImage=255-processedImage

    return processedImage


def process(image,flag=False):

    #preprocessing the image
    processedImage=preProcessImage(image,flag)

    #edge detection using Canny function from openCV
    edges = cv2.Canny(processedImage, 100,200)

    #finding contours (RETR_EXTERNAL didn't work well since parent delete child)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    #selecting potential license plate regions
    potentialLicensePlates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        #applying knowledge for lebanese plate number
        if (w > 100 and h > 30) and (w / h < 4.5)and (w / h > 2): 
            #drawing rectangles for potential regions
            cv2.rectangle(imageCopy,(x,y),(x+w,y+h),(0,255,0),5)
            potentialLicensePlates.append((x, y, w, h))

    #using OCR for each potential license plate region
    reader = easyocr.Reader(['en'])
    licensePlates = []
    for x, y, w, h in potentialLicensePlates:
        region = processedImage[y:y+h, x:x+w]

        #processing the region using OCR
        results = reader.readtext(region)

        #displaying result for each region
        print(results)

        if not results:continue #checking if results is empty to skip

        #building string found in each region
        full=''
        p=1
        for r in results:
            p*=r[2]
            full+=r[1].replace(" ", "")

        #applying knowledge for lebanese plate number
        if not full[0].isalpha() or len(full)<5:p/=4
        if not full[1:].isdigit():continue

        licensePlates.append((x, y, w, h, full,p))
        
    #searching for plate number with highest probability
    max=0
    plate=''
    index=-1
    for i in range(len(licensePlates)):
        if licensePlates[i][5]>max:
            max=licensePlates[i][5]
            plate=licensePlates[i][4]
            index =i

    #searching for the smallest area containing the plate number
    area=float('inf')
    rg=None
    for i in range(len(licensePlates)):
        if licensePlates[i][4]==plate and area>licensePlates[i][2]*licensePlates[i][3]:
            area=licensePlates[i][2]*licensePlates[i][3]
            rg=licensePlates[i]

    return rg



#reading image
image = cv2.imread(input('Enter Image number:')+'.jpg')

#getting a coppy of the image to show processing
imageCopy=image.copy()

#regions detection and OCR
rg=process(image)

#bluring if result None
if rg==None: rg=process(image,True)
#displaying the result found
print(rg)

#displaying the detected license plates
if rg:
    x, y, w, h, text,_=rg
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#displaying edges found
resizedImage1 = cv2.resize(imageCopy, (600, int(imageCopy.shape[0] * 600 / imageCopy.shape[1])), interpolation=cv2.INTER_CUBIC)
cv2.imshow('Image', imageCopy)
cv2.waitKey(0)
cv2.destroyAllWindows()

#showing the image with detected license plates
resizedImage2 = cv2.resize(image, (600, int(image.shape[0] * 600 / image.shape[1])), interpolation=cv2.INTER_CUBIC)
cv2.imshow('Image', resizedImage2)
cv2.waitKey(0)
cv2.destroyAllWindows()