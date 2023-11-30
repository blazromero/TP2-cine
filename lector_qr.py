from tkinter import Tk, Entry, Button, Label, LabelFrame
import fitz
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

import cv2
import os

CARPETA_CODIGOS_QR = 'QR'
ARCHIVO_INGRESOS = 'ingresos.txt'
QR_INVALIDO = 'QR_ID INVALIDO'

def obtener_id_qr(cadena: str) -> str:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera una cadena la cual es el id del qr.
    '''
    return cadena.split(',')[0].replace('id_qr: ', '')

def guardar_ingreso_en_archivo(ingreso: str) -> bool:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera un boolean el cual es True si el guardado fue exitoso y False en caso contrario.
    '''
    try:
        with open(ARCHIVO_INGRESOS, 'a') as archivo:
            archivo.write(ingreso[:-1] + '\n')

        return True
    except Exception as e:
        print('Error:', str(e))

        return False

def cargar_ingresos() -> list[str]:
    '''
    PRE: Sin parametros de entrada.
    POST: Se devolvera una lista de string los ingresos guardados en el archivo ingesos.txt. Si el archivo no existe, se creara.
    '''
    ingresados: list[str] = []

    if os.path.exists(ARCHIVO_INGRESOS):
        
        with open(ARCHIVO_INGRESOS, 'r') as archivo:
            for linea in archivo:
                ingresados.append(obtener_id_qr(linea))
    else:

        with open(ARCHIVO_INGRESOS, 'a') as archivo:
            pass

    return ingresados

def decodificar_pdf(ruta_pdf: str) -> str:
    '''
    PRE: Se esperan la ruta del archivo pdf de forma correcta.
    POST: Se devolvera los datos del qr como string.
    '''

    qr_pdf = fitz.open(ruta_pdf)

    pagina = qr_pdf.load_page(0)
    qr_imagen = pagina.get_pixmap()

    qr_imagen_pil = Image.frombytes("RGB", [qr_imagen.width, qr_imagen.height], qr_imagen.samples)

    imagen_bytesio = BytesIO()
    qr_imagen_pil.save(imagen_bytesio, format='PNG')
    imagen_bytesio.seek(0)
    
    imagen_np = np.array(Image.open(imagen_bytesio))

    imagen_gris = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2GRAY)

    detector = cv2.QRCodeDetector()

    valor = detector.detectAndDecodeMulti(imagen_gris)

    qr_pdf.close()

    return valor[1][0]

def cargar_qr(entry_id_qr: Entry, frame_datos_qr: LabelFrame, ingresos: list[str]) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se limpiara la pantalla y luego se mostraran los datos del id del QR ingresado.
    '''

    for hijo in frame_datos_qr.winfo_children():
        hijo.destroy()

    id_qr: str = str(entry_id_qr.get())

    path_qr: str = os.path.join(CARPETA_CODIGOS_QR, f'{id_qr}.pdf')

    if os.path.exists(path_qr):
        data = decodificar_pdf(path_qr)
        ingreso: str = ""
        
        for line in data.splitlines():
            lbl_id_qr: Label = Label(frame_datos_qr, text=line.replace('_', ' ').title())
            lbl_id_qr.grid()
            if 'ubicacion_totem' not in line:
                ingreso += line +','

        if id_qr not in ingresos:
            if guardar_ingreso_en_archivo(ingreso):
                ingresos.append(id_qr)

                lbl_ingreso_invalido: Label = Label(frame_datos_qr, text=f'Qr {id_qr} ingresado', bg='green')
                lbl_ingreso_invalido.grid()
            else:
                lbl_ingreso_invalido: Label = Label(frame_datos_qr, text=f'No se pudo guardar el ingreso con Qr {id_qr}', bg='red')
                lbl_ingreso_invalido.grid()  
        else:
            lbl_ingreso_invalido: Label = Label(frame_datos_qr, text=f'Qr {id_qr} ya ingresado', bg='red')
            lbl_ingreso_invalido.grid()
    else:
        lbl_no_encontrado: Label = Label(frame_datos_qr, text=f'Qr {id_qr} no encontrado', bg='red')
        lbl_no_encontrado.grid()

def obtener_id_qr_desde_qr(data: str) -> str:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera un string con el id del QR.
    '''
    id_qr: str = ''

    if 'id_qr' not in data:
        return QR_INVALIDO

    id_qr = data.split('\n')[0]
    id_qr = id_qr.replace(' ', '')
    id_qr = id_qr.split(':')[1]

    return id_qr

def scanear_codigo_qr(entry_id_qr: Entry,frame_lista_peliculas: LabelFrame, ingresos: list[str]) -> None:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se abrira la camara para leer el QR y se llenara el text con el id del QR.
    '''
    entry_id_qr.delete(0, 'end')

    captura = cv2.VideoCapture(0)
    datos_capturados: bool = False
    id_qr: str = ''

    while not datos_capturados:
        ret, frame = captura.read()

        qrDetecto = cv2.QRCodeDetector()

        qr_data, bbox, rectifiedImage = qrDetecto.detectAndDecode(frame) 

        if cv2.waitKey(1) == ord('s'):
            break

        if len(qr_data):
            cv2.imshow('webCam', rectifiedImage)
            id_qr = obtener_id_qr_desde_qr(qr_data)
            datos_capturados = True
        else:
            cv2.imshow('webCam', frame)
    
    captura.release()
    cv2.destroyAllWindows()

    entry_id_qr.insert(0, id_qr)
    cargar_qr(entry_id_qr, frame_lista_peliculas, ingresos)

def main() -> None:
    '''
    PRE: Sin parametros.
    POST: Punto de entrada de la aplicacion. Se mostrara la pantalla principal.
    '''
    ingresos: list[str] = cargar_ingresos()

    pantalla_principal: Tk = Tk()
    pantalla_principal.title('Pantalla Principal')
    pantalla_principal.geometry('250x300')

    lbl_id_qr: Label = Label(pantalla_principal, text='Id del QR:')
    lbl_id_qr.grid(row=0, column=0)
    entry_id_qr: Entry = Entry(pantalla_principal)
    entry_id_qr.grid(row=0, column=1)
   
    btn_cargar_qr: Button = Button(pantalla_principal, text='Cargar',command=lambda: cargar_qr(entry_id_qr, lblframe_datos_qr, ingresos))
    btn_cargar_qr.grid(row=0, column=2)

    btn_scanear_qr: Button = Button(pantalla_principal, text='Scanear QR', command= lambda:scanear_codigo_qr(entry_id_qr,lblframe_datos_qr, ingresos))
    btn_scanear_qr.grid(row=1, column=1)

    lblframe_datos_qr: LabelFrame = LabelFrame(pantalla_principal, text='Datos de la entrada:')
    lblframe_datos_qr.grid(row=2, columnspan=3)

    pantalla_principal.mainloop()

main()
