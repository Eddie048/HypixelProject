import subprocess
import pyautogui
import time
import os
import image_reader
import player
from threading import Thread
import requests

# Ignore these usernames, anyone who is in your party should be in this list
# TODO: Move this to a file
ignored_usernames = ["dragon0484", "krimsonpig", "cool_muns", "emimango", "origamimaster22"]

# the 4 rank colors, all of which may appear in tab
acceptable_colors = [(255, 170, 0, 255), (85, 255, 255, 255), (85, 255, 85, 255), (170, 170, 170, 255)]

# keeps track of the state of the thread
thread_state = False

# width of the screen
SCREEN_WIDTH = pyautogui.size()[0]

# boolean, describes whether the computer uses a retina display
# some behavior surrounding screenshots and searching on the screen changes if using a retina display
RETINA_DISPLAY = (subprocess.call("system_profiler SPDisplaysDataType | grep -i 'retina'", shell=True) == 0)


# returns a screenshot with the specified number of players, up to 14
def get_screenshot():
    # searches for part of the ping icon as a reference
    location = pyautogui.locateOnScreen("Marker.png")

    # if the location was not found, exit the function and display an error message
    if location is None:
        return "None"

    # if this is a retina display, the coordinates will be twice what they should be
    if RETINA_DISPLAY:
        location = (location[0]/2 - 1, location[1]/2)

    # finds the leftmost part of the usernames, including removing the player head icons
    left = SCREEN_WIDTH - (location[0] + 8) + 27

    # the exact maximum width of the usernames, including removing the player head and ping icons
    width = ((location[0] + 8) - (SCREEN_WIDTH / 2)) * 2 - (27 + 36)

    # take screenshot of the players
    if RETINA_DISPLAY:
        return pyautogui.screenshot(region=(left*2, 120, width*2, 54 * 16))
    else:
        return pyautogui.screenshot(region=(left, 60, width, 27 * 16))


# takes in an image, returns a list of the lines of text in the image
def get_text_from_image(img):
    # default scale factor, number of pixels per minecraft pixel
    scale_factor = 3

    # if retina display, screenshot size and therefore pixel size is doubled
    if RETINA_DISPLAY:
        scale_factor = 6

    ign_return_list = []

    # repeats 16 times as that is the maximum number of players in a lobby
    for x in range(16):
        temp_img = img.crop(box=(0, 9 * scale_factor * x, img.width, 9 * scale_factor * (x + 1) - scale_factor))

        arr = []

        for i in range(int(temp_img.width / scale_factor)):
            arr.append([])
            for k in range(int(temp_img.height / scale_factor)):
                # plus ones move to the center roughly
                px = temp_img.getpixel(xy=(i * scale_factor + 1, k * scale_factor + 1))

                # if the given pixel is one of these colors, it is part of a character
                if acceptable_colors.__contains__(px):
                    arr[i].append(1)
                else:
                    arr[i].append(0)

        # strings of length 0 aren't usernames
        temp_ign = image_reader.read_string(arr)
        if len(temp_ign) > 0:
            ign_return_list.append(temp_ign)

    return ign_return_list


# display desktop notification with given title and text
def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


# takes in a list of usernames (IGNs), gives notifications and prints a threat analysis
def do_threat_analysis(ign_list, key):

    # initialize lists of types of players
    nicks = []
    threats = []
    sweats = []
    result = ""
    for ign in ign_list:
        # ignore usernames in ignored list
        if ignored_usernames.__contains__(ign.lower()):
            continue

        threat_anal = player.get_player(ign, key)
        if threat_anal == ["", ""] or threat_anal is None:
            continue
        elif threat_anal == "Nick":
            nicks.append(ign)
        else:
            result += threat_anal[0] + "\n" + threat_anal[1] + "\n"
            threats.append(ign)

            if threat_anal[1] != "":
                sweats.append(ign)

    notification = ""
    print(ign_list)

    # TODO: save list of usernames

    if len(nicks) > 0:
        print(f"Nicks: {str(len(nicks))}")
        notification += "Nicks: " + str(len(nicks)) + " "
        print(nicks)
    if len(threats) > 0:
        print(f"Threats: {str(len(threats))}")
        notification += "Threats: " + str(len(threats)) + " "
        print(threats)

    if len(sweats) > 0:
        print(f"Sweats: {str(len(sweats))}")
        notification += "Sweats: " + str(len(sweats))
        print(sweats)
    print(result)

    if len(notification) == 0:
        notify("Done!", "No threats here")
    else:
        notify("Done!", notification)


