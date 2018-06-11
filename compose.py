#
# credits: https://github.com/miguelgrinberg/anaglyph.py/blob/master/anaglyph.py
#
import numpy as np
import cv2
from grab import WebcamVideoStream

class VideoCamera(object):
    def __init__(self):
        # left eye
        self.videoL = WebcamVideoStream(src=0).start()

        # right eye
        self.videoR = WebcamVideoStream(src=1).start()

        # declare various color blending algorithms to mix the pixels
        # from different perspectives so that red/blue lens glasses
        # make the image look 3D
        self.mixMatrices = {
               'true': [ [ 0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0 ], 
                         [ 0, 0, 0, 0, 0, 0, 0.299, 0.587, 0.114 ] ],
               'mono': [ [ 0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0 ], 
                         [ 0, 0, 0, 0.299, 0.587, 0.114, 0.299, 0.587, 0.114 ] ],
               'color': [ [ 1, 0, 0, 0, 0, 0, 0, 0, 0 ], 
                         [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
               'halfcolor': [ [ 0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0 ], 
                         [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
               'optimized': [ [ 0, 0.7, 0.3, 0, 0, 0, 0, 0, 0 ],
                         [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
               'redcyan': [ [ 0.2, 0.5, 0.3, 0, 0, 0, 0, 0, 0 ], 
                         [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
        }
        # init object - is there a better way?
        self.anaglyphImage = self.videoL.read()

    def __del__(self):
        self.videoL.stop()
        self.videoR.stop()
    
    def get_frame(self):
        # grab frames
        frameL = self.videoL.read()
        frameR = self.videoR.read()

        # use the color argument to select a color separation formula from mixMatrices
        m = self.mixMatrices['redcyan']

        # make an anaglyph (note that we presume the image is in BGR format)
        # split the left and right images into separate blue, green and red images
        lb,lg,lr = cv2.split(np.asarray(frameL[:,:]))
        rb,rg,rr = cv2.split(np.asarray(frameR[:,:]))
        resultArray = np.asarray(self.anaglyphImage[:,:])
        resultArray[:,:,0] = lb*m[0][6] + lg*m[0][7] + lr*m[0][8] + rb*m[1][6] + rg*m[1][7] + rr*m[1][8]
        resultArray[:,:,1] = lb*m[0][3] + lg*m[0][4] + lr*m[0][5] + rb*m[1][3] + rg*m[1][4] + rr*m[1][5]
        resultArray[:,:,2] = lb*m[0][0] + lg*m[0][1] + lr*m[0][2] + rb*m[1][0] + rg*m[1][1] + rr*m[1][2]

        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', self.anaglyphImage)
        return jpeg.tobytes()

