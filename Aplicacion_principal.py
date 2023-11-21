from tkinter import Tk, Toplevel, Entry, Button, Label, Frame,  LabelFrame
import requests
from PIL import Image
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

def mostrar_ventana_secundaria()-> None:
    ventana_secundaria = Tk()
    ventana_secundaria.geometry('400x800')
    ventana_secundaria.title('Pelicula')
    ventana_secundaria.config(bg= 'black')

    ventana_secundaria.mainloop()



def diseño_pantalla_principal(pantalla_principal, totem)-> dict:
    pantalla_principal = pantalla_principal

    
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
    
    boton_1 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_1.grid(row= 3, column= 2,pady= 5, padx= 5)

    boton_2 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_2.grid(row= 4, column= 2,pady= 5, padx= 5)

    boton_3 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_3.grid(row= 5, column= 3,pady= 5, padx= 5)

    boton_4 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_4.grid(row= 6, column= 3, pady= 5, padx= 5)

    boton_5 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_5.grid(row= 3, column= 3,pady= 5, padx= 5)

    boton_6 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_6.grid(row= 4, column= 3,pady= 5, padx= 5)

    boton_7 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_7.grid(row= 5, column= 2,pady= 5, padx= 5)

    boton_8 = Button(pantalla_principal, text= 'pelicula', command=lambda: mostrar_ventana_secundaria(), height= 20 , width= 25)
    boton_8.grid(row= 6, column= 2, pady= 5, padx= 5)

    boton_buscar: Button = Button(text='buscar', height= 1, width=6)
    boton_buscar.grid(row=1, column=3)

    boton_buscar: Button = Button(text='Finalizar Compra', height= 1, width=15)
    boton_buscar.grid(row=1, column=4)


    lbl_aclaracion: Label = Label(pantalla_principal, text=ACLARACION_FUNCIONES_PELICULAS, wraplength=200, bg='CadetBlue', font=ACLARACION_FONT)
    lbl_aclaracion.grid(row=2, column=2, columnspan=2, sticky='news', pady=20)
    entrada_usuario = Entry(pantalla_principal, width= 25)
    entrada_usuario.grid(row=1, column=2)

    

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










def main() -> None:
    totem:dict = {}
    
    pantalla_principal = Tk()
    pantalla_principal.geometry('800x1500')
    pantalla_principal.title('Pantalla Principal')
    pantalla_principal.config(bg = 'black')

    diseño_pantalla_principal(pantalla_principal, totem)
    
    pantalla_principal.mainloop()


main()
