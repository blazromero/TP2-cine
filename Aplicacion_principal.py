from tkinter import Tk, Toplevel, Entry, Button, Label, Frame, Spinbox, messagebox, OptionMenu, StringVar, LabelFrame, Canvas, Scrollbar
import qrcode
import os
import datetime
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

    totem['ventanas']['pantalla_reserva'] = pantalla_reserva

    lbl_precio_entrada: Label = Label(pantalla_reserva, text=f'Precio unitario ${precio_entradas}')
    lbl_precio_entrada.grid(row=0, column=1)

    lbl_cantidad_entradas = Label(pantalla_reserva, text="Cantidad de entradas")
    lbl_cantidad_entradas.grid(row=1, column=0)

    spin_cantidad_entradas = Spinbox(pantalla_reserva, from_=1, to=MAX_ENTRADAS, validate='key', width=5)
    spin_cantidad_entradas['validatecommand'] = (spin_cantidad_entradas.register(isNumber), '%P')
    spin_cantidad_entradas.config(command= lambda: spinbox_fondo_blanco(spin_cantidad_entradas))
    spin_cantidad_entradas.grid(row=1, column=1)

    btn_agregar_al_carrito: Button = Button(pantalla_reserva, text='Agregar al carrito', command= lambda:agregar_al_carrito(totem, cantidad_entradas=spin_cantidad_entradas, lbl_mas_info=lbl_mas_info))
    btn_agregar_al_carrito.grid(row=1, column=2)
    
    lblframe_lista_snacks: LabelFrame = LabelFrame(pantalla_reserva, text='Snacks')
    lblframe_lista_snacks.grid(row=4, columnspan=3)

    btn_agregar_snacks: Button = Button(pantalla_reserva, text='Agregar Snacks', command=lambda:mostrar_snacks(lblframe_lista_snacks, totem))
    btn_agregar_snacks.grid(row=3, column=1)

    lbl_mas_info = Label(pantalla_reserva, text="")
    lbl_mas_info.grid_forget()

    bnt_listo: Button = Button(pantalla_reserva, text='Listo!', bg='green', command= lambda: volver_a_pantalla_secundaria(pantalla_reserva, totem))
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


