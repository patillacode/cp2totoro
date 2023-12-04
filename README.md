# CP2TOTO

## Table of Contents
- [CP2TOTO](#cp2toto)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Motivation](#motivation)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Problem Solving](#problem-solving)
  - [Contribution](#contribution)
  - [Contact](#contact)

## Introduction
CP2TOTO is a Python script that automates the process of copying files from a local system to a remote server using Secure Copy Protocol (SCP). It provides an interactive terminal interface for users to select files/folders for copying, and offers the option to convert files to mp4 with H.265 codec before copying.

## Installation
To install and set up the project, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Run the following commands:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
To use the script, run the following command in the terminal:
```bash
python cp2toto.py
```
Follow the prompts in the terminal to select files/folders for copying.

## Motivation
The motivation behind this script was to simplify the process of copying files from a local system to a remote server. Manually selecting files and folders for copying can be a tedious and error-prone task. This script automates the process, reducing the possibility of errors and saving time.

## Features
- Automates the process of copying files from a local system to a remote server.
- Provides an interactive terminal interface for users to select files/folders for copying.
- Offers the option to convert files to mp4 with H.265 codec before copying.

## Requirements
- Python 3.6 or higher
- SCP installed on both local and remote systems
- [ffmpeg](https://ffmpeg.org/) installed on local system


## Problem Solving
This script solves several problems:

- It automates the process of copying files from a local system to a remote server, saving time and reducing the possibility of errors.
- It provides an interactive terminal interface for users to select files/folders for copying, making the process more user-friendly.
- It offers the option to convert files to mp4 with H.265 codec before copying, which can result in significant space savings on the server.

## Contribution
If you want to contribute to this project, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.

## Contact
Project Link: [https://github.com/patillacode/cp2toto](https://github.com/patillacode/cp2toto)
