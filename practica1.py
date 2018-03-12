#!/usr/bin/python3

import webapp
import csv
import os
import urllib.parse

class acortadorURLs(webapp.webApp):
	URLs_introcucidas = {}
	URLs_acortadas = {}
	
	try:
		with open("fichero", "r") as fichero:
			if os.stat("fichero").st_size == 0:
				print("El fichero está vacío")
			else:
				reader = csv.reader(fichero)
				for fila in reader:
					URL_acortada = fila[0]
					URL_introducida = fila[1]
					URLs_introcucidas[URL_acortada] = URL_introducida
					URLs_acortadas[URL_introducida] = URL_acortada
	#Si el fichero no existe lo creo nada más empezar para luego poder usarlo				
	except IOError: 
		NuevoFichero = open("fichero", 'w')
		NuevoFichero.close()

	def parse(self, request):
		try:
			metodo = request.split(' ',2)[0] #Almaceno el GET o el POST
		except IndexError:
			metodo = ""
		try:
			recurso = request.split(' ',2)[1] #/xx
		except IndexError:
			recurso = ""
		try:
			cuerpo = request.split('\r\n\r\n')[1] #query string para el POST
		except IndexError:
			cuerpo =""
		return(metodo, recurso, cuerpo)
		
	#Obtener las urls
	def list_URLsAcort(self):
		listaURLs = ""
		for url in self.URLs_introcucidas:
			URL_acortada = url
			URL_introducida = self.URLs_introcucidas[URL_acortada]
			listaURLs = listaURLs + "<p><a href=" +  URL_introducida + ">" + URL_introducida + "</a>" "........." + "<a href=" + URL_acortada + ">" + URL_acortada + "</a></p>"
		return listaURLs
	
	def NoEncontrado():
		return("HTTP/1.1 404 Not found", "<html><body>Not found</body></html>")

	def process(self, parsedRequest):
		try:
			metodo, recurso, cuerpo = parsedRequest
		except TypeError:
			return (NoEncontrado())
		
		if metodo == "GET" and recurso == "/":
			texto = "<p><h2> Acortador de URLs</h2></p>"
			formulario = "<form method='POST' action=''><input type='text'" " name='url'> <input type='submit' ""value='Enviar'></form></body></html>"

			if len(self.URLs_introcucidas) == 0:
				contlistURLs = "<p>Todavia no hay ninguna URL acortada </p>"
				listURLs = ""
			else:
				contlistURLs = "<p>URLs introducidas ----------- URLs acortadas:</p>"
				listURLs = self.list_URLsAcort()
			global codigoHTTP
			global cuerpoHTML	
			codigoHTTP = "HTTP/1.1 200 OK"
			cuerpoHTML = "<html><body>" + texto + formulario + contlistURLs + listURLs + "</body></html>"
			
		elif metodo == "GET" and recurso == "/favicon.ico":
			return (NoEncontrado())
												
		elif metodo == "POST" and recurso == "/":

			texto = "<p><h2> Acortador de URLs</h2></p>"
			urlFormulario = cuerpo.split("=")[1]
			
			#Si no introducimos nada en el formulario
			if urlFormulario == "":
				codigoHTTP = "HTTP/1.1 400 Bad Request"
				cuerpoHTML = "<html><body>Error. Debes introducir una url." \
							   "</body></html>"
			#Si introducimos una URL en el formulario
			else:
				
				urlFormulario = urllib.parse.unquote(urlFormulario)
				#Si la URL introducida empieza por http o https
				if (urlFormulario.startswith('http://') or urlFormulario.startswith('https://')):
					print("La URL empieza por HTTP o HTTPS")
					
				#Si la URL introducida no empieza por http ni por https
				else:
					print("La URL no empieza por HTTP o HTTPS")
					#Añado http a la URL que he puesto en el formulario
					urlFormulario = "http://" + urlFormulario
					print("Se deberia añadir http a la url: "+ urlFormulario)

								
				try: #Si ya tenemos acortada la URL
					URL_acortada = self.URLs_acortadas[urlFormulario]
					URLExiste = "<p> Esa URL ya ha sido acortada</p>"
				#Si no esta acortada la URL    
				except KeyError: 
					if len(self.URLs_introcucidas) == 0:
						self.contador = 0
					else:
						self.contador = (len(self.URLs_introcucidas)-1) + 1

					URL_acortada = "http://localhost:4567/" + str(self.contador)

					# Añadimos la URL, actualizamos el diccionario
					self.URLs_introcucidas[URL_acortada] = urlFormulario
					self.URLs_acortadas[urlFormulario] = URL_acortada
					#Abrimos el fichero en modo escritura posicionándonos al final del archivo
					with open('fichero', 'a') as fichero:
						escribir = csv.writer(fichero)
						escribir.writerow([URL_acortada, urlFormulario])
					URLExiste = ""
			
				codigoHTTP = "HTTP/1.1 200 OK"
				cuerpoHTML = "<html><body>" + texto + "<p><h2>" + URLExiste + "</h2></p>" +"<p>URL: <a href=" + urlFormulario + ">" + urlFormulario + "</a> <br> URL acortada: <a href=" + URL_acortada + ">" + URL_acortada + "</a></p></body></html>"

		elif metodo == "GET" and len(recurso) > 1:
			# Si ya tenemos algo en el diccionario
			try:
				nrecurso = int(recurso[1:])
			#Si no insertamos un número 
			except ValueError:
				
				codigoHTTP = "HTTP/1.1 404 Not Found"
				cuerpoHTML = "<html><body><h1>Introduzca un numero</h1></body></html>"
				return (codigoHTTP, cuerpoHTML)

			URL_acortada = "http://localhost:4567" + recurso
			try:
				URL_introducida = self.URLs_introcucidas[URL_acortada]
			#Si el recurso que inserto no lo tenemos almacenado    
			except KeyError:
				codigoHTTP = "HTTP/1.1 404 Not Found"
				cuerpoHTML = "<html><body><h1>Recurso no disponible</h1></body></html>"
				return (codigoHTTP, cuerpoHTML)

			codigoHTTP = "HTTP/1.1 302 Redirect"
			cuerpoHTML = '<html><head><meta http-equiv="Refresh" content="3; url=' + URL_introducida + '"/></head' + '<body>Redirigiendo a ' + URL_introducida + ' .Espere.</b></body></html>'
						
		return (codigoHTTP, cuerpoHTML)

if __name__ == "__main__":
	testWebApp = acortadorURLs("localhost", 4567)