def mostrar_pantalla_secundaria(pelicula, totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se muestra la pantalla secundaria con sus componentes pintados (con descripcion de la pelicula). Se actualiza el estado de la compra.
    '''
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
    pantalla_secundaria.title(nombre_pelicula)
    pantalla_secundaria.geometry('300x665')

    totem['ventanas']['pantalla_secundaria'] = pantalla_secundaria

    btn_volver: Button = Button(pantalla_secundaria, text='Volver a pantalla principal', command= lambda:volver_a_principal(pantalla_secundaria, totem))
    btn_volver.pack()

    lblframe_nombre_peli: LabelFrame = LabelFrame(pantalla_secundaria, text='Pelicula:')
    lblframe_nombre_peli.pack()
    
    lbl_nombre_peli: Label = Label(lblframe_nombre_peli, text=nombre_pelicula)
    lbl_nombre_peli.pack()

    lblframe_synopsis: LabelFrame = LabelFrame(pantalla_secundaria, text='Synopsis:')
    lblframe_synopsis.pack()

    lbl_synopsis: Label = Label(lblframe_synopsis, text=synopsis, wraplength=200)
    lbl_synopsis.pack()

    lblframe_actores: LabelFrame = LabelFrame(pantalla_secundaria, text='Actores:')
    lblframe_actores.pack()

    lbl_actores: Label = Label(lblframe_actores, text=actores, wraplength=200)
    lbl_actores.pack()

    lblframe_genero: LabelFrame = LabelFrame(pantalla_secundaria, text='Genero:')
    lblframe_genero.pack()

    lbl_genero: Label = Label(lblframe_genero, text=genero)
    lbl_genero.pack()

    lblframe_duracion: LabelFrame = LabelFrame(pantalla_secundaria, text='Duracion:')
    lblframe_duracion.pack()

    lbl_duracion: Label = Label(lblframe_duracion, text=duracion)
    lbl_duracion.pack()

    if hay_asientos_disponibles(MIN_ENTRADAS, totem):
        btn_reservar: Button = Button(pantalla_secundaria, text='Reservar', command= lambda: mostrar_pantalla_reserva(totem))
        btn_reservar.pack()
    else:
        lbl_entradas_agotadas: Label = Label(pantalla_secundaria, text='Entradas agotadas.', bg='yellow')
        lbl_entradas_agotadas.pack()

    pantalla_secundaria.protocol("WM_DELETE_WINDOW", lambda: terminar_aplicacion(totem))


def isNumber(age_spinbox: Spinbox) -> bool:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Devolvemos un bool para decir si la cadena es un numero, True en caso afirmativo, False en caso contrario.
    '''
    return age_spinbox.isdigit() 


def mostrar_peli_buscada(frame_lista_peliculas: Frame, pelicula: Entry, totem: dict, ubicacion_elejida: str) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se limpa el listado pintado de peliculas y se mostrara la pelicula que coincide con el nombre buscado.
    '''
    for hijo in frame_lista_peliculas.winfo_children():
        hijo.destroy()

    peli_a_buscar: str = pelicula.get().lower()

    if not len(peli_a_buscar):
        mostrar_pelis_de_cinema(frame_lista_peliculas, ubicacion_elejida, totem)
    else:
        peliculas = totem['CARTELERA_INFO']
        cine_id: str = obtener_id_cinema(ubicacion_elejida, totem)

        resultado: list[dict] = []

        for peli_id, peli_info in peliculas.items():
            pelis_name_splited: list = (peli_info['name']).lower().split(' ')

            for peli_mame in pelis_name_splited:
                if peli_a_buscar in peli_mame:
                    cines_ids: list[str] = peli_info['cinemas']

                    if cine_id in cines_ids:
                        resultado.append(peli_info)
        
        if len(resultado):
            mostrar_pelis_de_cinema(frame_lista_peliculas, ubicacion_elejida, totem, resultado)
   

def generar_qr(totem: dict, checkout_pelicula: Toplevel, btn_pagar: Button) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se genera un archivo .png que es la imagen del QR dentro de la carpeta QR. El nombre del archivo es el id del QR.
    '''
    compra: dict = totem['compra']
    lugares_disponibles: dict = totem['lugares_disponibles']

    if 'pelicula' in compra and 'ubicacion_key' in compra:
        ubicacion_key: dict = compra['ubicacion_key']
        id_qr: int = int(datetime.datetime.now().timestamp())

        timestamp: str = str(datetime.datetime.now())
        timestamp = timestamp.split('.')[0]
        timestamp = timestamp[:-3]
        
        nombre_pelicula: str = compra['pelicula']
        ubicacion_totem: str = compra['ubicacion']
        cant_entradas: int = int(compra['cantidad_entradas'])
        total_consumido: str = compra['total_consumido']

        if not hay_asientos_disponibles(cant_entradas, totem):
            lbl_entradas_agotadas: Label = Label(checkout_pelicula, text='Entradas agotadas.', bg='yellow')
            lbl_entradas_agotadas.grid()
        else:
            archivo_qr_path: str = os.path.join(CARPETA_CODIGOS_QR, str(id_qr))
            lugares_disponibles[ubicacion_key] -= cant_entradas

            img = qrcode.make(f'ID_QR: {id_qr}\nnombre_pelicula: {nombre_pelicula}\nubicacion_totem: {ubicacion_totem}\ncant_entradas: {cant_entradas}\ntimestamp: {timestamp}\ntotal_consumido: {total_consumido}'.lower())
            img.save(archivo_qr_path + '.png')

            imagen = Image.open(archivo_qr_path + '.png')
            imagen = imagen.convert('RGB')

            imagen.save(archivo_qr_path + '.pdf')

            os.remove(archivo_qr_path + '.png')

            lvl_qr_generado: Label = Label(checkout_pelicula, text='Qr Generado', bg='green')
            lvl_qr_generado.grid(sticky='ew')

            btn_pagar['state'] = 'disabled'
            btn_pagar['bg'] = 'grey'

        reiniciar_compra(compra)
    else:
        lvl_qr_generado: Label = Label(checkout_pelicula, text='Debe primero elegir una pelicula', bg='red')
        lvl_qr_generado.grid(sticky='ew')

    
def mostrar_pantalla_checkout(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se pintan todos los componenes de la pantalla checkout con la informacion de la compra.
    '''
    pantalla_principal = totem['ventanas']['pantalla_principal']
    pantalla_principal.withdraw()

    compra = totem['compra']

    total: float = 0.00
    subtotal_entradas: float = 0.00
    subtotal_snacks: float = 0.00
    nombre_pelicula: str = ''

    if not 'pelicula' in compra:
        nombre_pelicula = 'Sin Pelicula'
    else:
        nombre_pelicula = compra['pelicula']

    pantalla_checkout = Toplevel()
    pantalla_checkout.title(nombre_pelicula)
    pantalla_checkout.geometry('350x450')

    cantidad_entradas: int = compra['cantidad_entradas']
    precio_unitario_entrada: float = 0.00

    if 'precio_entrada' in compra:
        precio_unitario_entrada = compra['precio_entrada']

    lblframe_info_entrada: LabelFrame = LabelFrame(pantalla_checkout, text='Entrada/s:', font=CHECKOUT_FONT)
    lblframe_info_entrada.grid(row=0, sticky='ew', padx = 10)

    lbl_pelicula: Label = Label(lblframe_info_entrada, text='Pelicula')
    lbl_pelicula.grid(row=0, column=0)
    lbl_pelicula_nombe: Label = Label(lblframe_info_entrada, text = nombre_pelicula.title(), wraplength=80)
    lbl_pelicula_nombe.grid(row=1, column=0)

    lbl_cantidad_entradas: Label = Label(lblframe_info_entrada, text = 'Cantidad')
    lbl_cantidad_entradas.grid(row=0, column=1)
    lbl_cantidad_entrada: Label = Label(lblframe_info_entrada, text = cantidad_entradas)
    lbl_cantidad_entrada.grid(row=1, column=1)
    lbl_precio_unitario: Label = Label(lblframe_info_entrada, text = 'Precio U.')
    lbl_precio_unitario.grid(row=0, column=2)
    lbl_precio_entrada: Label = Label(lblframe_info_entrada, text = precio_unitario_entrada)
    lbl_precio_entrada.grid(row=1, column=2)

    subtotal_entradas = float(cantidad_entradas) * float(precio_unitario_entrada)
    
    lbl_subtotal_entradas: Label = Label(lblframe_info_entrada, text = 'Subtotal')
    lbl_subtotal_entradas.grid(row=0, column=3)
    lbl_subtotal_entrada: Label = Label(lblframe_info_entrada, text = subtotal_entradas)
    lbl_subtotal_entrada.grid(row=1, column=3)

    lbl_subtotal_final_entrada: Label = Label(lblframe_info_entrada, text = 'Subtotal Entrada/s:', font=CHECKOUT_FONT)
    lbl_subtotal_final_entrada.grid(row=2, column=2)
    lbl_subtotal_final_calculado: Label = Label(lblframe_info_entrada, text = subtotal_entradas, font=CHECKOUT_FONT)
    lbl_subtotal_final_calculado.grid(row=2, column=3)

    if len(compra['snacks'].keys()):
        snacks: dict = compra['snacks']
        lblframe_lista_snacks: LabelFrame = LabelFrame(pantalla_checkout, text='Snacks:', font=CHECKOUT_FONT)
        lblframe_lista_snacks.grid(row=1, sticky='ew', padx = 10)

        lbl_lista_nombre: Label = Label(lblframe_lista_snacks, text='Snack')
        lbl_lista_nombre.grid(row=0, column=0)
        lbl_lista_cantidad: Label = Label(lblframe_lista_snacks, text='Cantidad')
        lbl_lista_cantidad.grid(row=0, column=1)
        lbl_lista_preciou: Label = Label(lblframe_lista_snacks, text='Precio U.')
        lbl_lista_preciou.grid(row=0, column=2)
        lbl_lista_subtotal: Label = Label(lblframe_lista_snacks, text='Subtotal')
        lbl_lista_subtotal.grid(row=0, column=3)

        i: int = 1
        
        for snack in snacks:
            cantidad_snack: int = compra['snacks'][snack]['cantidad']
            precio_unitario_snack: float = compra['snacks'][snack]['precio_unidad']

            texto_snack: str = snack.title().replace('_', ' ')
            lbl_nombre_snack: Label = Label(lblframe_lista_snacks, text = texto_snack)
            lbl_nombre_snack.grid(row=i, column=0)

            lbl_cantidad_snack: Label = Label(lblframe_lista_snacks, text = cantidad_snack)
            lbl_cantidad_snack.grid(row=i, column=1)

            lbl_precio_snack_unidad: Label = Label(lblframe_lista_snacks, text = precio_unitario_snack)
            lbl_precio_snack_unidad.grid(row=i, column=2)
            
            subtotal_snack: float = float(cantidad_snack) * float(precio_unitario_snack)
            lbl_subtotal_snack: Label = Label(lblframe_lista_snacks, text = subtotal_snack)
            lbl_subtotal_snack.grid(row=i, column=3)

            total += float(cantidad_snack) * float(precio_unitario_snack)
            subtotal_snacks += subtotal_snack
            i +=1

        lbl_subtotal_snacks: Label = Label(lblframe_lista_snacks, text = 'Subtotal Snack/s:', font=CHECKOUT_FONT)
        lbl_subtotal_snacks.grid(row=i, column=2)
        lbl_subtotal_snacks: Label = Label(lblframe_lista_snacks, text = subtotal_snacks, font=CHECKOUT_FONT)
        lbl_subtotal_snacks.grid(row=i, column=3)

    lblframe_total: LabelFrame = LabelFrame(pantalla_checkout, text ='Total:', font=CHECKOUT_FONT)
    lblframe_total.grid()

    total = subtotal_entradas + subtotal_snacks
    compra['total_consumido'] = total
    lbl_total_sumatoria: Label = Label(lblframe_total, text = total, font=CHECKOUT_FONT)
    lbl_total_sumatoria.grid(column=0, padx=10)

    btn_pagar: Button = Button(lblframe_total, text='Pagar', width=15, bg='green',command= lambda: generar_qr(totem, pantalla_checkout, btn_pagar))
    btn_pagar.grid(row=0, column=1, padx=10, pady=10)

    btn_pantalla_principal: Button = Button(pantalla_checkout, text='Volver', command= lambda: volver_a_principal(pantalla_checkout, totem))
    btn_pantalla_principal.grid(pady=10)

    pantalla_checkout.protocol("WM_DELETE_WINDOW", lambda: terminar_aplicacion(totem))


def obtener_ubicacion_cines(totem: dict) -> list[str]:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera una lista de string, las cuales son las ubicaciones de los cines.
    '''
    cines: dict = totem['CINES_INFO']
    ubicaciones: list[str] = []

    for key, value in cines.items():
        ubicaciones.append(value['location'])

    
    return ubicaciones


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
    POST: Se limpa el listado pintado de peliculas y se mostraran todas las pelicula de la ubicacion elegida. Si resulta de una busqueda se mostrara la que coincide con el nombre buscado en esa ubicacion (sala).
    '''

    for hijo in frame_lista_peliculas.winfo_children():
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


def meter_scroll_en_frame(frame_lista_peliculas) -> None:
    my_canvas = Canvas(frame_lista_peliculas, width=500, height=800)
    my_scrollbar = Scrollbar(frame_lista_peliculas, orient='vertical', command=my_canvas.yview)
    scrollable_frame_peliculas = Frame(my_canvas)

    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox('all')))
    my_canvas.create_window((0,0), window=scrollable_frame_peliculas)
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.grid(row=0, column=0, sticky='news')

    my_scrollbar.grid(row=0, column=1, sticky='ns')

    return scrollable_frame_peliculas


def mostrar_pantalla_principal(totem: dict) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se pintara la pantalla principal con sus componentes. Ubicacion a elegir, listados de peliculas y buscar.
    '''
    pantalla_principal = totem['ventanas']['pantalla_principal']


    lbl_totem_ubicacion: Label = Label(pantalla_principal, text='Ubicacion:', pady=10)
    lbl_totem_ubicacion.grid(row=0, column=0)


    cine_ubicaciones = obtener_ubicacion_cines(totem)
    valor_option: StringVar = StringVar()
    valor_option.set(cine_ubicaciones[0])

    frame_lista_peliculas: Frame = Frame(pantalla_principal)
    opcion_ubicacion: OptionMenu = OptionMenu(pantalla_principal, valor_option, *cine_ubicaciones, command=lambda valor_option=valor_option: mostrar_pelis_de_cinema(scrollable_frame_peliculas, valor_option, totem))
    opcion_ubicacion.grid(row=0, column=1, columnspan=2, sticky='news', pady=10)

    lbl_buscar_peli: Label = Label(pantalla_principal, text='Buscar Peli:')
    lbl_buscar_peli.grid(row=1, column=0)

    entry_pelicula: Entry = Entry(pantalla_principal)
    entry_pelicula.grid(row=1, column=1)

    btn_buscar: Button = Button(pantalla_principal, text='Buscar', command= lambda: mostrar_peli_buscada(scrollable_frame_peliculas, entry_pelicula, totem, valor_option.get()))
    btn_buscar.grid(row=1, column=2)

    btn_buscar: Button = Button(pantalla_principal, text='Checkout/Finalizar compra', command= lambda: mostrar_pantalla_checkout(totem))
    btn_buscar.grid(row=1, column=3)

    lbl_aclaracion: Label = Label(pantalla_principal, text=ACLARACION_FUNCIONES_PELICULAS, wraplength=200, bg='CadetBlue', font=ACLARACION_FONT)
    lbl_aclaracion.grid(row=2, column=1, columnspan=2, sticky='news', pady=20)


    frame_lista_peliculas.grid(row=3, columnspan=4)

    scrollable_frame_peliculas = meter_scroll_en_frame(frame_lista_peliculas)
    mostrar_pelis_de_cinema(scrollable_frame_peliculas, valor_option.get(), totem)


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
    '''
    PRE: Sin parametros.
    POST: Punto de entrada de la aplicacion. Se mostrara la pantalla principal.
    '''
    totem: dict = {}

    inicializar_totem(totem)

    pantalla_principal: Tk = Tk()
    pantalla_principal.title('Pantalla Principal')
    pantalla_principal.geometry('600x1500')

    totem['ventanas']['pantalla_principal'] = pantalla_principal

    mostrar_pantalla_principal(totem)

    pantalla_principal.mainloop()


main()