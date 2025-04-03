#!/usr/bin/python
import time
import random
import requests
import os
from samplebase import SampleBase
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class QueueTimes(SampleBase):
    def __init__(self, *args, **kwargs):
        super(QueueTimes, self).__init__(*args, **kwargs)
        
        # Add park ID argument with default from .env
        self.parser.add_argument("-pa", "--park", help="The Park ID to display queue times for", 
                                default=os.getenv("PARK_ID", "16"))
        self.parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    def debug_print(self, message):
        if self.debug:
            print(f"DEBUG: {message}")

    def fetch_ride_data(self):
        self.debug_print("Fetching ride data...")
        url = f"https://queue-times.com/parks/{self.args.park}/queue_times.json"
        response = requests.get(url)
        data = response.json()
        rides = []
        for land in data["lands"]:
            rides.extend(land["rides"])
        self.debug_print(f"Fetched {len(rides)} rides")
        return rides

    def display_wait_time(self, ride):
        self.debug_print(f"Displaying information for {ride['name']}")
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        font_wait = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        name = ride['name']
        
        # Check if ride is open
        if ride['is_open']:
            wait = str(ride['wait_time'])
            wait_color = (0, 255, 0)  # Green
        else:
            wait = "DOWN"
            wait_color = (255, 0, 0)  # Red

        # Draw ride name (multiline)
        lines = []
        line = ""
        for word in name.split():
            if draw.textsize(line + " " + word, font=font_name)[0] <= 60:
                line += " " + word if line else word
            else:
                lines.append(line)
                line = word
        lines.append(line)

        y_offset = 2
        for line in lines[:3]:  # Limit to 3 lines
            draw.text((2, y_offset), line.strip(), font=font_name, fill=(255, 255, 0))
            y_offset += 12

        # Draw wait time or "DOWN"
        wait_width, wait_height = draw.textsize(wait, font=font_wait)
        draw.text(((64 - wait_width) // 2, 40), wait, font=font_wait, fill=wait_color)
        
        # Draw "min" only if the ride is open
        if ride['is_open']:
            draw.text((44, 54), "min", font=font_name, fill=wait_color)

        self.debug_print("Image created and drawn")
        self.matrix.SetImage(image)
        self.debug_print("Image set on matrix")

    def run(self):
        self.debug_print("Run method started")
        refresh_interval = int(os.getenv("REFRESH_INTERVAL", "5"))
        retry_interval = int(os.getenv("RETRY_INTERVAL", "10"))
        
        while True:
            try:
                self.debug_print("Entering main loop")
                rides = self.fetch_ride_data()
                random_ride = random.choice(rides)
                self.debug_print(f"Selected ride: {random_ride['name']}")
                self.display_wait_time(random_ride)
                self.debug_print(f"Waiting for {refresh_interval} seconds")
                time.sleep(refresh_interval)
            except Exception as e:
                print(f"An error occurred: {e}")
                self.debug_print(f"Waiting for {retry_interval} seconds before retrying")
                time.sleep(retry_interval)

    def process(self):
        self.args = self.parser.parse_args()
        
        # Override command-line with environment variables if provided
        if os.getenv("MATRIX_ROWS"):
            self.args.led_rows = int(os.getenv("MATRIX_ROWS"))
        if os.getenv("MATRIX_COLS"):
            self.args.led_cols = int(os.getenv("MATRIX_COLS"))
        if os.getenv("MATRIX_CHAIN"):
            self.args.led_chain = int(os.getenv("MATRIX_CHAIN"))
        if os.getenv("MATRIX_BRIGHTNESS"):
            self.args.led_brightness = int(os.getenv("MATRIX_BRIGHTNESS"))
        if os.getenv("MATRIX_GPIO_MAPPING"):
            self.args.led_gpio_mapping = os.getenv("MATRIX_GPIO_MAPPING")
        
        # Set debug mode from .env or command line argument
        self.debug = self.args.debug or self.debug
        
        return super(QueueTimes, self).process()

if __name__ == "__main__":
    queue_times = QueueTimes()
    if not queue_times.process():
        queue_times.print_help()