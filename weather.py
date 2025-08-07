import python_weather
import asyncio
import os
import tkinter as tk
import fetcher
import gui

location_file = "location.txt"


def read_from_file():
    if os.path.exists(location_file):
        with open(location_file, "r") as f:
            city = f.read().strip()
            if city:
                return city
    return "New-York"  # default


def save_to_file(city):
    with open(location_file, "w") as f:
        f.write(city)


def init_root():
    root = tk.Tk()
    root.configure(bg=gui.bg_color)
    root.title("Python Weather")
    return root


today_exclusive_info_list = [
    {
        "image_path": "humidity",
        "top_text": "   Humidity   ",
        "bottom_text": "Details 1",
    },
    {
        "image_path": "wind_direction",
        "top_text": "Wind Direction",
        "bottom_text": "Details 2",
    },
    {"image_path": "eye", "top_text": "  Visibility  ", "bottom_text": "Details 3"},
    {
        "image_path": "wind_speed",
        "top_text": "  Wind Speed  ",
        "bottom_text": "Details 4",
    },
    {"image_path": "similar", "top_text": "  Feels Like  ", "bottom_text": "Details 5"},
    {
        "image_path": "moon_phase",
        "top_text": "  Moon Phase  ",
        "bottom_text": "Details 6",
    },
]
left_info = None
hourly_info = None


def example():
    hourly_list = [
        {
            "time": "00:00",
            "kind": "fog",
            "temperature": 20,
            "humidity": 50,
        },
        {
            "time": "01:00",
            "kind": "cloudy",
            "temperature": 21,
            "humidity": 51,
        },
        {
            "time": "02:00",
            "kind": "heavy_rain",
            "temperature": 22,
            "humidity": 52,
        },
        {
            "time": "03:00",
            "kind": "light_snow",
            "temperature": 23,
            "humidity": 53,
        },
        {
            "time": "04:00",
            "kind": "fog",
            "temperature": 24,
            "humidity": 54,
        },
        {
            "time": "05:00",
            "kind": "cloudy",
            "temperature": 25,
            "humidity": 55,
        },
        {
            "time": "06:00",
            "kind": "heavy_rain",
            "temperature": 26,
            "humidity": 56,
        },
        {
            "time": "07:00",
            "kind": "light_snow",
            "temperature": 27,
            "humidity": 57,
        },
    ]
    for item in hourly_list:
        item["temperature"] = str(item["temperature"])
    return hourly_list


def get_left_info():
    result_list = []
    fetched_info = fetcher.get_all_days()
    fetched_kind = fetcher.get_all_days_kind()
    result_list = [
        {
            "image_path": fetched_kind[0],
            "top_text": fetched_info[0]["time"],
            "bottom_text": fetched_info[0]["weekday"],
        },
        {
            "image_path": fetched_kind[1],
            "top_text": fetched_info[1]["time"],
            "bottom_text": fetched_info[1]["weekday"],
        },
        {
            "image_path": fetched_kind[2],
            "top_text": fetched_info[2]["time"],
            "bottom_text": fetched_info[2]["weekday"],
        },
    ]
    return result_list


def start_all_days_frame():
    root = init_root()
    all_days_info = fetcher.get_all_days()
    temp_list = []
    for day_info in all_days_info:
        temp_list.append(str(day_info["temperature"]))
    extra_info = [all_days_info[1]["moon"], all_days_info[2]["moon"]]
    frame = gui.DailyFrame(
        root,
        restart_funcion=start_all_days_frame,
        left_info_block=get_left_info(),
        today_exclusive_info_list=get_today_exclusive_info_list(),
        temperature_text_list=temp_list,
        extra_info_subsequent_days=extra_info,
        bg=gui.bg_color,
    )

    frame.pack()
    root.mainloop()


def get_today_exclusive_info_list():
    today = fetcher.get_today()
    global today_exclusive_info_list
    today_exclusive_info_list[0]["bottom_text"] = str(today["humidity"]) + "%"
    today_exclusive_info_list[1]["bottom_text"] = today["wind_direction"]
    today_exclusive_info_list[2]["bottom_text"] = str(
        today["visibility"]) + " km"
    today_exclusive_info_list[3]["bottom_text"] = str(
        today["wind_speed"]) + " km/h"
    today_exclusive_info_list[4]["bottom_text"] = str(
        today["feels_like"]) + "°"
    today_exclusive_info_list[5]["bottom_text"] = today["moon"]
    return today_exclusive_info_list


def start_hourly_frame(hourly_info):
    root = init_root()
    frame = gui.HourlyFrame(root, hour_info=hourly_info, on_click=lambda: None)

    frame.pack()
    root.mainloop()


async def main() -> None:
    location = read_from_file()
    fetcher.city = location
    gui.location_text = location
    await fetcher.fetch_weather(gui.location_text)
    global left_info
    left_info = get_left_info()
    try:
        while not gui.close_program:
            gui.close_program = True
            gui.done = True
            while gui.done:
                start_all_days_frame()
                try:
                    await fetcher.fetch_weather(gui.location_text)
                    fetcher.city = gui.location_text
                    location = gui.location_text
                except (ValueError, python_weather.RequestError):
                    gui.show_error()
                    gui.close_program = True
                    break

            if gui.display_hourly_day_info != -1:
                global hourly_info
                hourly_info = fetcher.get_hour(gui.display_hourly_day_info)
                start_hourly_frame(hourly_info)
    finally:
        save_to_file(location)


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
