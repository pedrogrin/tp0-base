### Resolucion ejercicio 2:
Para este ejercicio agregue un mount para evitar que se copie los archivos de configuracion cada vez que quiera correr el compose, y asi evitar que la imagen se tenga que construir nuevamente si cambia algo en la configuracion.
Ademas agregue un .dockignore para indicar que archivos queria ignorar por Docker.
Y por ultimo tuve que borrar algunas variables de entorno que estaban en el compose, ya que sino se tomaban esos valores de las variables de entorno y no de los archivos de configuracion. 