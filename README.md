# 🖱️ Hand Gesture Mouse Controller

A modern, intuitive way to control your computer mouse using hand gestures captured through your webcam. This project leverages cutting-edge computer vision and hand tracking technology to create a natural interface for computer interaction.

## ✨ Features

- 🖱️ **Mouse Movement**: Precise cursor control using your index finger
- 🔵 **Left Click**: Natural clicking motion with half-folded fingers
- 🔴 **Right Click**: Intuitive two-finger gesture
- ✋ **Drag and Drop**: Seamless drag operations using thumb combinations
- 📜 **Scrolling**: Smooth scrolling with three-finger gestures
- 🎯 **Hand Orientation Detection**: Smart position recognition prevents accidental inputs
- 🎮 **Smooth Movement**: Enhanced cursor precision with intelligent smoothening

## ✨ Key Features


## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hand-gesture-mouse-controller.git
cd hand-gesture-mouse-controller
```
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python MouseController2.py
```

## Usage

1. Run the main script:
```bash
python MouseController2.py
```

2. Position your hand in front of the webcam
3. Use the following gestures:
   - **Move Cursor**: Raise only index finger
   - **Left Click**: Half-fold fingers in [0,1,0,0,0] configuration
   - **Right Click**: Raise index and middle fingers close together
   - **Drag**: Use thumb with specific finger combination
   - **Scroll**: Raise three fingers (index, middle, ring)

## Configuration

You can adjust various parameters in the code:
- `frameR`: Frame reduction for gesture detection area
- `smoothening`: Cursor movement smoothening factor
- Gesture configurations in `fingerConfig` dictionary

## Project Structure

- `MouseController2.py`: Main application file
- `HandTrackingModule.py`: Hand tracking and gesture detection module
- `HandGestureMin.py`: Minimal implementation example
- `HandGestureMouseControl.py`: Alternative implementation
- `MouseController.py`: Legacy version

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe for hand tracking capabilities
- OpenCV for computer vision functionalities
- PyMouse and PyKeyboard for system control

## Notes

- Ensure good lighting conditions for optimal hand detection
- Keep your hand within the camera frame
- The application works best when your hand is clearly visible and properly oriented
