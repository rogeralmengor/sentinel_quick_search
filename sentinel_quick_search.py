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
from tkcalendar import Calendar
from pandastable import Table, TableModel

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
        self.state("zoomed")
        self.folder = ""
        self.out_geojson = ""
        self.zip_files = []
        self.number_of_files = ""
        self.coordinates = []
        self.canvas_coordinates = []
        self.point_counter = 1

        # User inputs
        self.username = tk.StringVar() 
        self.password = tk.StringVar() 
        self.input_path = "" 
        self.output_folder = ""
        orbit_direction = "" 
        self.start_date = "YYYY-MM-DD" 
        self.end_date = "YYYY-MM-DD"
        self.footprints_path = "" 


        # ================= CTkFrames ============================== # 
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        self.frame_left = ctk.CTkFrame(master=self, 
                                        width = 150, 
                                        )

        self.frame_left.grid(row=0,
                            column=0,
                            padx=20,
                            pady=20,
                            sticky="nsew",
                            rowspan = 4)

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
        self.frame_bottom.grid(row=3,
                                column=1,
                                padx=20,
                                pady=5,
                                sticky="nsew",
                                columnspan=1)

        self.table_frame = ctk.CTkFrame(master = self, 
                                        corner_radius=5)
        #self.table_frame.grid(row=0,
        #                        column = 2,
        #                        padx=20,
        #                        pady=5,
        #                        sticky="nsew",
        #                        columnspan=1)
        
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
       
        # Credentials Label 

        # Label for platform type 
        self.label_credentials = ctk.CTkLabel(self.frame_left, text = "Copernicus scihub\ncredentials")
        self.label_credentials.place(relx=.5, rely=.1, anchor=CENTER)

        # Setting user name Entry 
        self.user_name_entry = Entry(self.frame_left,
                                    textvariable=self.username,
                                    width=20,
                                    justify="center")
        
        self.user_name_entry.insert(END, "username")
        self.user_name_entry.place(relx=.5, rely=.2, anchor = CENTER)
        self.user_name_entry.focus()
       
        # Settings password's Entry 
        self.password_entry = Entry(self.frame_left,
                                    textvariable=self.password,
                                    width=20,
                                    justify="center",
                                    show="*")

        self.password_entry.insert(END, "password")
        self.password_entry.place(relx=.5, rely=.3, anchor=CENTER) 
        self.password_entry.focus()
       

       # Setting buttons
        self.search_button = ctk.CTkButton(
            self.frame_bottom,
            text="Open..",
            command=self.save_file).grid(
            padx=5,
            pady=10,
            row=1,
            column=0,
            columnspan=1)

        self.run_button = ctk.CTkButton(
            self.frame_bottom,
            text="Run Query",
            command=self.run_query).grid(
            padx=5,
            pady=10,
            row=2,
            column=0,
            columnspan=1)

        self.display_file = Entry(self.frame_bottom, width=100,
                                    bg="white" ,textvariable=self.out_geojson)

        self.display_file.grid(padx=5, pady=10, sticky="w", row=1, column=1)

        # Label for platform type 
        self.label_platform_type = ctk.CTkLabel(self.frame_left, text = "Platform Type")
        self.label_platform_type.place(relx=.5, rely=.4, anchor=CENTER)

        # Canvas for radio button
        self.canvas_platforms = Canvas(self.frame_left, width=70, height=65, bg="#444444")
        self.canvas_platforms.place(relx=.5, rely=.55, anchor=CENTER)

        # RadioButtons 
        self.platform = IntVar()
        self.S1 = Radiobutton(self.canvas_platforms,
                                text="S-1",
                                variable=self.platform,
                                value=1,
                                command=self.sel, 
                                activeforeground="#000000",
                                bg="#444444", 
                                fg='#fff', 
                                relief=tk.FLAT,
                                bd=0,
                                selectcolor="#444444")
        self.S1.place(relx=.5, rely=.3, anchor = CENTER)

        self.S2 = Radiobutton(self.canvas_platforms,
                                text="S-2",
                                variable=self.platform,
                                value=2,
                                command=self.sel,
                                activeforeground="#000000",
                                bg="#444444",
                                fg='#fff',
                                relief=tk.FLAT,
                                bd=0,
                                selectcolor="#444444")
        self.S2.place(relx=.5, rely=.65, anchor = CENTER)

        # Add Calendar
        self.start_cal = Calendar(self.frame_left, selectmode = 'day',
                        year = 2020, month = 5,
                        day = 22)

        # Start Date  
        self.label_start_date = ctk.CTkLabel(self.frame_left, text = "Start Date")
        self.label_start_date.place(relx=.5, rely=.75, anchor=CENTER)
        self.button_start_date = ctk.CTkButton(self.frame_left,
                                    text = "YYYY-MM-DD",
                                    width=20)
        self.button_start_date.place(relx=.5, rely=.85, anchor = CENTER)

        # End Date
        self.label_end_date = ctk.CTkLabel(self.frame_left, text = "End Date")
        self.label_end_date.place(relx=.5, rely=.95, anchor=CENTER)
        self.button_end_date = ctk.CTkButton(self.frame_left,
                                    text = "YYYY-MM-DD",
                                    width=20)

        self.button_end_date.place(relx=.5, rely=1.05, anchor = CENTER)
        

        # Table Results 
        #self.canvas_table = Canvas(self.table_frame, width=70, height=65, bg="#444444")
        #self.canvas_table.place(relx=.5, rely=.55, anchor=CENTER)
        #self.canvas_table.pack(fill=BOTH)
        df = TableModel.getSampleData()
        print(df)
        self.table = pt = Table(self.table_frame, dataframe=df,
                                    showtoolbar=True, showstatusbar=True)
        #pt.show()

    def sel(self):
        selection = "You selected the option " + str(self.platform.get())
        print(selection)

    def save_file(self):
        self.footprints_path = filedialog.asksaveasfile(mode='w', defaultextension=".geojson").name
        self.display_file.delete(0, END)
        self.display_file.insert(0, self.footprints_path)


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


    def run_query(self): 
        print(self.username.get())
        print(self.password.get())


    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
