import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageColor, ImageTk
import threading

bg_color = "#6e5fa7"
secondary_color = "#7e52a1"
location_text: str = None
display_hourly_day_info = -1
daily_percentage = 70
done = False
close_program = False

condition = threading.Condition()


def get_image(kind: str, size: int, bg_color=bg_color):
    path = f"resources/{kind.replace(' ', '_')}.png"
    image = Image.open(path)
    image = image.convert("RGBA")
    background = Image.new(
        "RGBA", image.size, ImageColor.getcolor(str(bg_color), "RGBA")
    )
    background.paste(image, mask=image)
    background.thumbnail((size, size))
    background.convert("RGB")
    return background


def show_error(title="Error", message="Couldn't find that location on the map"):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(title, message)
    root.destroy()


def switch_frame(master, new_frame_class, **kwargs):
    # Remove current widgets
    for widget in master.winfo_children():
        widget.destroy()
    # Create and pack new frame
    new_frame = new_frame_class(master, **kwargs)
    new_frame.pack(fill="both", expand=True)
    return new_frame


def switch_to_existing_frame(master, frame_to_show):
    # Hide all frames inside master
    for widget in master.winfo_children():
        widget.pack_forget()
    # Show the existing frame
    frame_to_show.pack(fill="both", expand=True)


def clear_frame(frame: tk.Frame):
    master = frame.master
    for widget in master.winfo_children():
        widget.pack_forget()


class WeatherInfoBlock(tk.Frame):
    def __init__(
        self,
        master,
        top_text: str,
        image_text: str,
        bottom_text: str,
        size_percentage=100,
        bottom_size_percentage=100,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.time = tk.Label(
            self,
            text=top_text,
            font=("Arial", int(30 * size_percentage / 100)),
            bg=bg_color,
        )
        self.time.grid(row=0, column=0, sticky="ew")

        image = get_image(image_text, int(400 * size_percentage / 100))
        self.photo = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self, image=self.photo, bg=bg_color)
        self.image_label.grid(row=1, column=0, sticky="ew")

        self.temperature = tk.Label(
            self,
            text=bottom_text,
            font=("Arial", int(40 * size_percentage *
                  bottom_size_percentage / 10000)),
        )
        self.temperature.grid(row=2, column=0, sticky="ew")
        self.temperature.configure(bg=bg_color)


class HourlyFrame(tk.Frame):
    def __init__(self, master, hour_info: [], on_click=None, **kwargs):
        super().__init__(master, bg=bg_color, **kwargs)

        self.on_click_callback = on_click

        image = get_image("back-button", 50)
        photo = ImageTk.PhotoImage(image)
        btn = tk.Button(
            self,
            image=photo,
            command=lambda: self.on_click(master),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bg=bg_color,
            activebackground=bg_color,
            activeforeground=bg_color,
        )
        btn.image = photo
        btn.grid(column=0, row=0, sticky="ew", pady=5)
        self.button = btn

        for row in range(2):
            for column in range(4):
                list_index = row * 4 + column
                widget = WeatherInfoBlock(
                    self,
                    top_text=hour_info[list_index]["time"],
                    image_text=hour_info[list_index]["kind"],
                    bottom_text=str(
                        hour_info[list_index]["temperature"]) + "°",
                )
                widget.grid(row=row * 2 + 1, column=column *
                            2 + 1, padx=5, pady=5)

                if row < 1:
                    for column in range(4):
                        separator = tk.Frame(
                            self, height=2, bg=secondary_color)
                        separator.grid(
                            row=row * 2 + 2, column=column * 2 + 1, sticky="ew", pady=2
                        )

        separator = tk.Frame(self, height=2, bg=secondary_color)
        separator.grid(row=2, column=0, sticky="ew", pady=2)

    def on_click(self, master):
        global close_program
        close_program = False
        master.destroy()
        self.on_click_callback()


