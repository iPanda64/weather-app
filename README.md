# Python Weather Application

This is a Python-based weather application that provides a graphical user interface (GUI) to display the current weather and a 3-day forecast.

## Features

  * **3-Day Forecast**: View a detailed forecast for today and a summary for the next two days.
    <p align="center">
     <img src="https://github.com/iPanda64/weather-app/blob/main/screenshots/1.png" alt="Screenshot 1" width="500" />
    </p>
  * **Location Search**: Get weather information for any city or country you search. The app saves your last searched location.
    <p align="center">
     <img src="https://github.com/iPanda64/weather-app/blob/main/screenshots/3.png" alt="Screenshot 3" width="300" />
    </p>
  * **Hourly Forecast**: Click on any day to see a detailed hour-by-hour breakdown.
    <p align="center">
     <img src="https://github.com/iPanda64/weather-app/blob/main/screenshots/2.png" alt="Screenshot 2" width="500" />
  </p>
  
## Installation

1.  **Download and install Python3 from [here](https://www.python.org/downloads/)**
2.  **Clone the repository**:

    ```bash
    git clone https://github.com/iPanda64/weather-app.git
    cd weather-app
    ```
3.  **Create and activate a virtual environment**:
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # On Windows
    py -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Install dependencies**: All required packages are listed in the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

## How to Run

Once the dependencies are installed, you can start the application by running the following command:

```bash
python3 weather.py
```
