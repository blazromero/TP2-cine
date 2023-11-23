from tkinter import Tk, Entry, Button, Label, LabelFrame

CARPETA_CODIGOS_QR = 'QR'
ARCHIVO_INGRESOS = 'ingresos.txt'


def cargar_ingresos() -> list[str]:
    pass

def cargar_qr(entry_id_qr: Entry, frame_datos_qr: LabelFrame, ingresos: list[str]) -> None:
    pass

def scanear_codigo_qr(entry_id_qr: Entry,frame_lista_peliculas: LabelFrame, ingresos: list[str]) -> None:
    pass

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
