from File_Manager import user_file_exists
from StartWindow import start_start_window
from MainWindow import start_main_window

if __name__ == "__main__":
    if user_file_exists():
        start_main_window()
    else:
        start_start_window()