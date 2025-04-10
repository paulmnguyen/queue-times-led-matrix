#!/usr/bin/python
import time
import random
import requests
from samplebase import SampleBase
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

class Disneyland(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Disneyland, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--ride", help="The ride to scroll on the RGB LED panel", default="16")
        self.parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        self.debug = False

    def debug_print(self, message):
        if self.debug:
            print(f"DEBUG: {message}")

    def fetch_ride_data(self):
        self.debug_print("Fetching ride data...")
        url = "https://queue-times.com/parks/16/queue_times.json"
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
        font_wait = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        name = ride['name']
        
        # Check if ride is open
        if ride['is_open']:
            wait = str(ride['wait_time'])
            wait_color = (0, 255, 0)  # Green
        else:
            wait = "X"
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
        draw.text(((64 - wait_width) // 2, 43), wait, font=font_wait, fill=wait_color)
        
        # Draw "min" only if the ride is open
        if ride['is_open']:
            draw.text((44, 52), "min", font=font_name, fill=wait_color)

        self.debug_print("Image created and drawn")
        self.matrix.SetImage(image)
        self.debug_print("Image set on matrix")

    def run(self):
        self.debug_print("Run method started")
        while True:
            try:
                self.debug_print("Entering main loop")
                rides = self.fetch_ride_data()
                random_ride = random.choice(rides)
                self.debug_print(f"Selected ride: {random_ride['name']}")
                self.display_wait_time(random_ride)
                self.debug_print("Waiting for 5 seconds")
                time.sleep(5)
            except Exception as e:
                print(f"An error occurred: {e}")
                self.debug_print("Waiting for 10 seconds before retrying")
                time.sleep(10)

    def process(self):
        self.args = self.parser.parse_args()
        self.debug = self.args.debug
        return super(Disneyland, self).process()

if __name__ == "__main__":
    disneyland = Disneyland()
    if not disneyland.process():
        disneyland.print_help()
