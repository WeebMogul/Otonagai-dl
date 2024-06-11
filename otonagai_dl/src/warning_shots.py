from rich.panel import Panel
from rich.markdown import Markdown


def no_downloads():

    return Panel(
        Markdown(
            """

            There seems to be an issue with the urls you have provided.
            
            Here are some reasons:

            - No urls entered.
            - You entered a text instead of a number with the page-related input.
            - The starting page number is more than the ending page number.
            - The product associated with the url is already in the database.
            - The hobbylinkjapan link you entered is not available on the website.

            Try again.
            """
        ),
        title_align="center",
    )


def create_db_warning_panel():

    return Panel(
        Markdown(
            """
            There is no merchandise info added to the database. Please follow the instructions :
            
            - Go to the HobbyLinkJapan website (https://www.hlj.com)
            - Get the link to any of your favourite product or the search result containing multiple pages
            - Choose the "Open URLs" option and paste the links you copied.
            - Close and save the file.
            - Choose the option "Add Merchandise to the database". Follow the onscreen instructions.
            - Now, go the the database.                    
            """
        ),
        title_align="center",
    )


def create_log_warning_panel():

    return Panel(
        Markdown(
            """
            No merch has been added to your log. Please follow the instructions :
            
            - Go to the database
            - Choose any one of the merch in the database
            - Enter 'y' to add to your log.
            - Choose the status of what you're going to do with the merch, to the log.
            - Exit the database.
            - Now, go the the log and check if it is in.                    
            """
        ),
        title_align="center",
    )