class SmallInfo(tk.Frame):
    def __init__(
        self,
        master,
        left_image_path: str,
        top_text: str,
        bottom_text: str,
        bg_color=bg_color,
        **kwargs,
    ):
        super().__init__(master, bg=bg_color, **kwargs)

        font_size = 20

        image = get_image(left_image_path, 64, bg_color)
        self.photo = ImageTk.PhotoImage(image)
        self.left_label = tk.Label(self, image=self.photo, bg=bg_color)
        self.left_label.pack(side="left")

        self.top_label = tk.Label(
            self, text=top_text, font=("Arial", font_size), bg=bg_color, pady=10
        )
        self.top_label.pack(side="top")

        self.bottom_label = tk.Label(
            self, text=bottom_text, font=("Arial", font_size), bg=bg_color
        )
        self.bottom_label.pack(side="bottom")


class TodayExclusiveInfo(tk.Frame):
    def __init__(self, master, info_list: [], **kwargs):
        super().__init__(master, bg=secondary_color, **kwargs)
        self.info_list = info_list
        for i, info in enumerate(info_list):
            info_block = SmallInfo(
                self,
                info["image_path"],
                info["top_text"],
                info["bottom_text"],
                secondary_color,
            )
            info_block.grid(row=i % 3, column=i % 2)


class BaseDayInfo(tk.Frame):
    def __init__(
        self,
        master,
        day_number: int,
        info_block: [],
        temperature_text: str,
        info_frame_class,
        info_frame_args=(),
        info_frame_kwargs=None,
        size_percentage: int = 100,
        **kwargs,
    ):
        # int(400 * size_percentage / 100)
        super().__init__(master, bg=bg_color, **kwargs)
        if info_frame_kwargs is None:
            info_frame_kwargs = {}

        self.right_frame = tk.Frame(self, bg=bg_color, **kwargs)

        self.temperature_text = tk.Label(
            self.right_frame,
            text=temperature_text + "°",
            font=("Arial", int(120 * size_percentage / 100)),
            bg=bg_color,
        )

        self.extra_info = info_frame_class(
            self.right_frame, *info_frame_args, **info_frame_kwargs
        )

        image = get_image("more", size=int(50 * size_percentage / 100))
        photo = ImageTk.PhotoImage(image)
        btn = tk.Button(
            self.right_frame,
            image=photo,
            # command=self.on_click,
            command=lambda: self.on_click(master, day_number),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bg=bg_color,
            activebackground=bg_color,
            activeforeground=bg_color,
        )
        btn.image = photo
        self.button = btn
        self.temperature_text.pack(
            side="top", pady=(100 * size_percentage / 100, 0))
        self.extra_info.pack(side="top")
        self.button.pack(side="bottom")

        self.left_frame = tk.Frame(self, bg=bg_color, **kwargs)
        self.info_block = WeatherInfoBlock(
            self.left_frame,
            info_block["top_text"],
            info_block["image_path"],
            info_block["bottom_text"],
            size_percentage=size_percentage,
            bottom_size_percentage=50,
        )
        self.info_block.pack(side="right")
        self.left_frame.pack(side="left")
        self.right_frame.pack(side="right")
        self.pack()

    def on_click(self, master, day_number):
        global display_hourly_day_info
        display_hourly_day_info = day_number
        self.winfo_toplevel().destroy()


class TodayInfo(tk.Frame):
    def __init__(
        self,
        master,
        info_block: [],
        today_exclusive_info_list: [],
        temperature_text: str,
        size_percentage: int = 100,
        command=None,
        **kwargs,
    ):
        super().__init__(master, bg=bg_color, **kwargs)
        self.master = master
        self.dayly_info = BaseDayInfo(
            self,
            day_number=0,
            info_block=info_block,
            info_frame_class=TodayExclusiveInfo,
            info_frame_args=(today_exclusive_info_list,),
            size_percentage=size_percentage,
            temperature_text=temperature_text,
        )
        self.left_frame = self.dayly_info.left_frame
        location_image = get_image("location", 50)
        self.location_photo = ImageTk.PhotoImage(location_image)
        self.location = tk.Frame(self, bg=bg_color, **kwargs)
        self.location_btn = tk.Button(
            self.location,
            image=self.location_photo,
            command=command,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bg=bg_color,
            activebackground=bg_color,
            activeforeground=bg_color,
        )
        self.location_label = tk.Label(
            self.location, bg=bg_color, text=location_text, font=("Arial", 20)
        )
        self.location_btn.pack(side="left", pady=(0, 10))
        self.location_label.pack(side="right")
        self.location.pack(side="top")
        self.dayly_info.pack(side="bottom")

    def clear_master(self, master):
        for widget in master.winfo_children():
            widget.pack_forget()

    def on_second_click(self, master, **kwargs):
        self.clear_master(master)
        self.current_frame = LocationSelectFrame(master, **kwargs)
        self.current_frame.pack(fill="both", expand=True)


