### Resolucion ejercicio 5:
Para este ejercicio primero agregue las variables de entorno necesarias para una apuesta en cada cliente.
Ademas, en el cliente tuve que modelar un Ticket, que representa a un ticket de una apuesta, en base a las variables de entorno definidas.
El protocolo que defini fue que un cliente enviara un ticket de apuesta con el siguiente formato: TICKET,agency,firstname,lastname,document,birthdate_number.
De esta forma, el servidor al recibir un mensaje que contiene TICKET inicialmente podria identificarlo facilmente, y leerlo hasta el \n.
Con este protocolo simple me permitio facilmente serializar y deserealizar el mensaje tanto en cliente como servidor