# temporary function, to be replaced with code below once working
def check_for_file():
    pass
# # automatic system, constantly checks for new screenshots in the screenshot folder
# def check_for_file():
#
#     # location of screenshots
#     path = "/Users/edwardstump/Library/Application Support/minecraft/screenshots"
#     saved_set = set()
#
#     # initialize the saved set of all screenshot files
#     for file in os.listdir(path):
#         fullpath = os.path.join(path, file)
#         if os.path.isfile(fullpath):
#             saved_set.add(file)

    # while thread_state:
    #     time.sleep(0.2)
    #     temp_set = set()
    #
    #     for file in os.listdir(path):
    #         fullpath = os.path.join(path, file)
    #         if os.path.isfile(fullpath):
    #             temp_set.add(file)
    #
    #
    #     if len(list_names) < len(temp):
    #         file = list((set(temp) - set(list_names)))[0]
    #         print(file)
    #       temp_image = Image.open("/Users/edwardstump/Library/Application Support/minecraft/screenshots/" + file, "r")
    #         ign_list = get_text_from_image(temp_image, 16)
    #         do_threat_analysis(ign_list)
    #         list_names = temp


def main():
    print("API Key required!\nUse command '/api new' in hypixel to get an API key.")
    key = str(input("Enter Key: "))

    while str(requests.get("https://api.hypixel.net/key?key=" + key)) != "<Response [200]>":
        print("That is not a valid key.")
        key = str(input("Enter Key: "))

    # confirmation message
    print("Key Confirmed\n")

    user_input = ""

    # main loop for input
    while user_input != 0:
        # border to easily see new commands
        print("=============================================\n")
        print("Main Menu:\n0: Exit program\n1: Settings\n2: Run once\n3: Toggle Automatic\nIGN: Analyze IGN\n")
        user_input = str(input("Enter Number or IGN to look up: "))

        if user_input == "0":
            exit()
        elif user_input == "1":
            # variable for input for settings menu
            settings_input = ""

            # loop for using settings menu
            while settings_input != "0":
                # border to easily see settings differences
                print("=============================================\n")
                print("Settings:\n0: Exit to main menu\n1: How to use?\n2: API Key\n3: Ignored IGNs\n4: Time delay")
                print("5: Save usernames - [whether this is true or false]\n")
                settings_input = input("Enter a menu item: ")

                if settings_input == "0":
                    pass
                elif settings_input == "1":
                    print("Here is how to use this program:")
                    # TODO: Add explanation
                    print("Settings explanations")
                    # TODO: Add settings explanations
                elif settings_input == "2":
                    print("Change API Key Here")
                elif settings_input == "3":
                    print("Change ignored IGN list here")
                elif settings_input == "4":
                    print("Change time delay here")
                elif settings_input == "5":
                    print("Toggle saving usernames")
                else:
                    print("Input not recognized")

        elif user_input == "2":
            # delay for user to switch tabs or whatever
            time.sleep(2)
    
            # take screenshot of tab menu
            tab_screenshot = get_screenshot()
            if tab_screenshot == "None":
                print("Error: Reference Not Found")
                notify("Error", "Reference not found")
                continue

            ign_list = get_text_from_image(tab_screenshot)
            do_threat_analysis(ign_list, key)
        elif user_input == "3":
            # this is currently not working
            print("This functionality is currently not working.")

            # global thread_state
            # if thread_state:
            #     thread_state = False
            #     print("Automatic detection turned off.")
            # else:
            #     thread_state = True
            #     file_finder = Thread(target=check_for_file)
            #     file_finder.start()
            #     print("Automatic detection turned on.")
        else:
            temp_result = player.get_player(user_input, key)

            if temp_result is None or temp_result == "Nick":
                print("Player not found or input not recognized.\n")
            elif temp_result == ["", ""]:
                print("This player is not a threat.")
            else:
                print(f"{temp_result[0]}\n{temp_result[1]}")
            continue


if __name__ == "__main__":
    main()
