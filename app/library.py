from zoneinfo import ZoneInfo
import flet as f
from datetime import datetime, timedelta, timezone
from app.services.library_service import *
from app.services.book_service import *
from app.services.borrow_service import *
from app.db.database import SessionLocal, engine
from contextlib import contextmanager
from datetime import datetime

base_dados = []

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# lista vista como global
lista = f.ListView(
    spacing=15,
    padding=10,
    expand=True
)

def borrow_book_from_library(
    page,
    code,
    title,
    author,
    bookType,
    requester,
    return_date,
):
    def on_code_autofill(e: f.Event):
        if e.control.value:  # checkbox is checked
            with get_db() as db:
                book = get_book_by_code(db, code=code.value.strip())
                if book:
                    title.value = book.title
                    author.value = book.author
                    bookType.value = book.category
                    page.update()
                    bookType.update()  # update just the dropdown specifically
                else:
                    e.control.value = False  # uncheck if not found
                    page.show_dialog(
                        f.SnackBar(f.Text("Book not found!"), bgcolor=f.Colors.RED)
                    )
                    page.update()
        else:  # checkbox unchecked — clear autofilled fields
            title.value = ""
            author.value = ""
            bookType.value = None
            page.update()


    autofill_checkbox = f.Checkbox(
        label="Autofill from code",
        value=False,
        on_change=on_code_autofill  # fires on check/uncheck
    )

    def on_date_selected(e):
        if page.date_picker.value:
            return_date.value = page.date_picker.value.strftime("%d/%m/%Y")
            page.update()

    #page.date_picker = f.DatePicker(on_change=on_date_selected)
    page.date_picker = f.DatePicker(
        first_date=datetime.now(timezone.utc) + timedelta(days=1),  # tomorrow as minimum
        value=datetime.now(timezone.utc) + timedelta(days=1),       # default selected date
        on_change=on_date_selected,
    )
    page.overlay.append(page.date_picker)

    def abrir_datepicker(e):
        page.date_picker.open = True
        page.update()

    def guardar_dados():
        if code.value.strip() and title.value.strip() and author.value.strip() and bookType.value and return_date.value:
            # register the borrowing in the database
            # Store/save always in UTC
            if requester.value.strip():
                borrower_name = requester.value.strip()
                created_at = datetime.now(tz=ZoneInfo("UTC"))
                with get_db() as db:
                    book = get_book_by_code(db, code.value)  # the code is unique for each book so we can retrieve the book using the code and then use the id of the book to create the borrow record
                    if book:
                        borrow = Borrow(
                            book_id=book.id,
                            borrower_name=borrower_name,
                            borrow_date=created_at.strftime("%d/%m/%Y-%H:%M:%S"),
                            return_date=return_date.value,
                        )
                        create_borrow(db, borrow=borrow) # method to create a borrow record in the database
                        # only after the borrow record is created successfully in the database the fields can be cleared
                        page.show_dialog(
                            f.SnackBar(
                                f.Text("Book Borrowed from the Library Successfully!"), bgcolor=f.Colors.GREEN, duration=1000
                            )
                        )
                        code.value = ""
                        title.value = ""
                        author.value = ""
                        requester.value = ""
                        bookType.value = None
                        return_date.value = None
                    else:
                        page.show_dialog(
                            f.SnackBar(
                                f.Text("Book not found!"), bgcolor=f.Colors.RED, duration=1000
                            )
                        )
            else:
                page.show_dialog(
                    f.SnackBar(
                        f.Text("The name of the borrower is mandatory!"), bgcolor=f.Colors.RED, duration=1000
                    )
                )
                return
        else:
            page.show_dialog(
                f.SnackBar(
                    f.Text("All the Fields are mandatory!"), bgcolor=f.Colors.RED, duration=1000
                )
            )


    page.add(
        f.Container(
            content=f.Column(
                [
                    f.Text("Register book Borrowing", size=30),
                    f.Row(
                        [
                            code,
                            autofill_checkbox,
                        ],
                        alignment=f.MainAxisAlignment.CENTER
                    ),
                    title,
                    author,
                    bookType,
                    requester,
                    f.Row(
                    [
                        return_date,
                        f.IconButton(f.Icons.CALENDAR_MONTH, on_click=abrir_datepicker),
                    ],
                    alignment=f.MainAxisAlignment.CENTER
                    ),
                    f.Button("Save Data", on_click=guardar_dados)
                ],
                spacing=20,  # espaçamento entre os elementos
                horizontal_alignment=f.CrossAxisAlignment.CENTER,
            ),
            alignment=f.alignment.Alignment.CENTER,
            expand=True
        )
    )    

