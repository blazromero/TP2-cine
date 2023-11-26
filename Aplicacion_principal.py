from tkinter import Tk, Toplevel, Entry, Button, Label, Frame, Spinbox, messagebox, OptionMenu, StringVar, LabelFrame, Canvas, Scrollbar
import qrcode
import os
import requests
from PIL import Image, ImageTk
import base64
import io


CARPETA_CODIGOS_QR: str = 'QR'
ACLARACION_FUNCIONES_PELICULAS: str = 'Cada cine tiene sala unica. Cada pelicula se proyectara en la misma sala pero distintas horas y dias para evitar superposicion.'
ACLARACION_FONT: str = 'Helvetica 9 bold'
PRECIO_ENTRADAS_GENERAL: float = 3000.0
MAX_ENTRADAS: int = 12
MIN_ENTRADAS: int = 1

MAX_SNACKS: int = 12

CHECKOUT_FONT: str = 'Helvetica 9 bold'

TOKEN: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.DGI_v9bwNm_kSrC-CQSb3dBFzxOlrtBDHcEGXvCFqgU'
API: dict = {
    'BASE_URL': 'http://vps-3701198-x.dattaweb.com:4000',
    'PATH': {
        'TODAS_LAS_PELIS': '/movies',
        'PELI_POR_ID': '/movies/{movie_id}',
        'POSTER_POR_ID': '/posters/{poster_id}',
        'TODOS_LOS_SNACKS': '/snacks',
        'DONDE_SE_PROYECTA': '/movies/{movie_id}/cinemas',
        'TODOS_LOS_CINES': '/cinemas',
        'TODAS_LAS_PELIS_DEL_CINE': '/cinemas/{cinema_id}/movies'
    },
    'HEADERS': { 'Authorization': f'Bearer {TOKEN}'}
}
def mostrar_snacks(lblframe_snacks: LabelFrame, totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se pintan en pantalla el listado de snacks con nombre, cantidad y el boton para agregar al carrito.
    '''
    snacks = totem['SNACKS']

    i: int = 0
    for snack in snacks:
        texto_snack: str = f'{snack} ${snacks[snack]}'.title().replace('_', ' ')

        lbl_snack: Label = Label(lblframe_snacks, text = texto_snack) 
        lbl_snack.grid(row=i, column=0)
        
        spin_cantidad_snacks = Spinbox(lblframe_snacks, from_=0, to=MAX_SNACKS, validate='key', width=5)
        spin_cantidad_snacks['validatecommand'] = (spin_cantidad_snacks.register(isNumber), '%P')
        spin_cantidad_snacks.config(command= lambda spin_cantidad_snacks=spin_cantidad_snacks: spinbox_fondo_blanco(spin_cantidad_snacks))
        spin_cantidad_snacks.grid(row=i,column=1)
        
        btn_agregar_al_carrito: Button = Button(lblframe_snacks, text='Agregar al carrito', command= lambda snack=snack, spin_cantidad_snacks=spin_cantidad_snacks: agregar_al_carrito(totem=totem, snack=snack, spin_cantidad_snacks=spin_cantidad_snacks))
        btn_agregar_al_carrito.grid(row=i, column=2)

        i += 1



def hay_asientos_disponibles(cantidad_entradas: int, totem: dict) -> bool:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Devolvera un bool con valor True indicado que aun hay asientos disponibles, False en caso contrario.
    '''
    cine_info:dict = totem['CINES_INFO']
    ubicacion:str = totem['ubicacion']
    
    compra = totem['compra']
    nombre_pelicula: str = compra['pelicula']
    lugares_disponibles:dict = totem['lugares_disponibles']

    lugar_disponible_key:str = f'{ubicacion}_{nombre_pelicula}'

    if lugar_disponible_key in lugares_disponibles:
        asientos_vacios: int = int(lugares_disponibles[lugar_disponible_key])

        if asientos_vacios < cantidad_entradas:
            return False
        else:
            compra['ubicacion_key'] = lugar_disponible_key
    else:
        cine_id: str = obtener_id_cinema(ubicacion, totem)
        lugares_disponibles[lugar_disponible_key] = int(cine_info[cine_id]['available_seats'])
        compra['ubicacion_key'] = lugar_disponible_key

    return True



def spinbox_fondo_blanco(spin_box: Spinbox) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Pinta de blanco el fondo del SpinBox.
    '''  
    spin_box['bg'] = 'white'



def agregar_al_carrito(totem: dict, cantidad_entradas: Spinbox = None, snack: str = '', spin_cantidad_snacks: Spinbox = None, lbl_mas_info: Label = None) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Actualiza el estado de la compra. En caso de cantidad de entradas valida la cantidad contra lugares disponibles.
    '''      
    compra = totem['compra']

    if cantidad_entradas:
        cant_entradas: int = int(cantidad_entradas.get())

        if not hay_asientos_disponibles(cant_entradas, totem):
            lugares_disponibles: int = int(totem['lugares_disponibles'][f'{totem["ubicacion"]}_{compra["pelicula"]}'])

            cantidad_entradas['bg'] = 'red' 

            lbl_mas_info.config(text=f'Quedan {lugares_disponibles} lugares disponibles.', bg='red')
            lbl_mas_info.grid(column=1)
        else:
            if cant_entradas > MAX_ENTRADAS:
                cantidad_entradas['bg'] = 'red'      
            else:
                compra['cantidad_entradas'] = cant_entradas
                cantidad_entradas['bg'] = 'green'
                lbl_mas_info.grid_forget()

    elif snack:
        cantidad_snack: int = int(spin_cantidad_snacks.get())

        if cantidad_snack:
            snacks = totem['SNACKS']
            compra['snacks'][snack] = {'cantidad': cantidad_snack, 'precio_unidad': snacks[snack] }
            spin_cantidad_snacks['bg'] = 'green'
        else:
            spin_cantidad_snacks['bg'] = 'white'



def volver_a_principal(pantalla_actual, totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Escondemos la pantalla actual y mostramos la pantalla principal.
    '''
    pantalla_actual.withdraw()

    pantalla_principal = totem['ventanas']['pantalla_principal']

    pantalla_principal.deiconify()



def volver_a_pantalla_secundaria(pantalla_actual, totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Escondemos la pantalla actual y mostramos la pantalla secundaria.
    '''
    pantalla_actual.withdraw()

    pantalla_secundaria = totem['ventanas']['pantalla_secundaria']

    bnt_listo: Button = Button(pantalla_secundaria, text='Listo!', bg='green', command= lambda: volver_a_principal(pantalla_secundaria, totem))
    bnt_listo.pack()

    pantalla_secundaria.deiconify()



def mostrar_pantalla_reserva(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Escondemos la pantalla secundaria y mostramos la pantalla reserva con sus componentes pintados. Se actualiza el estado de la compra.
    '''
    pantalla_secundaria = totem['ventanas']['pantalla_secundaria']
    pantalla_secundaria.withdraw()

    precio_entradas = totem['precio_entradas_general']
    compra = totem['compra']
    
    reiniciar_compra(compra)

    compra['precio_entrada'] = precio_entradas
    compra['ubicacion'] = totem['ubicacion']

    pantalla_reserva = Toplevel()
    pantalla_reserva.title('RESERVA')
    pantalla_reserva.geometry('380x350')
    pantalla_reserva.config(bg='black')

    totem['ventanas']['pantalla_reserva'] = pantalla_reserva

    lbl_precio_entrada: Label = Label(pantalla_reserva, text=f'Precio unitario ${precio_entradas}', bg='black', fg='white')
    lbl_precio_entrada.grid(row=0, column=1)

    lbl_cantidad_entradas = Label(pantalla_reserva, text="Cantidad de entradas", bg='black', fg='white')
    lbl_cantidad_entradas.grid(row=1, column=0)

    spin_cantidad_entradas = Spinbox(pantalla_reserva, from_=1, to=MAX_ENTRADAS, validate='key', width=5, bg='black', fg='white')
    spin_cantidad_entradas['validatecommand'] = (spin_cantidad_entradas.register(isNumber), '%P')
    spin_cantidad_entradas.config(command= lambda: spinbox_fondo_blanco(spin_cantidad_entradas))
    spin_cantidad_entradas.grid(row=1, column=1)

    btn_agregar_al_carrito: Button = Button(pantalla_reserva, text='Agregar al carrito', command= lambda:agregar_al_carrito(totem, cantidad_entradas=spin_cantidad_entradas, lbl_mas_info=lbl_mas_info), bg='black', fg='white')
    btn_agregar_al_carrito.grid(row=1, column=2)
    
    lblframe_lista_snacks: LabelFrame = LabelFrame(pantalla_reserva, text='Snacks', bg='black', fg='white')
    lblframe_lista_snacks.grid(row=4, columnspan=3)

    btn_agregar_snacks: Button = Button(pantalla_reserva, text='Agregar Snacks', command=lambda:mostrar_snacks(lblframe_lista_snacks, totem), bg='black', fg='white')
    btn_agregar_snacks.grid(row=3, column=1)

    lbl_mas_info = Label(pantalla_reserva, text="", bg='black', fg='white')
    lbl_mas_info.grid_forget()

    bnt_listo: Button = Button(pantalla_reserva, text='Listo!', bg='green', command= lambda: volver_a_pantalla_secundaria(pantalla_reserva, totem), fg='white')
    bnt_listo.grid(column=1)

    pantalla_reserva.protocol("WM_DELETE_WINDOW", lambda: terminar_aplicacion(totem))



def reiniciar_compra(compra: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Reniciamos el estado de la compra.
    '''
    compra_cpy = compra.copy()

    compra.clear()

    compra['cantidad_entradas'] = 0
    compra['snacks'] = {}
    compra['ubicacion'] = ''
    compra['pelicula'] = compra_cpy['pelicula']



def isNumber(age_spinbox: Spinbox) -> bool:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Devolvemos un bool para decir si la cadena es un numero, True en caso afirmativo, False en caso contrario.
    '''
    return age_spinbox.isdigit() 



def mostrar_pantalla_secundaria(pelicula, totem)-> None:

    pantalla_principal = totem['ventanas']['pantalla_principal'] 
    pantalla_principal.withdraw()

    nombre_pelicula = pelicula['name']
    
    compra = totem['compra']
    compra['pelicula'] = nombre_pelicula

    synopsis = pelicula['synopsis']
    duracion = pelicula['duration']
    actores = pelicula['actors']
    genero = pelicula['gender']


    pantalla_secundaria = Toplevel()
    pantalla_secundaria.geometry('400x800')
    pantalla_secundaria.title('Pelicula')
    pantalla_secundaria.config(bg='black')

    totem['ventanas']['pantalla_secundaria'] = pantalla_secundaria
    
    btn_volver: Button = Button(pantalla_secundaria, text='Volver a pantalla principal', command= lambda:volver_a_principal(pantalla_secundaria, totem))
    btn_volver.pack()

    lblframe_nombre_peli: LabelFrame = LabelFrame(pantalla_secundaria, text='Pelicula:', bg='black', fg='white')
    lblframe_nombre_peli.pack()
    
    lbl_nombre_peli: Label = Label(lblframe_nombre_peli, text=nombre_pelicula, bg='black', fg='white')
    lbl_nombre_peli.pack()

    lblframe_synopsis: LabelFrame = LabelFrame(pantalla_secundaria, text='Synopsis:', bg='black', fg='white')
    lblframe_synopsis.pack()

    lbl_synopsis: Label = Label(lblframe_synopsis, text=synopsis, wraplength=200, bg='black', fg='white')
    lbl_synopsis.pack()

    lblframe_actores: LabelFrame = LabelFrame(pantalla_secundaria, text='Actores:', bg='black', fg='white')
    lblframe_actores.pack()

    lbl_actores: Label = Label(lblframe_actores, text=actores, wraplength=200, bg='black', fg='white')
    lbl_actores.pack()

    lblframe_genero: LabelFrame = LabelFrame(pantalla_secundaria, text='Genero:', bg='black', fg='white')
    lblframe_genero.pack()

    lbl_genero: Label = Label(lblframe_genero, text=genero, bg='black', fg='white')
    lbl_genero.pack()

    lblframe_duracion: LabelFrame = LabelFrame(pantalla_secundaria, text='Duracion:', bg='black', fg='white')
    lblframe_duracion.pack()

    lbl_duracion: Label = Label(lblframe_duracion, text=duracion, bg='black', fg='white')
    lbl_duracion.pack()

    if hay_asientos_disponibles(MIN_ENTRADAS, totem):
        btn_reservar: Button = Button(pantalla_secundaria, text='Reservar', command= lambda: mostrar_pantalla_reserva(totem), bg='black', fg='white')
        btn_reservar.pack()
    else:
        lbl_entradas_agotadas: Label = Label(pantalla_secundaria, text='Entradas agotadas.', bg='yellow',fg='black')
        lbl_entradas_agotadas.pack()

    pantalla_secundaria.protocol("WM_DELETE_WINDOW", lambda: terminar_aplicacion(totem), bg='black', fg='white')



def diseño_pantalla_principal(totem)-> dict:
    
    pantalla_principal = totem['ventanas']['pantalla_principal']
    
    lbl_cines = Label(text = 'Cine : ', bg= 'black', fg= 'white' )
    lbl_cines.grid(row=0, column=1)
    
    lbl_pelicula = Label(text = 'Buscar peli: ', bg= 'black', fg= 'white' )
    lbl_pelicula.grid(row=1, column=1)
    

    lbl_espacios = Label(text='   adsdsadss           ', bg= 'black')
    lbl_espacios.grid(row=3, column=0)
    lbl_espacios1 = Label(text='as ', bg= 'black')
    lbl_espacios1.grid(row=4, column=0)
    lbl_espacios2 = Label(text='s', bg= 'black')
    lbl_espacios2.grid(row=5, column=0)
    lbl_espacios3 = Label(text='sa', bg= 'black')
    lbl_espacios3.grid(row=6, column=0)
    
    boton_1 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_1.grid(row= 3, column= 2,pady= 5, padx= 5)

    boton_2 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_2.grid(row= 4, column= 2,pady= 5, padx= 5)

    boton_3 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_3.grid(row= 5, column= 3,pady= 5, padx= 5)

    boton_4 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_4.grid(row= 6, column= 3, pady= 5, padx= 5)

    boton_5 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_5.grid(row= 3, column= 3,pady= 5, padx= 5)

    boton_6 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_6.grid(row= 4, column= 3,pady= 5, padx= 5)

    boton_7 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_7.grid(row= 5, column= 2,pady= 5, padx= 5)

    boton_8 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_pantalla_secundaria(totem), height= 20 , width= 25)
    boton_8.grid(row= 6, column= 2, pady= 5, padx= 5)

    boton_buscar: Button = Button(text='buscar', height= 1, width=6)
    boton_buscar.grid(row=1, column=3)

    boton_buscar: Button = Button(text='Finalizar Compra', height= 1, width=15)
    boton_buscar.grid(row=1, column=4)


    lbl_aclaracion: Label = Label(pantalla_principal, text=ACLARACION_FUNCIONES_PELICULAS, wraplength=200, bg='CadetBlue', font=ACLARACION_FONT)
    lbl_aclaracion.grid(row=2, column=2, columnspan=2, sticky='news', pady=20)
    entrada_usuario = Entry(pantalla_principal, width= 25)
    entrada_usuario.grid(row=1, column=2)

    

def obtener_id_cinema(ubicacion_cine_elegido: str, totem: dict) -> str:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: En caso de ser encontrado devolvera una cadena con el id de la ubicacion del cine, sino esta sera vacia.
    '''
    cines: dict = totem['CINES_INFO']
    id_cine_encontrado: str = ''

    for cine_id, cine_info in cines.items():
        ubicacion: str = cine_info['location']
        
        if ubicacion_cine_elegido == ubicacion:
            id_cine_encontrado = cine_id

    return id_cine_encontrado



def cargar_snacks(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se actualiza el estado de snacks, cargandolo con los datos obtenidos de la API dada.
    '''
    snacks: dict = {}

    try:
        request_todos_los_snakcs = requests.get(API['BASE_URL'] + API['PATH']['TODOS_LOS_SNACKS'], headers=API['HEADERS'])
    except Exception as e:
        print('Error al consultar API request_todos_los_snakcs', str(e))

    if request_todos_los_snakcs.status_code == 200:
        snacks = request_todos_los_snakcs.json()

    totem['SNACKS'] = snacks



def cargar_cines(totem: dict) -> None: 
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se actualiza el estado de cines_info, cargandolo con los datos obtenidos de la API dada.
    '''
    CINES_INFO: dict = {}

    try:
        request_todos_los_cines = requests.get(API['BASE_URL'] + API['PATH']['TODOS_LOS_CINES'], headers=API['HEADERS'])
    except Exception as e:
        print('Error al consultar API todos_los_cines', str(e))

    if request_todos_los_cines.status_code == 200:
        cines: list = request_todos_los_cines.json()

        for cine in cines:
            cine_id: str = cine['cinema_id']
            request_url = (API['BASE_URL'] + API['PATH']['TODAS_LAS_PELIS_DEL_CINE']).replace('{cinema_id}', cine_id)

            try:
                request_todas_proyecciones_cine = requests.get(request_url, headers=API['HEADERS'])                
            except Exception as e:
                print('Error al consultar API request_todas_proyecciones_cine', str(e))

            if request_todas_proyecciones_cine.status_code == 200:
                proyecciones: list = request_todas_proyecciones_cine.json()

                CINES_INFO[cine_id] = cine | proyecciones[0]

        totem['CINES_INFO'] = CINES_INFO



def cargar_cartelera(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se actualiza el estado de cartelera_info, cargandolo con los datos obtenidos de la API dada.
    '''
    cartelera_info: dict = {}

    try:
        request_todas_las_pelis: list = requests.get(API['BASE_URL'] + API['PATH']['TODAS_LAS_PELIS'], headers=API['HEADERS'])
    except Exception as e:
        print('Error al consultar API request_todas_las_pelis', str(e))

    if request_todas_las_pelis.status_code == 200:
        peliculas: list = request_todas_las_pelis.json()

        for pelicula in peliculas:
            peli_desc: dict = {}
            poster: dict = {}
            movie_id: str = pelicula['movie_id']
            poster_id: str = pelicula['poster_id']
            
            request_url_peli_desc: str = (API['BASE_URL'] + API['PATH']['PELI_POR_ID']).replace('{movie_id}', movie_id)

            try:
                request_peli_desc: list = requests.get(request_url_peli_desc, headers=API['HEADERS'])
            except Exception as e:
                print('Error al consultar API request_url_peli_desc', str(e))

            if request_peli_desc.status_code == 200:
                peli_desc = request_peli_desc.json()
            
            request_url_peli_poster: str = (API['BASE_URL'] + API['PATH']['POSTER_POR_ID']).replace('{poster_id}', poster_id)

            try:
                request_peli_poster: list = requests.get(request_url_peli_poster, headers=API['HEADERS'])
            except Exception as e:
                print('Error al consultar API request_url_peli_poster', str(e))

            if request_peli_poster.status_code == 200:
                poster = request_peli_poster.json()
                
                poster_image: str = poster['poster_image']
                poster_image: str = poster_image.split('base64,')[1]
                poster['poster_image'] = base64.b64decode(poster_image)
                poster['poster_image'] = Image.open(io.BytesIO(poster['poster_image']))

            request_url_peli_cinemas: str = (API['BASE_URL'] + API['PATH']['DONDE_SE_PROYECTA']).replace('{movie_id}', movie_id)

            try:
                request_peli_cinemas: list = requests.get(request_url_peli_cinemas, headers=API['HEADERS'])
            except Exception as e:
                print('Error al consultar API request_url_peli_cinemas', str(e))

            if request_peli_cinemas.status_code == 200:
                cinemas = request_peli_cinemas.json()

            cartelera_info[movie_id] = pelicula | peli_desc | poster
            cartelera_info[movie_id]['cinemas'] = cinemas

    
    totem['CARTELERA_INFO'] = cartelera_info



def inicializar_totem(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se incializara el estado del totem, creando y cargando con los datos necesarios para la aplicacion.
    '''
    totem['ventanas']: dict = {}
    
    totem['compra']: dict = {
        'cantidad_entradas': 0,
        'snacks': {},
        'ubicacion_key': ''
    }

    totem['precio_entradas_general']: float = PRECIO_ENTRADAS_GENERAL
    totem['ubicacion']: str = ''

    totem['CARTELERA_INFO']: dict = {}
    totem['CINES_INFO']: dict = {}
    totem['SNACKS']: dict = {}
    totem['lugares_disponibles']: dict = {}

    cargar_cartelera(totem)
    cargar_cines(totem)
    cargar_snacks(totem)



def obtener_pelis_de_cinema(cine_elegido: str, totem: dict) -> list[dict]:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera una lista de diccionarios, las cuales son las peliculas del cine/ubicacion elegido.
    '''
    cines: dict = totem['CINES_INFO']
    peliculas: dict = totem['CARTELERA_INFO']

    encontrado: bool = False
    
    peliculas_del_cine: list[dict] = []
    cinema_id: str = ''

    for cine_id, info in cines.items():
        if not encontrado:
            if info['location'] == cine_elegido:
                cinema_id = str(info['cinema_id'])
                encontrado = True

    for pelicula_id, pelicula_info in peliculas.items():
        if cinema_id in pelicula_info['cinemas']:
            peliculas_del_cine.append(pelicula_info)

    return peliculas_del_cine


def mostrar_pelis_de_cinema(frame_lista_peliculas: Frame, ubicacion_cine: str, totem: dict, peliculas_busqueda: list[dict] = []) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se limpia el listado pintado de peliculas y se mostraran todas las pelicula de la ubicacion elegida. Si resulta de una busqueda se mostrara la que coincide con el nombre buscado en esa ubicacion (sala).
    '''

    for hijo in frame_lista_peliculas.winfo_children():
    #     hijo.grid_forget()
        hijo.destroy()
    
    totem['ubicacion'] = ubicacion_cine
    
    peliculas: list[dict] = []
    
    if len(peliculas_busqueda):
        peliculas = peliculas_busqueda
    else:
        peliculas: list[dict] = obtener_pelis_de_cinema(ubicacion_cine, totem)

    num_peliculas_por_fila = 2
    i: int = 0

    for pelicula in peliculas:
        poster_image = pelicula['poster_image']
        fila = i // num_peliculas_por_fila
        columna = i % num_peliculas_por_fila
        poster_image = ImageTk.PhotoImage(poster_image)

        btn: Button = Button(frame_lista_peliculas, image=poster_image, command = lambda pelicula=pelicula: mostrar_pantalla_secundaria(pelicula, totem) ) 
        btn.poster_image = poster_image
        
        btn.grid(row=int(fila + 1), column=int(columna), padx=10, pady=12)

        i += 1



        
def terminar_aplicacion(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Si cierra la ventana haciendo clic en la "x" preguntamos si esta seguro. Se cerrara o no la aplicacion segun respuesta.
    '''
    respuesta = messagebox.askyesno(title='Salir de la aplicacion', message='¿Esta segudo que desea salir de la aplicacion?')

    if respuesta:
        pantalla_principal = totem['ventanas']['pantalla_principal']
        pantalla_principal.destroy()







def main() -> None:
    totem:dict = {}

    inicializar_totem(totem)

    pantalla_principal = Tk()
    pantalla_principal.geometry('800x1500')
    pantalla_principal.title('Pantalla Principal')
    pantalla_principal.config(bg = 'black')

    totem['ventanas']['pantalla_principal'] = pantalla_principal

    diseño_pantalla_principal(totem)
    

    pantalla_principal.mainloop()


main()
