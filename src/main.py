"""
    Minecraft Server Status Checker (minecraft-server-status-checker)
    Description: Checks status of gived minecraft server, collects data about it, and gives it to special function where you can write your code or use some scenarios.
    Date: 2019
    Author: Kirill Zhosul (@kirillzhosul)
"""

# Impoting modules
from time import sleep  # Module for sleeping on time before next request.
from mcstatus import MinecraftServer  # MinecraftServer class for making requests to the server / working with query.
from plyer import notification  # Module for working with notification, you may not import this if you dont working with notifications.


def server_query(query):
    # Main function where you can write your own code that will executed when querying server or just default scenario.

    # Executing scenarios.
    for scenario in scenarios:
        scenario(query)

def default_scenario_print(query):
    # Default scenarios functions used to be added in to server_query / server_event as default log functions.
    # If there is some data in query.
    if query is not None:
        if server_detailed_data_is_enabled:
            # If there is enable-query: true in properities of the server.
            # Printing server host.
            print(f"Server host: {query.raw['hostip']}:{query.raw['hostport']}")
            # Printing server software.
            print(f"Server software: v{query.software.version} {query.software.brand}")
            # Printing server plugins.
            print(f"Server plugins: {query.software.plugins}")
            # Printing server MOTD.
            print(f"Server MOTD: \"{query.motd}\"")
            # printing server players.
            print(f"Server players: {query.players.online}/{query.players.max} {query.players.names}")
        else:
            # If there is enable-query: false in properities of the server
            # Getting players list from the server or "No player online" if there no players.
            players_list = [f"{player.name} ({player.id})" for player in query.players.sample] if query.players.sample is not None else "No players online"
            # Printing server version.
            print(f"Server version: {query.version.name} (protocol {query.version.protocol})")
            # Printing server description
            print(f"Server description: \"{query.description}\"")
            # Printing server players
            print(f"Server players: {query.players.max}/{query.players.online} {players_list}")
        # Printing line separator.
        print("--- --- ----")


def default_scenario_notification(query):
    # Default scenario used to show notification when server changes state.
    if server_previous_query is None and query is not None:
        # If previosly there no data, but now there data.
        # Show notification that server went offline.
        notification.notify(
            title="Minecraft Server Status Checker",
            message="Server with name " + server_connect_address + " are went online!",
            app_icon=None,
            timeout=100
        )
    if server_previous_query is not None and query is None:
        # If previosly there was data, but now there no data.
        # Show notification that server went offline.
        notification.notify(
            title="Minecraft Server Status Checker",
            message="Server with name " + server_connect_address + " are went offline!",
            app_icon=None,
            timeout=100
        )


def get_user_input():
    # Get user input function to get input from user.
    while True:
        # While user dont enters input.

        # Asking for the input.
        print("[Input]: ", end="")
        user_input = input()

        # If user enters not empty string - exiting function with return, if not - repeat asking of the input.
        if len(user_input) > 0:
            return user_input

def send_query():
    # Main program function that is used to query minecraft server and execute server_event / server_query functions

    # Global variables.
    global server_detailed_data_is_enabled
    global server_previous_query

    # Variables.
    server_response = None  # Server responce variable, by default is None.

    # Trying to query the server.
    if server_detailed_data_is_enabled:
        try:
            # Trying to make query request.
            server_response = server_connection.query()
        except:
            # If there error in query request, it means query are disabled on gived server.
            # Turning off later asking of the query request.
            server_detailed_data_is_enabled = False

            # Printing information.
            print("Server are disabled query request, so detailed data was disabled.")

            # Checking status of the server.
            try:
                server_response = server_connection.status()
            except:
                server_response =  None
    else:
        # Checking server status.
        try:
            server_response = server_connection.status()
        except:
            server_response =  None
        
    # Executing server_query / server_event functions.
    server_query(server_response)

    # Adding query data to server_previous_query.
    server_previous_query = server_response

def query_loop():
    # Main query loop code.

    while True:
        # Infinity loop ffor sending query.
        try:
            # Sending query.
            send_query()
        except KeyboardInterrupt:
            # Breaking on keyboard interrupt.
            break
        except:
            # If there error, continue
            continue
        # Sleeping for gived amount of the time.
        sleep(server_query_interval)

def get_settings_from_user():
    # Function that returns tuple with all settings from the user input.

    # Welcome message.
    print("[Console]: Welcome to the Minecraft Server Status Checker!")

    # Getting server address from user
    print("[Console]: Please enter IP adress of the server:")
    server_connect_address = get_user_input()
    print(f"[Console]: Server adress is set to {server_connect_address}!")

    # Getting query interval from user
    print("[Console]: Please enter query interval in seconds:")
    try:
        server_query_interval = int(get_user_input())
    except ValueError:
        server_query_interval = 1
    finally:
        print(f"[Console]: Query interval is set to {str(server_query_interval)}s!")

    # Getting query interval from user
    print("[Console]: Do program need to use query?(YES for yes):")
    server_detailed_data_is_enabled = (get_user_input() == "YES")
    print(f"[Console]: Query is set to {server_detailed_data_is_enabled}!")

    # Printing some important information.
    if server_detailed_data_is_enabled:
        print("!!!You enabled query, you may need to wait some time!")

    # If interval bigger than 4294967, so setting interval to 4294967 to not get OverflowError.
    if server_query_interval > 4294967:
        server_query_interval = 4294967

    # Returning.
    return server_connect_address, server_query_interval, server_detailed_data_is_enabled

if __name__ == "__main__":
    # Entry point.

    # Variables.
    server_previous_query = None # Previous query data to be compared in next calculation.

    # Getting settings.
    server_connect_address, server_query_interval, server_detailed_data_is_enabled = get_settings_from_user()

    # Scenarios
    scenarios = [default_scenario_notification, default_scenario_print]

    # Creating server connection.
    server_connection = MinecraftServer.lookup(server_connect_address)

    # Starting query loop.
    query_loop()