def add_book_to_library(
    page: f.Page,
    title: f.TextField,
    code: f.TextField,
    author: f.TextField,
    category: f.Dropdown,
    publisher: f.TextField,
    year: f.TextField,
):
    
    def save_book():
        if title.value.strip() and \
        code.value.strip() and \
        author.value.strip() and \
        publisher.value.strip() and \
        year.value.strip() and \
        category.value:
            with get_db() as db:
                book = Book(
                    title=title.value.strip(),
                    code=code.value.strip(),
                    author=author.value.strip(),
                    category=category.value,
                    publisher=publisher.value.strip(),
                    year=year.value.strip(),
                )
                create_book(db, book=book) # method to create a book record in the database
                # only after the book record is created successfully in the database the fields can be cleared
                # for now also add to the default library it should be possible to define when creating the Book record into db but this was simpler for now...
                # preperaded for later on to select a library instead of the predefining one as default
                library = get_library(db, library_id=1)
                print(f"fetched library:", library)
                if library:
                    library_id = library.id
                    add_book_to_library_db(db, library_id=library_id, book=book)
                    print(f"successfull associated to the library:", library.to_dict())
                else:
                    page.show_dialog(
                        f.SnackBar(
                            f.Text("Missing Default Library! - Contact Platform Admin"), bgcolor=f.Colors.ORANGE, duration=1000
                        )
                    )
                title.value = ""
                code.value = ""
                author.value = ""
                category.value = None
                publisher.value = ""
                year.value = ""
                page.show_dialog(
                    f.SnackBar(
                        f.Text("Book Added successfully!"), bgcolor=f.Colors.BLUE, duration=1000
                    )
                )

        else:
            page.show_dialog(
                f.SnackBar(
                    f.Text("All the Fields are mandatory!"), bgcolor=f.Colors.RED, duration=1000
                )
            )

    page.add(
        f.Container(
            content=f.Column(
                [
                    f.Text("Add Book", size=30),
                    code,
                    title,
                    author,
                    category,
                    publisher,
                    year,
                    f.Button("Save Data", on_click=save_book)
                ],
                spacing=20,  # espaçamento entre os elementos
                horizontal_alignment=f.CrossAxisAlignment.CENTER,
            ),
            alignment=f.alignment.Alignment.CENTER,
            expand=True
        )
    )       

