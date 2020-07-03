# -*- coding: utf-8 -*-
import time
from selenium import webdriver #(herramienta scrapper)
from selenium.webdriver.chrome.options import Options #configuración selenium
from bs4 import BeautifulSoup  #ver pag web en estructura de arbol con elementos
from datetime import date
import platform #conocer sistema operativo
import os.path
import os
import re


import itertools

def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def extraccion_precios(log_file, log_file_error):

# CONFIGURACIÓN BUSCADOR LOCAL

    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--headless") #no abrir navegador
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    path = os.path.abspath(os.getcwd())

    if platform.system() == "Windows":
        driver = webdriver.Chrome(path + '/chromedriver83_win.exe', options=options)
    elif platform.system() == "Linux":
        driver = webdriver.Chrome(path + '/chromedriver83_linux', options=options)
    elif platform.system() == "Darwin":
        driver = webdriver.Chrome(path + '/chromedriver83_mac', options=options)
    else:
        with open(log_file_error, "w+") as myfile:
            myfile.write("Sistema operativo no compatible con el scrapper! \n")

#CONFIGURACIÓN URL

    url = 'https://www.zooplus.es/' #ver si hay alguna desde la que interese más empezar!
    driver.get(url)

    with open(log_file, "w+") as myfile:
        myfile.write("Starting ETL: " + str(date.today()) + "\n")


