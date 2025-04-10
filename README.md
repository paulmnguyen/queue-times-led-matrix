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

### Quick Start

1. Run the start script:
   ```
   ./start-matrix.sh
   ```
   This will create a default `.env` file if it doesn't exist and start the matrix.

2. To install dependencies and start:
   ```
   ./start-matrix.sh --install
   ```

### For Automatic Startup

1. Run the service installer:
   ```
   ./install-service.sh
   ```

2. The script will now start automatically on boot. You can control it with:
   ```
   sudo systemctl start queue-times-matrix
   sudo systemctl stop queue-times-matrix
   sudo systemctl status queue-times-matrix
   ```

## Configuration

Edit the `.env` file to customize:

- LED matrix dimensions (`MATRIX_ROWS`, `MATRIX_COLS`, `MATRIX_CHAIN`)
- Park ID (`PARK_ID`) - default is 16 for Disneyland
- Refresh intervals (`REFRESH_INTERVAL`, `RETRY_INTERVAL`)
- Debug mode (`DEBUG`)

## Credits

- Queue time data provided by [queue-times.com](https://queue-times.com/)
- LED matrix control using [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library

## License

[MIT License](LICENSE)

## Components Used

- [64x64 RGB LED Matrix Panel](https://www.amazon.com/gp/product/B0BRBG71WS/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&th=1)
- Raspberry Pi 3
- [RGB Matrix Bonnet for Raspberry Pi](https://www.amazon.com/gp/product/B0BC8Y447G/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
