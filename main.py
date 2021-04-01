import threading
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import Image
from PIL import ImageTk
import io
import re
import os
import cv2
import numpy as np
import colorsys


class Camera:
    cam = None
    props_ = {}

    def __init__(self, port:int):
        self.cam = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        # self.cam.set(cv2.CAP_OPENNI_DEPTH_GENERATOR, 1)
        self.props_['CAP_PROP_FPS'] = self.cam.get(cv2.CAP_PROP_FPS)
        self.props_['CAP_PROP_PAN'] = self.cam.get(cv2.CAP_PROP_PAN)
        self.props_['CAP_PROP_HUE'] = self.cam.get(cv2.CAP_PROP_HUE)
        self.props_['CAP_PROP_FOCUS'] = self.cam.get(cv2.CAP_PROP_FOCUS)
        self.props_['CAP_PROP_GAIN'] = self.cam.get(cv2.CAP_PROP_GAIN)
        self.props_['CAP_PROP_APERTURE'] = self.cam.get(cv2.CAP_PROP_APERTURE)
        self.props_['CAP_PROP_AUTO_EXPOSURE'] = self.cam.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        self.props_['CAP_PROP_AUTO_WB'] = self.cam.get(cv2.CAP_PROP_AUTO_WB)
        self.props_['CAP_PROP_BITRATE'] = self.cam.get(cv2.CAP_PROP_BITRATE)
        self.props_['CAP_PROP_BRIGHTNESS'] = self.cam.get(cv2.CAP_PROP_BRIGHTNESS)
        self.props_['CAP_PROP_CONTRAST'] = self.cam.get(cv2.CAP_PROP_CONTRAST)
        self.props_['CAP_PROP_EXPOSURE'] = self.cam.get(cv2.CAP_PROP_EXPOSURE)
        self.props_['CAP_PROP_FORMAT'] = self.cam.get(cv2.CAP_PROP_FORMAT)
        self.props_['CAP_PROP_FOURCC'] = self.cam.get(cv2.CAP_PROP_FOURCC)
        self.props_['CAP_PROP_FRAME_COUNT'] = self.cam.get(cv2.CAP_PROP_FRAME_COUNT)
        self.props_['CAP_PROP_FRAME_HEIGHT'] = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.props_['CAP_PROP_FRAME_WIDTH'] = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.props_['CAP_PROP_MODE'] = self.cam.get(cv2.CAP_PROP_MODE)
        self.props_['CAP_PROP_ZOOM'] = self.cam.get(cv2.CAP_PROP_ZOOM)
        #
        for key, value in self.props_.items():
            print('{} {}'.format(key, value))

    def ready(self):
        return self.cam.read()[0]

    def close(self):
        self.cam.release()


class Window:
    def __init__(self, master):
        self.package = 'Web Cam Toolbox'
        master.title(self.package)
        master.minsize(1200, 600)
        master.resizable(0, 0)
        self.master = master
        self.filename = ""
        self.commandText = ""

        self.cam1Obj = None
        self.cam1Connected = False
        self.cam2Obj = None
        self.cam2Connected = False

        toolbar = LabelFrame(root)
        toolbar.grid(row=1, column=1)

        self.cam1 = StringVar(root)
        options = [0, 1, 2, 3, 4]
        self.cam1.set(options[0])
        cam1 = OptionMenu(*(toolbar, self.cam1) + tuple(options))
        cam1.grid(row=1, column=2, padx=2, pady=1)
        cam1.configure(width=15)
        self.connectButton1 = Button(toolbar, text="Connect", command=self.connect_cam1)
        self.connectButton1.grid(row=1, column=3, padx=2, pady=1)

        self.cam2 = StringVar(root)
        options = [0, 1, 2, 3, 4]
        self.cam2.set(options[1])
        cam2 = OptionMenu(*(toolbar, self.cam1) + tuple(options))
        cam2.grid(row=1, column=4, padx=2, pady=1)
        cam2.configure(width=15)
        self.connectButton2 = Button(toolbar, text="Connect", command=self.connect_cam2)
        self.connectButton2.grid(row=1, column=5, padx=2, pady=1)

        # im = Image.open("Default.png")
        image = np.zeros((400, 400), dtype=np.uint8)
        photo = self.arrayToImage(image)  # openCV to PIL image
        self.cam1ImageView = Label(root, width=400, height=360)
        self.cam1ImageView.grid(row=2, column=1)
        self.cam1ImageView["image"] = photo
        self.cam1Photo = photo

        self.cam2ImageView = Label(root, width=400, height=360)
        self.cam2ImageView.grid(row=2, column=2)
        self.cam2ImageView["image"] = photo
        self.cam2Photo = photo

    def is_grayscale(self, image):
        return len(image.shape) < 3

    def arrayToImage(self, image):
        if not self.is_grayscale(image):
            b, g, r = cv2.split(image)
            image = cv2.merge((r, g, b))
        p = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image=p)
        return photo

    def imageToBytes(self, image):
        b = io.BytesIO()
        image.save(b, 'gif')
        p = b.getvalue()
        photo = PhotoImage(data=p)
        return photo

    def connect_cam1(self):
        if self.cam1Connected:
            self.cam1Obj.cam.release()
            self.connectButton1.configure(text="Connect")
            self.cam1Connected = False
        else:
            thread = threading.Thread(group=None, target=self.init_cam1, name=None, args=(), kwargs={})
            thread.start()

    def connect_cam2(self):
        if self.cam2Connected:
            self.cam2Obj.cam.release()
            self.connectButton2.configure(text="Connect")
            self.cam2Connected = False
        else:
            thread = threading.Thread(group=None, target=self.init_cam2, name=None, args=(), kwargs={})
            thread.start()

    def init_cam1(self):
        port = int(self.cam1.get())
        print('Connecting cam1, port ' + str(port))
        self.cam1Obj = Camera(port)
        if self.cam1Obj.ready():
            self.cam1Connected = True
            self.connectButton1.configure(text='Disconnect')
            while self.cam1Obj.cam.isOpened():
                _, frame = self.cam1Obj.cam.read()
                # cv2.imshow('Im', frame)
                photo = self.arrayToImage(frame)
                self.cam1ImageView["image"] = photo
                self.cam1Photo = photo
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            self.cam1Obj.cam.release()

    def init_cam2(self):
        port = int(self.cam2.get())
        print('Connecting cam2, port ' + str(port))
        self.cam2Obj = Camera(port)
        if self.cam2Obj.ready():
            self.cam2Connected = True
            self.connectButton2.configure(text='Disconnect')
            while self.cam2Obj.cam.isOpened():
                _, frame = self.cam2Obj.cam.read()
                photo = self.arrayToImage(frame)
                self.cam2ImageView["image"] = photo
                self.cam2Photo = photo
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            self.cam2Obj.cam.release()

root = Tk()
window = Window(root)
root.mainloop()
