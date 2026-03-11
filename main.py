import flet as f
from datetime import datetime
# import clinica
from app.services.library_service import *
from app.services.book_service import *
from app.services.borrow_service import *
import app.db.models as models
from app.library import *

# Create the database tables
models.Base.metadata.create_all(bind=engine)
# Define the options for the dropdowns
options = models.BookCategory

# base_dados_medicos = []

from sqlalchemy import inspect
inspector = inspect(engine)
print(inspector.get_table_names())

def main(page: f.Page):

    page.title = "LEITURA ATIVA"  # definir título da janela
    page.window.width = 950  # definir largura da janela
    page.window.height = 600  # definir algura da janela
    page.window.resizable = False  # impedir o redimensionar da janela

    # To simplify one Library will pre-populate the database with dummy data for testing purposes, this will be done every time the app is run, but in a real application
    # the Library would be created from user Input
    with get_db() as db:
        # Clear existing data
        delete_all_libraries(db)
        # Create The default library
        library = create_library(db, library=Library(name="Active Reading Library"))
        print(f"Created library: {library.to_dict()}")
    ####################################################################

    def menu_click(nomes):
        page.controls.clear()

        if nomes == "Home":
            page.add(
                f.Row(
                    [
                        f.Text("Library Home Page!")
                    ],
                    alignment=f.MainAxisAlignment.CENTER
                )
            )

        elif nomes == "Borrow":
             # Fields to autofill
            title = f.TextField(label="Book Title", width=300, read_only=True)
            author = f.TextField(label="Book Author", width=300, read_only=True)
                                
            # The fields pertaning to the book
            code = f.TextField(label="Code of the book", width=300) # add here a picker to validate the code and autofill the following book fields sepcific

            # Fields pertaining to who is borrowing the book and when it should be returned
            requester = f.TextField(label="Person Requesting", width=300)

            # the medics should be loaded from the database as it already been populated with dummy data... now retrive from there and load into the dropdown
            # ficheiros_paciente.carregar_medicos(base_dados_medicos)
            
            bookType = f.Dropdown(
                label="Book Category",
                hint_text="Choose a category",
                width=300,
                disabled=True,
                options=[
                        f.DropdownOption(key=str(c.value), text=c.value)
                        for c in options
                ], 

            )

            return_date = f.TextField(
                label="Return Date",
                read_only=True,
                width=250,
            # value=datetime.today().strftime("%d/%m/%Y")
            )

            borrow_book_from_library(
                page=page,
                code=code,
                title=title,
                author=author,
                requester=requester,
                bookType=bookType,
                return_date=return_date,
            )

            #clinica.registar_consulta(page, nome, medico, estado, data)

        elif nomes == "Book":

            # The fields pertaning to the book
            code = f.TextField(label="Code of the Book", width=300)
            title = f.TextField(label="Title", width=300)
            author = f.TextField(label="Author", width=300)
            # Fields pertaining to who is borrowing the book and when it should be returned
            # category = f.TextField(label="Category", width=300)
            category = f.Dropdown(
                label="Category",
                hint_text="Choose a category",
                width=300,
                options=[
                        f.DropdownOption(key=str(c.name), text=c.name)
                        for c in options
                ]
            )

            publisher = f.TextField(label="Publisher", width=300)
            year = f.TextField(label="Release Year", width=300)

            add_book_to_library(
                page,
                title,
                code,
                author,
                category,
                publisher,
                year,
            )

        elif nomes == "Borrowed Books":
            with get_db() as db:
                requester = f.Dropdown(
                    label="Requester",
                    hint_text="Filter by Requester",
                    width=300,
                    options=[
                            f.DropdownOption(key=requester, text=requester)
                            for requester in get_requester_list(db)
                    ]
                )

                list_borrowed_books_by_person(page, requester=requester)
            #f.TextField(label="Person Requesting", width=300)

        elif nomes == "Total Borrowed":

            show_total_borrow_counter(page)

    page.appbar = f.AppBar(

            color=f.Colors.WHITE,  # cor do texto
            bgcolor=f.Colors.BLUE,  # cor de fundo do menu
            actions=[

                f.TextButton("HOME", icon=f.Icons.HOME, style=f.ButtonStyle(f.Colors.WHITE),
                             on_click=lambda e1: menu_click("Home")),
                f.TextButton("Borrow a book", icon=f.Icons.INSERT_CHART,
                             style=f.ButtonStyle(f.Colors.WHITE),
                             on_click=lambda e1: menu_click("Borrow")),
                f.TextButton("Add Book to Library", icon=f.Icons.LIST, style=f.ButtonStyle(f.Colors.WHITE),
                             on_click=lambda e1: menu_click("Book")),
                f.TextButton("Borrowed Books List", icon=f.Icons.CATEGORY, style=f.ButtonStyle(f.Colors.WHITE),
                             on_click=lambda e1: menu_click("Borrowed Books")),
                # f.TextButton("Consultas Paciente", icon=f.Icons.CATEGORY, style=f.ButtonStyle(f.Colors.WHITE),
                #              on_click=lambda e1: menu_click("Consultas_Paciente")),
                f.TextButton("Total Borrowed", icon=f.Icons.SUMMARIZE, style=f.ButtonStyle(f.Colors.WHITE),
                             on_click=lambda e1: menu_click("Total Borrowed"))

            ]
    )


f.run(main, view=f.AppView.FLET_APP)