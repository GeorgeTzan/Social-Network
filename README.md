# Social-Network
Social Network Application. A Python based Social Network app using a graphical user interface (GUI) built with tkinter & wxPython versions. The Application supports essential functionalities, such as user managment, connection creation and network analysis based in C++.

### Table of Contents

- [Installation](#installation)
    - [Windows](#Windows)
    - [Linux](#Linux)
- [Usage](#usage)
- [How to Use](#how-to-use)
- [Features](#features)
- [License](#license)

### Installation

Getting the Social Network up and running, follow these steps:

1. **Clone the Repository:**
   
   Fire up your terminal and run this command:
   ```bash
   git clone https://github.com/GeorgeTzan/Social-Network.git
   ```

2. Navigate to the project directory:

    ```bash
    cd Social-Network
    ```

3. Install the required modules:
    ```bash
    pip install -r requirements.txt
    ```

4. Compile the .so file:
    ```bash
    g++ -shared -fPIC -std=c++17 -I./pybind11/include/ `python3.10 -m pybind11 --includes` social_network.cpp -o social_network.so `python3.10-config --ldflags`
    ```
    Make sure you put your installed python version

5. Run the App:

    ```bash
    python3 Social\ Network.py 
    ```

## Windows

* **Warning:** 
This was built in a Linux enviroment. Behaviour in Windows OS is unknown.

Have Visual C++ Build Tools installed & wxPython 
```bash
pip install -r requirements_wx.txt 
pip install -r requirements_tkinter.txt
```
## Linux
```bash
sudo apt update
sudo apt install -y libgtk-3-dev libjpeg-dev libpng-dev libfreetype6-dev
pip install -r requirements_wx.txt 
pip install -r requirements_tkinter.txt
```

## Usage

After installing the Social Network App, follow the following instructions on how it works.

## How to use

1. Manage your users.
2. Manage your connections.
3. View Network connections either live or offline.
4. Use Network analysis on your network such as finding the shortest path.
5. Save your Network (optional)

## Features

- Randomly generated Networks.
- Save and/or load Networks.
- Manage your users and their connections.
- Live view of your Network.
- Responsive GUI design.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.