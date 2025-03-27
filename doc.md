# Resolucion de ejercicios

### Resolucion ejercicio 1:

Para este ejercicio realice un script de bash que internamente llama a un archivo de python en donde se genera el compose.
Separe el codigo en distintas funciones dependiendo que parte queria generar (clientes, servidor, network). De esta forma a futuro era mas facil encontrar el codigo que debia modificar, de ser necesario.

### Resolucion ejercicio 2:
Para este ejercicio agregue un mount para evitar que se copie los archivos de configuracion cada vez que quiera correr el compose, y asi evitar que la imagen se tenga que construir nuevamente si cambia algo en la configuracion.
Ademas agregue un .dockignore para indicar que archivos queria ignorar por Docker.
Y por ultimo tuve que borrar algunas variables de entorno que estaban en el compose, ya que sino se tomaban esos valores de las variables de entorno y no de los archivos de configuracion. 

### Resolucion ejercicio 3:
Para este ejercicio realice un simple script en donde se corria una imagen de docker que contenia netcat ya instalado, por lo que no se debia instalar en la maquina de host para que funcione.
Inicialmente el nombre del servidor y del puerto no estaban simplemente hardcodeados en el codigo, sino que iba a buscarlo al archivo de configuracion del servidor. El problema fue que los tests en ese momento me fallaban y estuve un buen rato intentando descifrar que era lo que sucedia.
Finalmente me di cuenta que estaba definiendole un nombre incorrecto a la network en el docker compose, y que este era el problema por lo que mis tests no funcionaban.

### Resolucion ejercicio 4:
Para este ejercicio me fue mas facil en python que en go, ya que tenia mas experiencia en el primero.
Para esto en python utilice el modulo signal que permite atrapar una signal y ejecutar una funcion de tipo handler para esta. Al sevidor le tuve que agregar una lista de clientes activos para poder cerrarlos correctamente si recibia esta signal, ademas del socket del servidor.
En go lo realice de forma similar, con la funcion notify de os/signal y definiendo un handler. Y aca al tener un cliente unicamente tenia que cerrar su socket.

### Resolucion ejercicio 5:
Para este ejercicio primero agregue las variables de entorno necesarias para una apuesta en cada cliente.
Ademas, en el cliente tuve que modelar un Ticket, que representa a un ticket de una apuesta, en base a las variables de entorno definidas.
El protocolo que defini fue que un cliente enviara un ticket de apuesta con el siguiente formato: TICKET,agency,firstname,lastname,document,birthdate_number.
De esta forma, el servidor al recibir un mensaje que contiene TICKET inicialmente podria identificarlo facilmente, y leerlo hasta el \n.
Con este protocolo simple me permitio facilmente serializar y deserealizar el mensaje tanto en cliente como servidor

### Resolucion ejercicio 6:
Para este ejercicio mantuve de igual manera la forma de enviar un Ticket, pero ahora en vez de cortar en un \n se corta cuando el servidor recibe un mensaje con BATCH_DONE.
De esta forma un cliente envia por ejemplo TICKET,agency,firstname,lastname,document,birthdate_number\nTICKET,agency,firstname,lastname,document,birthdate_number\nBATCH_DONE. 
Asi el servidor empezara separando por los \n, por lo que nos quedaran dos tickets y BATCH_DONE. Como encontro un BATCH_DONE termina de leer, y luego para construir un Ticket verifica si contiene todos los campos necesarios y si no contiene BATCH_DONE.

### Resolucion ejercicio 7:
Para este ejercicio agregue que un cliente envie un ALL_BETS_DONE,agency una vez que envia todas sus apuestas y quiere conocer a los ganadores de su agencia. 
Para esto el servidor necesita guardarse un diccionario de agencia y socket asi luego puede contestar con los ganadores unicamente a la agencia que corresponda.
Ademas, para este ejercicio como el servidor debe inicialmente chequear el mensaje para ver si la agencia esta enviando tickets o si quiere conocer los ganadores, decidi que era mejor que el modulo de server.py se encargue de manipular los sockets (tanto para lectura como escritura). 
Por este motivo quite del modulo loteria las funciones que manipulaban los sockets y las movi al modulo server.

### Resolucion ejercicio 8:
Para este ejercicio introduje el modulo multiprocessing en python ya que es recomendado en python porque el global interpreter lock en python no permite que varios threads se ejecuten en paralelo. En cambio utilizando procesos diferentes, estos no comparten memoria y tampoco el global interpreter lock, por lo que si podemos tener paralelismo de verdad.
Para esto tuve que utilizar la clase Manager y asi poder compartir recursos entre diferentes procesos.
A su vez, tuve que pasar varios metodos a estaticos y agregar argumentos a esas funciones ya que utilizando self algunas cosas no se podrian serializar facilmente para pasarle del proceso padre a un proceso hijo.
