# CP2TOTO - Simplified File Transfer Automation

Welcome to CP2TOTO! This tool is designed to streamline the process of transferring files from your local machine to a remote server using the Secure Copy Protocol (SCP). With a user-friendly terminal interface, CP2TOTO takes the hassle out of file transfers and even offers file conversion to optimize storage space on your server.

## Table of Contents
- [CP2TOTO - Simplified File Transfer Automation](#cp2toto---simplified-file-transfer-automation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

## Introduction
SCP, or Secure Copy Protocol, is a method for securely transferring files between a local host and a remote host or between two remote hosts. CP2TOTO leverages SCP to provide a seamless file transfer experience, complete with interactive selection and optional file conversion to the efficient H.265 mp4 format.

## Features
- **Interactive File Selection**: Choose exactly which files or folders you want to transfer with an easy-to-use interface.
- **File Conversion**: Convert your files to mp4 with H.265 codec on-the-fly for efficient storage.
- **Automation**: Save time with automated processes, reducing manual effort and the risk of errors.

## Installation
Here's a step-by-step guide to get CP2TOTO up and running on your system:

1. Clone the repository:
   ```bash
   git clone https://github.com/patillacode/cp2toto.git
   ```
2. Navigate to the project directory:
   ```bash
   cd cp2toto
   ```
3. Copy the `.env.sample` file to `.env` and configure it with your settings:
   ```bash
   cp .env.sample .env
   # Edit the .env file with your preferred text editor
   ```
4. Set up a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
5. Alternatively, you can use the `Makefile` to set up your environment and install dependencies:
   ```bash
   make install
   ```

## Usage
To start using CP2TOTO, you can utilize the `Makefile` commands for a simplified setup process. Follow these simple steps:

1. Launch the script:
   ```bash
   python cp2toto.py
   ```
2. Use the interactive terminal interface to select the files or folders you wish to transfer.
3. Choose whether to convert files to H.265 mp4 format before transfer.
4. Confirm the transfer and let CP2TOTO handle the rest!

Example:
```bash
# Start the script
python cp2toto.py

# Follow the on-screen prompts to select and transfer your files.
```

## Troubleshooting
If you encounter any issues, please check the following:

- Ensure you have Python 3.6 or higher installed.
- Verify that SCP is installed and configured on both your local and remote systems.
- Make sure [ffmpeg](https://ffmpeg.org/) is installed if you wish to use the file conversion feature.

## Contributing
We welcome contributions of all kinds! To contribute:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
If you have any questions or suggestions, feel free to reach out to us at [https://github.com/patillacode/cp2toto](https://github.com/patillacode/cp2toto).
