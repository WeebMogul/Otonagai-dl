from .src.menu import menu
from .src.utils import create_data_contents


def main():

    # create the data files required for the app
    create_data_contents()
    menu()


if __name__ == "__main__":
    main()
