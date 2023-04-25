import cv2
import time
import re
from pyzbar import pyzbar
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class codeScanner:
    def __init__(self, window):
        self.window = window
        self.cap = None
        self.camera_idx = 0
        self.interval = 1000    #scan interval
        self.start_time = time.time()

        self.create_widgets()
        
    def create_widgets(self):
        self.left_frame = tk.Frame(self.window)
        self.left_frame.pack(side="left",padx=5, pady=5, fill="y")

        self.right_frame = tk.Frame(self.window)
        self.right_frame.pack(side="right", padx=5, pady=5, fill="y")

        self.video = tk.Label(self.right_frame) #show camera video 
        self.video.pack(side="top",anchor="ne")
        

        self.log_text = tk.Text(self.right_frame, font="microsoftYahei", width=54, height=9,state="disabled")
        self.log_text.pack(side="bottom", anchor="se")

        self.clear_butn = tk.Button(self.right_frame, font="microsoftYahei",height=1, text="clear log", command=self.clear_log)
        self.clear_butn.pack(side="bottom",anchor="sw")


        self.str_interval = tk.StringVar()
        self.str_interval.set(str(self.interval/1000))
        vcmd = (self.window.register(self.validate),"%P")
        ivcmd = (self.window.register(self.invalidate),)
        self.interval_label = tk.Label(self.left_frame, text="Scan interval:",font="microsoftYahei")
        self.interval_entry = ttk.Entry(self.left_frame, width=18, font="microsoftYahei", textvariable= self.str_interval,validate="focusout",validatecommand=vcmd,invalidcommand=ivcmd)#interval submit entry
        self.submit_button = tk.Button(self.left_frame, text="submit",height=1,width=11, command=self.submit,font="microsoftYahei")
        self.label_error = tk.Label(self.left_frame,fg="red")


        self.interval_label.grid(row=0, column=0,sticky=tk.E)
        self.interval_entry.grid(row=0, column=1,sticky=tk.W)
        self.label_error.grid(row=1,column=1,sticky=tk.NW)
        self.submit_button.grid(row=0, column=2)

        self.combobox_label = tk.Label(self.left_frame, text="Select camera:", font="microsoftYahei")
        self.combobox_label.grid(row=2, column=0, sticky=tk.E)

        self.camera_list = self.get_camera_list()
        self.camera_combobox = ttk.Combobox(self.left_frame, values=self.camera_list, font="microsoftYahei",state="readonly",width=18)
        self.camera_combobox.current(0)
        self.camera_combobox.grid(row=2,column=1,sticky=tk.W)

        self.switch_button = tk.Button(self.left_frame,text="open camera",height=1,width=11, command=self.combine_camera, font="microsoftYahei")
        self.switch_button.grid(row=2, column=2,sticky=tk.W)

        self.scan_code()

    def show_message(self,error='',color="black"):
        """
        show the error message
        """
        self.label_error['text'] = error
        self.interval_entry['foreground'] = color

    def validate(self,value):
        """
        scan interval entry validation rules
        """
        pattern = r'\d+(\.)?(\d+)?'
        if re.fullmatch(pattern,value) is None:
            return False
        self.show_message("")
        print("show ")
        return True

    def invalidate(self):
        self.show_message("scan interval must be a number","red")

    def submit(self):
        self.log_text.focus()
        try:
            self.interval = int(float(self.interval_entry.get())* 1000)

            user_prompt = str(self.interval/1000)
            self.log_text.config(state="normal")
            self.log_text.insert("end","System: Scan interval has been changed to "+user_prompt+" s\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        except ValueError:
            return False
    def clear_log(self):
        """
        clear log text 
        """

        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
    
    # get current device camera index
    def get_camera_list(self):
        index = 0
        camera_list = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                break
            else:
                camera_list.append("Camera {}".format(index))
            cap.release()
            index += 1
        return camera_list

    # control camera switch by button 
    def combine_camera(self):
        if self.cap == None:
            self.open_camera()
        else:
            self.close_camera()

    def open_camera(self):
        self.camera_idx = self.camera_combobox.current()
        self.cap = cv2.VideoCapture(self.camera_idx)
        if self.cap.isOpened():
            self.switch_button.config(text="close camera")

    def close_camera(self):
        self.cap.release()
        self.cap = None
        self.switch_button.config(text="open camera")

    # read video and capture frame then used to decode
    def scan_code(self):

        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                image_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_RGB = Image.fromarray(image_RGB)
                self.video_image = ImageTk.PhotoImage(image_RGB)
                self.video.config(image=self.video_image)
                elapsed_time = time.time() - self.start_time

                if int(elapsed_time * 1000) >= self.interval:
                    self.start_time = time.time()
                    barcodes = pyzbar.decode(frame)
                    for barcode in barcodes:
                        barcode_data = barcode.data.decode("utf-8")
                        barcode_type = barcode.type
                    
                        log = "code data: "+str(barcode_data) +"\n" + "code type: "+str(barcode_type)+"\n"
                        self.log_text.config(state="normal")
                        self.log_text.insert("end", log)
                        self.log_text.see("end")
                        self.log_text.config(state="disabled")
        
        self.window.after(1, self.scan_code)

if __name__ == "__main__":
    window = tk.Tk()
    window.title("barcode scanner")
    window.geometry("1500x800")
    app = codeScanner(window)
    window.mainloop()
    input("press Enter to continue...")
