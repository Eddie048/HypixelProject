import requests

# API Key from hypixel, use command '/api' or '/api new' in hypixel
# TODO: do this better, maybe have the user enter it?
API_KEY = "bf3a9ff4-aa5c-4fc5-8aef-34f9146eff30"

# gamemodes to check for in JSON file
gamemodes = ["four_four_", "eight_two_", "eight_one_", "four_three_"]

# bridging types in JSON file
bridge_types = {"bridging_distance_30:elevation_NONE:angle_STRAIGHT:" : 9500,
                "bridging_distance_30:elevation_NONE:angle_DIAGONAL:" : 8500,
                "bridging_distance_30:elevation_SLIGHT:angle_STRAIGHT:" : 13000,
                "bridging_distance_30:elevation_SLIGHT:angle_DIAGONAL:" : 12000,
                "bridging_distance_30:elevation_STAIRCASE:angle_STRAIGHT:" : 17000,
                "bridging_distance_30:elevation_STAIRCASE:angle_DIAGONAL:" : 20000}

# store the data value
data = None

# store the threat analysis
threat = ["", ""]

def get_stat(index, source = ""):
    global data
    if source == "":
        source = data

    try:
        zoom = source
        for item in index:
            zoom = zoom[item]

        return zoom
    except KeyError:
        return -1

def update_threat(stat_num, threat_criteria, sweat_criteria, stat_string):
    global threat

    if stat_num > sweat_criteria:
        threat[1] += stat_string + ": " + str(stat_num) + " - "
    elif stat_num > threat_criteria:
        threat[0] += ", " + stat_string + ": " + str(stat_num)


# takes in a player's ign and returns data about them
def get_player(player_name):
    global data
    data = requests.get(
        url="https://api.hypixel.net/player",
        params={
            "key": API_KEY,
            "name": player_name
        }
    ).json()

    # reset threat
    global threat
    threat = ["", ""]

    if data is None:
        return
    if not data["success"]:
        return
    if data['player'] == "None" or data['player'] is None:
        return "Nick"

    bedwars_stats = get_stat(["player", "stats", "Bedwars"])
    if bedwars_stats == -1:
        return ["", ""]

    update_threat(get_stat(["winstreak"], bedwars_stats), 5, 20, "Winstreak")
    finals = get_stat(["final_kills_bedwars"], bedwars_stats)
    update_threat(finals, 1500, 10000, "Finals")
    update_threat(get_stat(["beds_broken_bedwars"], bedwars_stats), 1000, 10000, "Beds")
    update_threat(round(finals/get_stat(["final_deaths_bedwars"], bedwars_stats), 1), 2, 10, "FKDR")


    max_winstreak = 0
    for mode in gamemodes:
        max_winstreak = max(max_winstreak, get_stat([mode + "winstreak"], bedwars_stats))

    update_threat(max_winstreak, 5, 20, "Max Winstreak")
    max_fkdr = 0
    for mode in gamemodes:
        max_winstreak = max(max_winstreak, get_stat([mode + "final_kills_bedwars"], bedwars_stats),
                                get_stat([mode + "final_deaths_bedwars"], bedwars_stats))

    update_threat(max_fkdr, 2, 10, "Max FKDR")

    bridge_rating = 0
    for type in bridge_types.keys():
        time = get_stat(["practice", "records", type], bedwars_stats)
        if time == -1:
            continue
        elif time < bridge_types.get(type):
            bridge_rating += 1

    if bridge_rating > 0:
        threat[0] += ", Bridge Rating: " + str(bridge_rating)

    if len(threat[0]) > 1 or len(threat[1]) > 1:
        threat[0] = data["player"]["displayname"] + threat[0]

    return threat
