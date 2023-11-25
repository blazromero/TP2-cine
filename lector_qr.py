from tkinter import Tk, Entry, Button, Label, LabelFrame
import os
import cv2

CARPETA_CODIGOS_QR = 'QR'
ARCHIVO_INGRESOS = 'ingresos.txt'


def obtener_id_qr(cadena: str) -> str:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera una cadena la cual es el id del qr.
    '''
    return cadena.split(',')[0].replace('id_qr: ', '')

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

def cargar_qr(entry_id_qr: Entry, frame_datos_qr: LabelFrame, ingresos: list[str]) -> None:
    pass

def obtener_id_qr_desde_qr(data: str) -> str:
    '''
    PRE: Se esperan los parametros solicitado de forma correcta.
    POST: Se devolvera un string con el id del QR.
    '''
    pass

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
