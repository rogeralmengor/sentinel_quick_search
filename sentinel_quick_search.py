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

        super().__init__(*args, **kwargs)
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        self.folder = ""
        self.out_geojson = ""
        self.zip_files = []
        self.number_of_files = ""
        self.coordinates = []
        self.canvas_coordinates = []
        self.point_counter = 1

        # User inputs
        self.password = "password"
        self.username = "username"
        self.input_path = "" 
        self.output_folder = ""
        orbit_direction = "" 
        start_date = "" 
        end_date = ""


        # ================= CTkFrames ============================== # 
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        self.frame_left = ctk.CTkFrame(master=self, 
                                        width = 150)

        self.frame_left.grid(row=0,
                            column=0,
                            padx=20,
                            pady=20,
                            sticky="nsew")

        self.frame_right = ctk.CTkFrame(master=self, 
                                        corner_radius=10)
        self.frame_right.grid(row=0,
                            column=1,
                            rowspan=1,
                            pady=20,
                            padx=20,
                            sticky="nsew")

        self.frame_bottom = ctk.CTkFrame(master=self, 
                                        corner_radius=5)
        self.frame_bottom.grid(row=2,
                                column=0,
                                padx=20,
                                pady=10,
                                sticky="nsew",
                                columnspan=2)
        
        #  Map View and Map Functionalities
        self.map_widget = TkinterMapView(self.frame_right, 
                                        width=500, 
                                        height=250, 
                                        corner_radius=10, 
                                        relief=SUNKEN,
                                        )      
        
        self.map_widget.grid(row=0, 
                            rowspan=1, 
                            column=0,
                            columnspan=2, 
                            sticky="nswe", 
                            padx=20, 
                            pady=20)

        self.map_widget.add_right_click_menu_command(label = "Add Point",
                                                    command = self.add_marker_event,
                                                    pass_coords=True)

        self.map_widget.add_right_click_menu_command(label = "Create AOI",
                                                    command = self.create_polygon,
                                                    pass_coords=False)

        self.user_name_entry = Entry(self.frame_left, width=20, justify="center")
        self.user_name_entry.insert(END, self.username)
        self.user_name_entry.place(relx=.5, rely=.1, anchor = CENTER)
        
        self.password_entry = Entry(self.frame_left, width=20, justify="center")
        self.password_entry.insert(END, self.password)
        self.password_entry.place(relx=.5, rely=.2, anchor=CENTER) 
        
        self.search_button = ctk.CTkButton(
            self.frame_bottom,
            text="Open..",
            command=self.save_file).grid(
            padx=5,
            pady=10,
            row=1,
            column=0,
            columnspan=1)


        self.display_file = Entry(self.frame_bottom, width=80,
                                    bg="white" ,textvariable=self.out_geojson)
        self.display_file.grid(padx=5, pady=10, sticky="w", row=1, column=1)


    def save_file(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".geojson").name
        self.display_file.delete(0, END)
        self.display_file.insert(0, filename)


    def update_path(self, close_path=False):

        """Updates path based on coordinates stored as markers"""
        if close_path == True:
            x = self.coordinates[0][0]
            y = self.coordinates[0][1]
            self.map_widget.set_marker(x, y) 
            self.canvas_coordinates.append(self.osm_to_decimal(x,y,self.map_widget.zoom))
            self.coordinates.append((x,y))
            self.map_widget.set_path(self.coordinates)
        else: 
            self.map_widget.set_path(self.coordinates)


    def osm_to_decimal(self, tile_x: int, tile_y: int, zoom: int) -> tuple:
        
        """ converts internal OSM coordinates to decimal coordinates """

        n = 2.0 ** zoom
        lon_deg = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg


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