#LISTA PRINCIPAL (NOMBRES MASCOTAS)

    #Obtener índices (para acceso) y nombres (para log) de la lista principal
    time.sleep(1)
    num_elementos_principales = len(driver.find_elements_by_css_selector("a[class^=nav-header]"))
    tipo_mascota = BeautifulSoup(driver.page_source, "html.parser").select('a[class*=nav-header]')

    #Extraer nombres de lista para log
    lista_tipo_mascota_limpia = []
    for tipo in tipo_mascota:
        lista_tipo_mascota_limpia.append(tipo.text.replace(" ", "").replace("\n", ""))
    with open(log_file, "a+") as myfile:
        myfile.write("Se han encontrado " + str(num_elementos_principales) + " categorías principales: " + str(lista_tipo_mascota_limpia) + "\n")


    #Recorrer elementos y subelementos lista principal por índices
    for index_mascota in range(num_elementos_principales):
        nombre_mascota = lista_tipo_mascota_limpia[index_mascota]

        #ACCEDER A CATEGORÍA PRINCIPAL (tipo mascota)
        time.sleep(1)
        driver.find_elements_by_css_selector("a[class^=nav-header]")[index_mascota].click()
        with open(log_file, "a+") as myfile:
            myfile.write("Se ha accedido con éxito a la categoría: " + str(nombre_mascota) + "\n")

        #ACCEDER A SUBCATEGORÍAS DE CADA MASCOTA
        time.sleep(1)
        num_elementos_subcategoria = len(driver.find_elements_by_xpath("//div[@class='lhs-nav']/ul/li/a"))
        div_lista_subcategoria = BeautifulSoup(driver.page_source, "html.parser").select('div[class*=lhs-nav]')
        lista_subcategoria = []

        for div in div_lista_subcategoria:
            for ul in div.findAll('ul'):
                for li in ul.findAll('li'):
                    lista_subcategoria.append(li.text.replace("\n", ""))

        with open(log_file, "a+") as myfile:
            myfile.write("Se han encontrado " + str(num_elementos_subcategoria) + " subcategorias: " + str(lista_subcategoria) + "\n")

        for index_subcategoria in range(num_elementos_subcategoria):
            time.sleep(1)
            driver.find_elements_by_xpath("//div[@class='lhs-nav']/ul/li/a")[index_subcategoria].click()
            time.sleep(1)
            nombre_subcategoria = lista_subcategoria[index_subcategoria]

            #ACCEDER A SECCIONES DE CADA SUBCATEGORÍA  DE CADA MASCOTA

            paneles_subcategoria = BeautifulSoup(driver.page_source, "html.parser").select('div[class*=category__list__box]')
            panel_lista_secciones_subcategoria = []
            panel_lista_secciones_subcategoria_xpaths = []
            existe_panel_marcas = 0
            for panel in range(len(paneles_subcategoria)):
                #si existe panel marcas, me traigo todos los elementos (a) de ese panel a partir de su xpath generado
                time.sleep(1)
                if ("Todas las marcas de la A a la Z" in str(paneles_subcategoria[panel].findAll('h2'))) or ("Prueba las siguientes marcas" in str(paneles_subcategoria[panel].findAll('h2'))):
                    time.sleep(1)
                    elements = paneles_subcategoria[panel].findAll('a')
                    for elem in elements:
                        panel_lista_secciones_subcategoria.append(elem.text.replace("\n", "").strip())
                        panel_lista_secciones_subcategoria_xpaths.append(xpath_soup(elem))
                    num_elementos_secciones_subcategoria = len(panel_lista_secciones_subcategoria_xpaths)
                    with open(log_file, "a+") as myfile:
                        myfile.write("Se han encontrado " + str(num_elementos_secciones_subcategoria) + " secciones en la subcategoría " + str(lista_subcategoria[index_subcategoria]) + ": " + str(panel_lista_secciones_subcategoria) + "\n")
                    existe_panel_marcas = 1
                elif existe_panel_marcas == 0 and panel == len(paneles_subcategoria)-1:
                    for panel2 in range(len(paneles_subcategoria)):
                        time.sleep(1)
                        enlaces_en_el_panel = paneles_subcategoria[panel2].findAll('a')
                        for elem in enlaces_en_el_panel:
                            panel_lista_secciones_subcategoria_xpaths.append(xpath_soup(elem))
                            panel_lista_secciones_subcategoria.append(elem.text.replace("\n", "").strip())
                    num_elementos_secciones_subcategoria = len(driver.find_elements_by_xpath("//div[@class='category__content']/div/a"))
                    with open(log_file, "a+") as myfile:
                        myfile.write("Se han encontrado " + str(num_elementos_secciones_subcategoria) + " secciones en la subcategoría " + str(lista_subcategoria[index_subcategoria]) + ": " + str(panel_lista_secciones_subcategoria) + "\n")
                    #print("Se han encontrado" + str(num_elementos_secciones_subcategoria) + " número de secciones en la subcategoría: " + str(div_lista_secciones_subcategoria))
                else:
                    pass



            #ACCEDER A PROODUCTOS Y PRECIOS DE CADA SUBCATEGORÍA DE CADA SECCIÓN DE CADA MASCOTA (Directamente a partir de la lista de xpaths generados en la función anterior)
            for elemento_panel in panel_lista_secciones_subcategoria_xpaths:
                time.sleep(0.5)
                driver.find_element_by_xpath(elemento_panel).click()

                cajas_todos_productos = BeautifulSoup(driver.page_source, "html.parser").select('div[class*="row product__list product__list__min-info"]')
                for caja_producto in cajas_todos_productos:
                    titulo_caja = caja_producto.findAll('h3')
                    caja_dias_de_entrega = caja_producto.findAll("div", {"class",'inline__boxes delivery-info hidden-xs'})
                    caja_con_modelos = caja_producto.findAll("div", {"class", 'product__offer'})
                    caja_con_precios = caja_producto.findAll("div", {"class",'product__prices_col'})



                    estrellas_producto = 5 - len(caja_producto.findAll("span", {"class", 'icon-star empty__star'}))
                    titulo_producto = []
                    dias_de_entrega = []
                    nombre_modelo = []
                    precio_original_y_por_peso = []
                    precio_x_kg = []
                    # Sacamos los títulos para cada caja
                    for titulo_producto_caja in titulo_caja:
                        enlace_titulo_producto = titulo_producto_caja.findAll("a")
                        for texto_enlace_titulo_producto in enlace_titulo_producto:
                            titulo_producto = texto_enlace_titulo_producto.text.replace("\n", "").strip()

                    for dias_entrega_small in caja_dias_de_entrega:
                        conjunto_dias_entrega_small = dias_entrega_small.findAll("small")
                        for span_dias_entrega in conjunto_dias_entrega_small:
                            dias_de_entrega = span_dias_entrega.find("span").text.replace("\n", "").strip()

                    for caja_modelo_unidad in caja_con_modelos:
                        conjunto_dias_entrega_small = caja_modelo_unidad.findAll("div", {"class": "ui-text--small"})
                        for nombre_modelo_small in conjunto_dias_entrega_small:
                            nombre_modelo.append(nombre_modelo_small.text.split("\n", 3)[2].strip())
                    for caja_modelo_unidad_precios in caja_con_precios:
                        conjunto_dias_entrega_small = caja_modelo_unidad_precios.findAll("span", {"class": "product__smallprice__text"})
                        for nombre_modelo_small in conjunto_dias_entrega_small:
                            string_precios = nombre_modelo_small.text.split("\n", 1)[1].replace("\n", "").strip() #aplcir esto solo a pares
                            while '  ' in nombre_modelo_small:
                                string_precios = string_precios.replace('  ', ' ')
                            precio_original_y_por_peso.append(string_precios)
                        print(precio_original_y_por_peso)



                    # Extraidos los datos los unimos en un csv
                    print("Nombre del producto: " + titulo_producto)
                    print("Días de entrega: " + dias_de_entrega)
                    print("Número de estrellas: " + str(estrellas_producto))
                    print("Nombre modelos: " + str(nombre_modelo))
                    print("Precio original: " + str(precio_original_y_por_peso[::2]))
                    print("Precio por Kg: " + str(precio_x_kg[1::2]))

                driver.back()

            driver.back()


        #except:
        #    with open(log_file_error, "a+") as myfile:
        #        myfile.write("Error al acceder a la categoría número: " + str(nombre_mascota) + "\n")
        time.sleep(2) #para que de tiempo a verlo en la pestaña -> quitar cuando este acabado
        driver.back()




#EJECUTAR SCRIPT
if __name__ == '__main__':
    log_file_error = 'error.txt'
    log_file = 'log.txt'
    extraccion_precios(log_file, log_file_error)