def list_borrowed_books_by_person(page, requester):

    lista.controls.clear()
    with get_db() as db:
        borrowed_books = get_all_borrows_by_requester(db, requester=requester.value.strip())
        for borrow in borrowed_books:

            if borrow.return_date == "Agendada":

                estado = f.Icon(f.Icons.ALARM, color=f.Colors.ORANGE)

            elif borrow.status == "Cancelada":
                estado = f.Icon(f.Icons.CANCEL, color=f.Colors.RED)

            else:
                estado = f.Icon(f.Icons.CALENDAR_MONTH, color=f.Colors.GREEN)

            lista.controls.append(

                f.Card(
                    content=f.Container(
                        padding=12,
                        content=f.Row(
                            [
                                f.Column(
                                    [
                                        f.Text(f"Paciente: {consult.pacient.name}", size=14,
                                            weight=f.FontWeight.BOLD),
                                        f.Text(f"Médico: {consult.medic.name}", size=12),
                                        f.Text(f"Data: {consult.date}", size=12),
                                        estado
                                    ],
                                    spacing=5,
                                ),
                                # f.Row(
                                #     [
                                #         f.IconButton(
                                #             f.Icons.EDIT,
                                #             icon_color=f.Colors.BLUE,
                                #             tooltip="Atualizar",
                                #             on_click=lambda e, p=consult: atualizar_consulta(page, p),
                                #         ),
                                #         f.IconButton(
                                #             f.Icons.DELETE,
                                #             icon_color=f.Colors.RED,
                                #             tooltip="Apagar",
                                #             on_click=lambda e, p=consult: apagar_consulta(page, p),
                                #         ),
                                #     ]
                                # )

                            ],
                            alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    ),
                    elevation=2
                )
            )


# def listar_total(page):
#     # ficheiros_paciente.atualizar_lista_dados(base_dados)
#     with get_db() as db:    
#         consults = get_all_consults(db)
#         if not consults:
#             janela = f.AlertDialog(
#                 title="Informação",
#                 content=f.Text(f"Ainda não foram registadas consultas!"),
#                 actions=[
#                     f.Button("OK", on_click=lambda e: fechar_janela())
#                 ]
#             )
#         else:
#             print(f"Existem até ao momento {len(consults)} consultas")
#             janela = f.AlertDialog(
#                 title="Informação",
#                 content=f.Text(f"Existem até ao momento {len(consults)} consultas"),
#                 actions=[
#                     f.Button("OK", on_click=lambda e: fechar_janela())
#                 ]
#             )

#         def fechar_janela():
#             janela.open = False
#             page.update()

#         page.show_dialog(janela)
#         janela.open = True
#         page.update()




# def listar_consultas(page):
#     # ficheiros_paciente.atualizar_lista_dados(base_dados)
#     with get_db() as db:
#         consults = get_all_consults(db)
#         if not consults:

#             page.add(
#                 f.Container(
#                     content=f.Text("Não existem consultas marcadas!", size=18),
#                     alignment=f.alignment.Alignment.CENTER,
#                     expand=True
#                 )
#             )
#         else:

#             listagem(page)

#             page.add(
#                     f.Container(

#                         content=f.Column(
#                             [
#                                 f.Text("Consultas Registadas", size=16, weight=f.FontWeight.BOLD),
#                                 lista
#                             ],

#                             horizontal_alignment=f.CrossAxisAlignment.CENTER,

#                         ),

#                         alignment=f.alignment.Alignment.CENTER,
#                         expand=True

#                     )

#                 )


# def apagar_consulta(page, p):

#     janela = f.AlertDialog(
#         title="Informação",
#         content=f.Text(f"Tem a certeza que pretende apagar a consulta do paciente: {p.get_nome()}"),
#         actions=[
#             f.Button("Confirmar", on_click=lambda e: remove_consulta()),
#             f.Button("Cancelar", on_click=lambda e: fechar_janela())
#         ]
#     )

#     def remove_consulta():

#         base_dados.remove(p)
#         ficheiros_paciente.atualizar_ficheiro(base_dados)
#         janela.open = False
#         if not base_dados:
#             lista.controls.clear()
#             lista.controls.append(

#                 f.Row(
#                     [
#                         f.Text("Não existe informação disponível!!")
#                     ],
#                     alignment=f.MainAxisAlignment.CENTER
#                 )
#             )

#         else:
#             listagem(page)

#         page.update()
#         page.show_dialog(
#                 f.SnackBar(
#                     f.Text("Consulta removida com sucesso!"), bgcolor=f.Colors.GREEN, duration=1000
#                 )
#             )

#     def fechar_janela():
#         janela.open = False
#         page.update()

#     page.show_dialog(janela)
#     janela.open = True
#     page.update()


# def atualizar_consulta(page, p):

#     novo_estado = f.Dropdown(
#         label="Atualizar Estado da Consulta",
#         width=300,
#         options=[
#             f.DropdownOption(key="Agendada", text="Agendada"),
#             f.DropdownOption(key="Cancelada", text="Cancelada"),
#             f.DropdownOption(key="Realizada", text="Realizada")
#         ]
#     )
#     janela = f.AlertDialog(
#         title="Informação",
#         content=f.Container(
#             content=f.Column(
#                 [
#                     f.Text(f"Atualmente a consulta tem o seguinte estado: {p.get_estado()}"),
#                     novo_estado,
#                 ]
#             )
#         ),
#         actions=[
#             f.Button("Atualizar", on_click=lambda e: atualiza_consulta()),
#             f.Button("Cancelar", on_click=lambda e: fechar_janela())
#         ]
#     )

#     def atualiza_consulta():

#         if novo_estado.value:
#             p.set_estado(novo_estado.value)
#             ficheiros_paciente.atualizar_ficheiro(base_dados)

#         janela.open = False
#         if not base_dados:
#             lista.controls.clear()
#             lista.controls.append(

#                 f.Row(
#                     [
#                         f.Text("Não existe informação disponível!!")
#                     ],
#                     alignment=f.MainAxisAlignment.CENTER
#                 )
#             )

#         else:
#             listagem(page)

#         page.update()
#         if novo_estado.value:
#             page.show_dialog(
#                     f.SnackBar(
#                         f.Text("Consulta atualizada com sucesso!"), bgcolor=f.Colors.GREEN, duration=1000
#                     )
#                 )

#     def fechar_janela():
#         janela.open = False
#         page.update()

#     page.show_dialog(janela)
#     janela.open = True
#     page.update()


# def listar_consultas_realizadas(page):
#     lista.controls.clear()
#     with get_db() as db:
#         # consults = get_all_consults(db)
#         medics = get_all_medics(db)
#         medico = f.Dropdown(
#             label="Escolha um Médico",
#             width=230,
#             options=[
#                 f.DropdownOption(key=str(m.id), text=m.name)
#                 for m in medics
#             ]
#         )

#     def selecionar_data_ini(e):

#         if page.data_picker_ini.value:
#             data_ini.value = page.data_picker_ini.value.strftime("%d/%m/%Y")
#             page.update()

#     page.data_picker_ini = f.DatePicker(on_change=selecionar_data_ini)

#     page.overlay.append(page.data_picker_ini)

#     def abrir_data_ini():

#         page.data_picker_ini.open = True
#         page.update()

#     data_ini = f.TextField(
#         label="Data Inicial",
#         read_only=True,
#         width=150,
#         # value=datetime.today().strftime("%d/%m/%Y")
#     )

#     def selecionar_data_fim(e):

#         if page.data_picker_fim.value:
#             data_fim.value = page.data_picker_fim.value.strftime("%d/%m/%Y")
#             page.update()

#     page.data_picker_fim = f.DatePicker(on_change=selecionar_data_fim)

#     page.overlay.append(page.data_picker_fim)

#     def abrir_data_fim():

#         page.data_picker_fim.open = True
#         page.update()

#     data_fim = f.TextField(
#         label="Data Final",
#         read_only=True,
#         width=150,
#         # value=datetime.today().strftime("%d/%m/%Y")
#     )

#     def realizadas():
#         lista.controls.clear()

#         if not medico.value or not data_ini.value or not data_fim.value:
#             page.show_dialog(
#                 f.SnackBar(
#                     f.Text("Os campos são de preenchimento obrigatório!"), bgcolor=f.Colors.RED, duration=1000
#                 )
#             )
#             return

#         data_ini_formatada = datetime.strptime(data_ini.value, "%d/%m/%Y")
#         data_fim_formatada = datetime.strptime(data_fim.value, "%d/%m/%Y")
#         if data_ini_formatada > data_fim_formatada:
#             page.show_dialog(
#                 f.SnackBar(
#                     f.Text("A data inicial deve ser anterior à data final!"), bgcolor=f.Colors.RED, duration=1000
#                 )
#             )
#             return
#         else:
#             # ficheiros_paciente.atualizar_lista_dados(base_dados)
#             with get_db() as db:
#                 consults = get_all_consults(db)
#                 aux = False
#                 for consulta in consults:
#                     data_ficheiro = datetime.strptime(consulta.date, "%d/%m/%Y")
#                     print(f"Data Ini: {data_ini.value} - Data Ficheiro: {consulta.date} - Data Fim: {data_fim.value}")
#                     if medico.value == consulta.medic.name and data_ini_formatada <= data_ficheiro <= data_fim_formatada:
#                         aux = True
#                         # print(f"Data Ini: {data_ini.value} - Data Ficheiro: {consulta.get_data()}")

#                         if consulta.status == "Agendada":

#                             estado = f.Icon(f.Icons.ALARM, color=f.Colors.ORANGE)

#                         elif consulta.status == "Cancelada":
#                             estado = f.Icon(f.Icons.CANCEL, color=f.Colors.RED)

#                         else:
#                             estado = f.Icon(f.Icons.CALENDAR_MONTH, color=f.Colors.GREEN)

#                         lista.controls.append(

#                                 f.Card(
#                                     content=f.Container(
#                                             padding=12,
#                                             content=f.Column(
#                                                 [
#                                                     f.Text(f"Paciente: {consulta.pacient.name}", size=14,
#                                                         weight=f.FontWeight.BOLD),
#                                                     f.Text(f"Médico: {consulta.medic.name}", size=12),
#                                                     f.Text(f"Data da Consulta: {consulta.date}", size=12),
#                                                     estado
#                                                 ],
#                                                 spacing=5
#                                             )
#                                     )
#                                 )
#                         )

#                 if not aux:
#                     page.show_dialog(
#                         f.SnackBar(
#                             f.Text("Não existem consultas, nesse espaço temporal para o Médico em questão!"), bgcolor=f.Colors.RED, duration=1000
#                         )
#                     )

#             medico.value = None
#             data_ini.value = ""
#             data_fim.value = ""
#     page.add(
#         f.Column(
#             [
#                 f.Row(
#                     [
#                         data_ini,
#                         f.IconButton(f.Icons.CALENDAR_MONTH, on_click=abrir_data_ini),
#                         data_fim,
#                         f.IconButton(f.Icons.CALENDAR_MONTH, on_click=abrir_data_fim),
#                         medico,
#                         f.Button("Pesquisar Consultas", width=180, on_click=realizadas)
#                     ],
#                     spacing=20,
#                     alignment=f.MainAxisAlignment.CENTER
#                 ),
#                 f.Divider(),
#                 lista
#             ]
#         )

#     )

