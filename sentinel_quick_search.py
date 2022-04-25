import os
from turtle import update
from zipfile import ZipFile
import tkinter as tk
from tkinter import Frame
from tkinter import Label
from tkinter import GROOVE
from tkinter import LEFT
from tkinter import TOP
from tkinter import Button
from tkinter import SUNKEN
from tkinter import W
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from tkinter import Tk
import tkintermapview 
import customtkinter as ctk
from tkintermapview import TkinterMapView
import math
from tkinter import * 


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class App(ctk.CTk):

    APP_NAME = "Sentinel-Quick-Search"
    WIDTH = 800
    HEIGHT = 500

    """Main frame to add widgets to the app."""

    def __init__(self, *args, **kwargs):

        #self.master = master
        super().__init__(*args, **kwargs)
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        self.folder = ""
        self.zip_files = []
        self.number_of_files = ""
        self.coordinates = []
        self.canvas_coordinates = []
        self.point_counter = 1 

#       Logo Frame
        #path = "sentinel_quick_search_logo.gif"
        #self.image = tk.PhotoImage(file=path)
        #self.larger_image = self.image.zoom(2, 2)
        #self.smaller_image = self.image.subsample(8, 8)
        #self.logo = Label(
        #    master, image=self.smaller_image).pack(
        #    side=TOP, padx=5)
        
        #self.black_space_00 = Label(self, text="").pack(side=TOP, padx=5)

        # ================= CTkFrames ============================== # 
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        self.frame_left = ctk.CTkFrame(master=self, 
                                        width = 150)
        self.frame_left.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame_right = ctk.CTkFrame(master=self, 
                                        corner_radius=10)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=20, padx=20, sticky="nsew")
        
        #  Map View and Map Functionalities
        #self.canvas = ctk.CTkCanvas(self, width=800, height=500, bg="black", relief=SUNKEN)
        #self.canvas.pack(side=TOP)
        self.map_widget = TkinterMapView(self.frame_right, 
                                        width=450, 
                                        height=250, 
                                        corner_radius=10, 
                                        relief=SUNKEN)      
        self.map_widget.grid(row=0, 
                            rowspan=1, 
                            column=0, 
                            columnspan=3, 
                            sticky="nswe", 
                            padx=20, 
                            pady=20)
        
        self.map_widget.add_right_click_menu_command(label = "Add Point",
                                                    command = self.add_marker_event,
                                                    pass_coords=True)

        self.map_widget.add_right_click_menu_command(label = "Create AOI",
                                                    command = self.create_polygon,
                                                    pass_coords=False)

        #self.black_space_00_1 = Label(self, text="").pack(side=TOP, padx=5)

        
        # Frame: browse folder
#        self.search_folder_frame = ctk.CTkFrame(self, width=150, height=30,
#                                         relief=GROOVE, borderwidth=4)
#
#        self.blank_label = Label(
#            self.search_folder_frame,
#            text="").pack(
#            side=TOP,
#            padx=5)
#
#        self.search_button = ctk.CTkButton(
#            self.search_folder_frame,
#            text="Open..",
#            command=self.browse_folder).pack(
#            side=LEFT,
#            padx=5,
#            pady=10)
#
#        self.display_folder = Label(self.search_folder_frame, width=80,
#                                    bg="white", textvariable=self.folder,
#                                    relief=SUNKEN, anchor=W)
#
#        self.display_folder.pack(side=LEFT)
#
#        self.input_folder_label = Label(
#            self.search_folder_frame,
#            text="Input Folder",
#            relief=GROOVE).place(
#            relx=0.70,
#            rely=0.20,
#            anchor=W)
#
#        self.search_folder_frame.pack(side=TOP)
#
#        self.black_space_01 = Label(self, text="").pack(side=TOP, padx=5)
#
#        # Frame: number of files
#
#        self.number_files_frame = ctk.CTkFrame(self, width=150, height=30,
#                                        relief=GROOVE, borderwidth=4)
#
#        self.list_files_button = ctk.CTkButton(
#            self.number_files_frame,
#            text="Search .zip",
#            command=self.list_tar).pack(
#            side=LEFT,
#            padx=5,
#            pady=10)
#
#        self.display_num_zips = Label(
#            self.number_files_frame,
#            width=10,
#            bg="white",
#            textvariable=self.number_of_files,
#            relief=SUNKEN,
#            anchor=W)
#
#        self.display_num_zips.pack(side=LEFT)
#
#        self.number_files_frame.pack(side=TOP)
#
#        self.blank_space_02 = Label(self, text="").pack(side=TOP, padx=5)
#
#        self.run_button_frame = ctk.CTkFrame(self, width=150, height=30,
#                                      relief=GROOVE, borderwidth=4)
#        self.run_button = ctk.CTkButton(self.run_button_frame, text="Run",
#                                 command=self.unzip_files).pack(
#                side=LEFT, padx=5, pady=10)
#
#        self.run_button_frame.pack(side=TOP)
#
#
#    def browse_folder(self):
#        
#        """Command to browse folder."""
#
#        folder_name = askdirectory()
#        self.folder = folder_name
#        self.display_folder.config(text=folder_name)
#
#    def list_tar(self):
#
#        """Creates a list of zip files."""
#
#        files = [
#            os.path.join(
#                root, file) for root, subdir, files in os.walk(
#                self.folder) for file in files if file.endswith('.zip')]
#        self.zip_files = files
#        self.display_num_zips.config(text=str(len(self.zip_files)))
#        print(self.zip_files)
#        print(str(len(self.zip_files)))
#
#        return files
#
#    def unzip_files(self):
#
#        """Unzip files from a list."""
#
#        if len(self.zip_files) == 0:
#            messagebox.showerror("Error", "No zip files in this folder")
#
#        else:
#            for file in self.zip_files:
#                zip_obj = ZipFile(file, 'r')
#                zip_obj.extractall(self.folder)
#                print(f"extracted {file}\n{'-'*75}")
#
#
#    def update_path(self, close_path=False):
#
#        """Updates path based on coordinates stored as markers"""
#        if close_path == True:
#            x = self.coordinates[0][0]
#            y = self.coordinates[0][1]
#            self.map_widget.set_marker(x, y) 
#            self.canvas_coordinates.append(self.osm_to_decimal(x,y,self.map_widget.zoom))
#            self.coordinates.append((x,y))
#            self.map_widget.set_path(self.coordinates)
#        else: 
#            self.map_widget.set_path(self.coordinates)
#
#
#    def osm_to_decimal(self, tile_x: int, tile_y: int, zoom: int) -> tuple:
#        
#        """ converts internal OSM coordinates to decimal coordinates """
#
#        n = 2.0 ** zoom
#        lon_deg = tile_x / n * 360.0 - 180.0
#        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
#        lat_deg = math.degrees(lat_rad)
#        return lat_deg, lon_deg
#
#
    def add_marker_event(self, coords):
        x = coords[0]
        y = coords[1] 
        print("Add marker:", coords)
        self.map_widget.set_marker(x, y, text = "P" + "_" + \
                                            str(self.point_counter))
        self.point_counter = self.point_counter + 1
        self.canvas_coordinates.append(self.osm_to_decimal(x,y,self.map_widget.zoom))
        self.coordinates.append((x, y))
        print(self.coordinates)
        self.update_path()


    def create_polygon(self):
        print("coordinates after transformation..")
        if len(self.coordinates) < 3:
            print("Cannot create polygon with less than three points..")
        else:
            self.update_path(close_path=True) 
            self.map_widget.set_polygon(self.coordinates)

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
