# File System Simulation

This Python project implements a simple file system simulation, creating a custom file system within a single file stored on a real file system. The simulation supports operations such as copying files into the system, renaming files, removing files, and more.

## Features

- Create a custom file system within a single file.
- Copy files from the real file system into the simulated file system.
- Copy files from the simulated file system to the real file system.
- Rename files within the simulated file system.
- Remove files from the simulated file system.
- List all files stored in the simulated file system.
- Display free space within the simulated file system.

## Usage

1. **Installation:**
   - Clone the repository: `git clone https://github.com/gvlk/file-system.git`
   - Navigate to the project directory: `cd file-system`

2. **Run the Simulation:**
   - Execute the main script with the desired options:
     ```bash
     python main.py -s <size_in_MB> -f <fs_file> --copy_to_fs <file_path>
     ```

3. **Command-Line Options:**
   - `-s, --size`: Set the size of the simulated file system in megabytes (default: 200).
   - `-f, --fs_file`: Specify the name of the simulated file system file (default: "furgfs.fs").
   - `--copy_to_fs`: Copy a file from the real file system into the simulated file system.

4. **Examples:**
   ```bash
   # Create a simulated file system with a size of 200 MB
   python main.py -s 200

   # Copy a file "example.txt" into the simulated file system
   python main.py -s 200 -f "furgfs.fs" --copy_to_fs "example.txt"

## License
This project is licensed under the MIT License.
