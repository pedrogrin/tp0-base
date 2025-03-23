### Resolucion ejercicio 4:
Para este ejercicio me fue mas facil en python que en go, ya que tenia mas experiencia en el primero.
Para esto en python utilice el modulo signal que permite atrapar una signal y ejecutar una funcion de tipo handler para esta. Al sevidor le tuve que agregar una lista de clientes activos para poder cerrarlos correctamente si recibia esta signal, ademas del socket del servidor.
En go lo realice de forma similar, con la funcion notify de os/signal y definiendo un handler. Y aca al tener un cliente unicamente tenia que cerrar su socket.