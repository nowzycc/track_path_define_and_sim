# from track_define_interface import single_track
import track_define_interface
import cv2

track = track_define_interface.single_track('anyang','grayscalepic')

track.set_grayscale_pic('./test_img/track_anyang_cad.png',
                        pix_length=0.05)

cv2.imshow('test',track.binary_pic)
key = cv2.waitKey(0)
