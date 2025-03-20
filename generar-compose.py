import sys

def main(args):
    file, clients_size = validate_args(args)
    if file is None or clients_size is None:
        return
    
    compose_file_lines = ["name: tp0", "services:"]
    compose_file_lines += generate_server_lines()
    compose_file_lines += generate_client_lines(clients_size)
    compose_file_lines += generate_network_lines()

    with open(file, "w") as f:
        f.write("\n".join(compose_file_lines))
    
    
def validate_args(args):
    if len(args) != 3:
        print("Usage: generar-compose.py <output_file> <number_of_clients>")
        return None, None
    
    name = args[1]
    try:
        clients = int(args[2])
        if clients < 1:
            raise ValueError()
    except ValueError:
        print("The number of clients must be a positive integer")
        return None, None

    return name, clients

def generate_server_lines():
    return [
        "  server:",
        "    container_name: server",
        "    image: server:latest",
        "    entrypoint: python3 /main.py",
        "    environment:",
        "      - PYTHONUNBUFFERED=1",
        "    networks:",
        "      - testing_net",
        "    volumes:",
        "      - ./server/config.ini:/config.ini",
        ""
    ]

def generate_client_lines(clients_size):
    client_lines = []
    for i in range(clients_size):
        client_lines += [
            f"  client{i + 1}:",
            f"    container_name: client{i + 1}",
            "    image: client:latest",
            "    entrypoint: /client",
            "    environment:",
            f"      - CLI_ID={i + 1}",
            f"      - NOMBRE=Santiago Lionel",
            f"      - APELLIDO=Lorca",
            f"      - DOCUMENTO=30904465",
            f"      - NACIMIENTO=1999-03-17",
            f"      - NUMERO=7574",
            "    networks:",
            "      - testing_net",
            "    volumes:",
            "      - ./client/config.yaml:/config.yaml",
            f"      - ./data/agency{i + 1}.csv:/agency{i + 1}.csv",
            "    depends_on:",
            "      - server",
            ""
        ]
    return client_lines

def generate_network_lines():
    return [
        "networks:",
        "  testing_net:",
        "    ipam:",
        "      driver: default",
        ""
    ]
    

if __name__ == "__main__":
    main(sys.argv)