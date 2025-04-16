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
load_dotenv(override=True)

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
        font_wait = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        
        # Use matrix dimensions from args instead of hardcoded values
        width = self.args.led_cols * self.args.led_chain
        height = self.args.led_rows
        self.debug_print(f"Matrix dimensions: width={width}, height={height}")
        self.debug_print(f"Matrix settings: cols={self.args.led_cols}, chain={self.args.led_chain}, rows={self.args.led_rows}")
        
        self.debug_print(f"Creating image with dimensions: {width}x{height}")
        image = Image.new("RGB", (width, height))
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
        max_width = width 
        
        # Split ride name into words
        for word in name.split():
            # Measure text width safely
            try:
                # Use getbbox() for newer Pillow versions or fallback to textsize
                if hasattr(draw, "textbbox"):
                    # Get width using textbbox (newer Pillow versions)
                    _, _, text_width, _ = draw.textbbox((0, 0), line + " " + word if line else word, font=font_name)
                else:
                    # Fallback to textsize for older Pillow versions
                    text_width, _ = draw.textsize(line + " " + word if line else word, font=font_name)
                
                # Add word to current line or start new line if too wide
                if text_width <= max_width:
                    line += " " + word if line else word
                else:
                    lines.append(line)
                    line = word
            except Exception as e:
                self.debug_print(f"Error measuring text: {e}")
                # Fallback method if text measuring fails
                if len(line + " " + word) > 20:  # Rough estimate
                    lines.append(line)
                    line = word
                else:
                    line += " " + word if line else word
        
        # Add the last line
        if line:
            lines.append(line)

        # Draw name lines with limited height - strictly 3 lines max, no left padding
        y_offset = 2
        for line in lines[:3]:  # Always limit to 3 lines exactly
            draw.text((0, y_offset), line.strip(), font=font_name, fill=(255, 255, 0))
            y_offset += 12

        # Handle "DOWN" indication with larger X
        if not ride['is_open']:
            # Use larger font for "DOWN" indication (X)
            font_down = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            try:
                if hasattr(draw, "textbbox"):
                    # Get dimensions using textbbox (newer Pillow versions)
                    _, _, wait_width, wait_height = draw.textbbox((0, 0), wait, font=font_down)
                else:
                    wait_width, wait_height = draw.textsize(wait, font=font_down)
            except Exception as e:
                self.debug_print(f"Error measuring wait text: {e}")
                wait_width = len(wait) * 20  # Rough estimate for larger font
                wait_height = 30
            
            # Position X centered in bottom half of display
            wait_y = height - wait_height - 10
            wait_x = (width - wait_width) // 2  # Center horizontally
            draw.text((wait_x, wait_y), wait, font=font_down, fill=wait_color)
        else:
            # Regular font for normal wait times
            try:
                if hasattr(draw, "textbbox"):
                    # Get dimensions using textbbox (newer Pillow versions)
                    _, _, wait_width, wait_height = draw.textbbox((0, 0), wait, font=font_wait)
                else:
                    wait_width, wait_height = draw.textsize(wait, font=font_wait)
            except Exception as e:
                self.debug_print(f"Error measuring wait text: {e}")
                wait_width = len(wait) * 12  # Rough estimate
                wait_height = 20
            
            # Measure "min" text
            try:
                if hasattr(draw, "textbbox"):
                    _, _, min_width, min_height = draw.textbbox((0, 0), "min", font=font_name)
                else:
                    min_width, min_height = draw.textsize("min", font=font_name)
            except Exception as e:
                self.debug_print(f"Error measuring min text: {e}")
                min_width = 20  # Rough estimate
                min_height = 10
            
            # Position wait time in bottom right
            wait_y = height - wait_height - 5
            wait_x = width - wait_width - min_width - 7  # Allow space for "min"
            
            # Draw wait time
            draw.text((wait_x, wait_y), wait, font=font_wait, fill=wait_color)
            
            # Draw "min" next to wait time, bottom-aligned
            min_x = wait_x + wait_width + 2
            min_y = wait_y + wait_height - min_height  # Bottom-align with wait time
            draw.text((min_x, min_y), "min", font=font_name, fill=wait_color)

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
        # Set debug mode from env first so we can debug the parsing
        if os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"):
            self.debug = True
            
        self.debug_print("Process method starting")
        self.debug_print(f"Environment variables: MATRIX_ROWS={os.getenv('MATRIX_ROWS')}, MATRIX_COLS={os.getenv('MATRIX_COLS')}, MATRIX_CHAIN={os.getenv('MATRIX_CHAIN')}")
        
        # Manually override defaults before parsing
        if os.getenv("MATRIX_ROWS"):
            self.parser.set_defaults(led_rows=int(os.getenv("MATRIX_ROWS")))
            self.debug_print(f"Setting default rows from .env: {os.getenv('MATRIX_ROWS')}")
        if os.getenv("MATRIX_COLS"):
            self.parser.set_defaults(led_cols=int(os.getenv("MATRIX_COLS")))
            self.debug_print(f"Setting default cols from .env: {os.getenv('MATRIX_COLS')}")
        if os.getenv("MATRIX_CHAIN"):
            self.parser.set_defaults(led_chain=int(os.getenv("MATRIX_CHAIN")))
            self.debug_print(f"Setting default chain from .env: {os.getenv('MATRIX_CHAIN')}")
        if os.getenv("MATRIX_BRIGHTNESS"):
            self.parser.set_defaults(led_brightness=int(os.getenv("MATRIX_BRIGHTNESS")))
        if os.getenv("MATRIX_GPIO_MAPPING"):
            self.parser.set_defaults(led_gpio_mapping=os.getenv("MATRIX_GPIO_MAPPING"))
            
        # Parse args after setting defaults
        self.args = self.parser.parse_args()
        self.debug_print(f"After parsing: rows={self.args.led_rows}, cols={self.args.led_cols}, chain={self.args.led_chain}")
        
        # Set debug mode from command line argument, overriding env
        self.debug = self.args.debug or self.debug
        
        # Apply additional env settings
        if os.getenv("MATRIX_SLOWDOWN_GPIO"):
            self.args.led_slowdown_gpio = int(os.getenv("MATRIX_SLOWDOWN_GPIO"))
            self.debug_print(f"Setting slowdown from .env: {self.args.led_slowdown_gpio}")
        if os.getenv("MATRIX_MULTIPLEXING"):
            self.args.led_multiplexing = int(os.getenv("MATRIX_MULTIPLEXING"))
            self.debug_print(f"Setting multiplexing from .env: {self.args.led_multiplexing}")
        if os.getenv("MATRIX_NO_HARDWARE_PULSE") and os.getenv("MATRIX_NO_HARDWARE_PULSE").lower() in ("true", "1", "yes"):
            self.args.led_no_hardware_pulse = 1
            self.debug_print("Disabling hardware pulse")
        
        # Always print matrix configuration at startup regardless of debug mode
        print(f"[Matrix Configuration] rows={self.args.led_rows}, cols={self.args.led_cols}, chain={self.args.led_chain}, width={self.args.led_cols * self.args.led_chain}, height={self.args.led_rows}")
        
        # Use super method to create the matrix
        result = super(QueueTimes, self).process()
        
        # Debug the actual matrix after creation to find discrepancy
        options = self.matrix._options
        print(f"[Actual Matrix] rows={options.rows}, cols={options.cols}, chain_length={options.chain_length}")
        
        return result

if __name__ == "__main__":
    queue_times = QueueTimes()
    if not queue_times.process():
        queue_times.print_help()