class DailyInfo(tk.Frame):
    def __init__(
        self,
        master,
        day_number: int,
        info_block: [],
        extra_info: str,
        temperature_text: str,
        size_percentage: int = 100,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.info = BaseDayInfo(
            self,
            day_number=day_number,
            info_block=info_block,
            info_frame_class=tk.Label,
            info_frame_args=(),
            info_frame_kwargs={
                "bg": bg_color,
                "text": extra_info,
                "font": ("Arial", 28),
            },
            temperature_text=temperature_text,
            size_percentage=size_percentage,
        )


class DailyFrame(tk.Frame):
    def __init__(
        self,
        master,
        restart_funcion,
        left_info_block: [[], [], []],
        today_exclusive_info_list: [],
        temperature_text_list: [str, str, str],
        extra_info_subsequent_days: [str, str],
        size_percentage: int = 100,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        global done
        done = False
        global display_hourly_day_info
        display_hourly_day_info = -1
        daily_percentage = 70
        today_percentage = 100
        self.restart_funcion = restart_funcion
        self.right = tk.Frame(self, bg="black")
        self.left = tk.Frame(self)
        self.day_0 = TodayInfo(
            self.left,
            info_block=left_info_block[0],
            today_exclusive_info_list=today_exclusive_info_list,
            temperature_text=temperature_text_list[0],
            size_percentage=today_percentage * size_percentage / 100,
            command=lambda: self.switch_to_location_frame(master, **kwargs),
        )
        self.day_0.pack()

        self.day_1 = DailyInfo(
            self.right,
            day_number=1,
            info_block=left_info_block[1],
            extra_info=extra_info_subsequent_days[0],
            temperature_text=temperature_text_list[1],
            size_percentage=daily_percentage * size_percentage / 100,
        )

        self.day_2 = DailyInfo(
            self.right,
            day_number=2,
            info_block=left_info_block[2],
            extra_info=extra_info_subsequent_days[1],
            temperature_text=temperature_text_list[2],
            size_percentage=daily_percentage * size_percentage / 100,
        )

        self.day_1.pack(side="top", pady=(6, 0), padx=(6, 0))
        self.day_2.pack(side="bottom", pady=(6, 6), padx=(6, 0))

        self.left.pack(side="left")
        self.right.pack(side="right")

    def switch_to_location_frame(self, master, **kwargs):
        clear_frame(self)
        self.current_frame = LocationSelectFrame(
            master, self.restart_funcion, frame_to_switch_on_enter=self, **kwargs
        )
        self.current_frame.pack(fill="both", expand=True)


class LocationSelectFrame(tk.Frame):
    def __init__(
        self, master, restart_funcion, frame_to_switch_on_enter=tk.Frame, **kwargs
    ):
        super().__init__(master, **kwargs)
        self.frame_to_switch_on_enter = frame_to_switch_on_enter
        self.current_frame = master
        self.restart_funcion = restart_funcion

        self.location_label = tk.Label(
            master,
            bg=bg_color,
            text="Enter a location below:",
            font=("Arial", 40),
            pady=15,
        )
        self.entry = tk.Entry(master, font=("Arial", 40), **kwargs)
        self.entry.bind("<Return>", lambda event: self.on_enter(event, master))

        self.location_label.pack()
        self.entry.pack()

    def on_enter(self, event, master):
        value = self.entry.get()
        global location_text
        location_text = value
        master.destroy()
        global done
        done = True
