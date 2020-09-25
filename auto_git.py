import os
import pathlib
import time
from argparse import ArgumentParser

FILE_PATH = "The path to the file you want to git."

def main():
    parser = ArgumentParser()
    parser.add_argument("file_path", help=FILE_PATH)

if __name__ == "__main__":
    print("hello man!")
    main()

