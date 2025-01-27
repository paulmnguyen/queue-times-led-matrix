# queue-times-led-matrix

LED Matrix project for displaying queue times from queue-times.com

## Description

This project uses a Raspberry Pi and an LED matrix to display real-time queue times for theme park attractions. Data is sourced from queue-times.com.

## Installation

1. Clone this repository:
   
   git clone https://github.com/yourusername/queue-times-led-matrix.git
   cd queue-times-led-matrix
   

2. Install dependencies:
   
   pip install -r requirements.txt
   

3. Set up the rpi-rgb-led-matrix library:
   
   git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
   cd rpi-rgb-led-matrix
   make -C examples-api-use
   

## Usage

Run the main script:


python main.py


## Configuration

Edit the `config.py` file to customize:

- LED matrix dimensions
- Refresh rate
- Theme parks and attractions to display

## Credits

- Queue time data provided by [queue-times.com](https://queue-times.com/)
- LED matrix control using [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library

## License

[MIT License](LICENSE)

## Components Used

- [64x64 RGB LED Matrix Panel](https://www.amazon.com/gp/product/B0BRBG71WS/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&th=1)
- Raspberry Pi (model used: [specify your Raspberry Pi model])
- [RGB Matrix Bonnet for Raspberry Pi](https://www.amazon.com/gp/product/B0BC8Y447G/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
