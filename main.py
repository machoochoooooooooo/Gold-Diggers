import math
import random
import sys
import pygame


# Initialize Pygame
pygame.init()


# --- WINDOW SETUP ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GOLD DIGGERS")
clock = pygame.time.Clock()


# --- COLORS ---
DARK_BLUE = (11, 24, 44)
LIGHT_BLUE = (52, 152, 219)
GOLD = (244, 180, 26)
WHITE = (255, 255, 255)
SHADOW_COLOR = (40, 40, 40)
GRAY = (100, 110, 120)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
SAND = (240, 210, 160)
ORANGE = (230, 126, 34)
WOOD_BROWN = (139, 69, 19)
PURPLE = (155, 89, 182)


# --- FONTS ---
font_title = pygame.font.SysFont("impact", 72)
font_subtitle = pygame.font.SysFont("impact", 40)
font_button = pygame.font.SysFont("couriernew", 16, bold=True)
font_ui = pygame.font.SysFont("couriernew", 16, bold=True)
font_event = pygame.font.SysFont("couriernew", 18, bold=True)


# --- PRE-RENDER MENU TEXT ---
title_text = "GOLD DIGGERS"
title_shadow = font_title.render(title_text, True, SHADOW_COLOR)
title_main = font_title.render(title_text, True, GOLD)
title_x = SCREEN_WIDTH // 2 - title_main.get_width() // 2
title_base_y = SCREEN_HEIGHT // 2 - 120


# --- GAME STATES ---
globals()['current_state'] = "MENU"
current_event_type = "ISLAND"  


# --- GAMEPLAY VARIABLES ---
player_gold = 500
player_manpower = 10
player_cargo = 0        
max_cargo_capacity = 10
player_armor = 5
player_speed = 5


current_day = 1
prompts_faced_today = 0
game_over_reason = "SPEED"


# --- PORT VARIATION VARIABLES ---
current_port_cargo_price = 100
current_port_sail_price = 225
current_port_hold_price = 180
current_port_crew_price = 75


# --- SCALING ENEMY DIFFICULTY ---
pirate_difficulty_modifier = 0.0  


# --- ERROR & RESOLUTION TRACKING ---
error_message_timer = 0
show_error_message = False
error_text_string = "ERROR: NOT ENOUGH GOLD!"
trap_gold_lost = 0
resolution_text_lines = []
screenshake_timer = 0
island_explore_gold = 0
island_explore_crew = 0
island_explore_start_crew = 0
island_explore_timer = 0
ISLAND_EXPLORE_TICK_MS = 1000


# --- HIGHSCORE TRACKING ---
max_days_survived = 1
max_gold_claimed = 500
current_tax_amount = 100


PROMPT_INTERVAL = 10000  
sailing_timer = 0        
last_time_check = pygame.time.get_ticks()


# --- FLOATING CRATES SYSTEM ---
crates_list = []
crate_reward_popups = []
CRATE_SPAWN_CHANCE = 0.002


class FloatingCrate:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = -self.width - 10
        self.y = random.randint(100, SCREEN_HEIGHT - 100)
        self.speed = random.uniform(1.5, 3.0)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def update(self):
        self.x += self.speed
        self.rect.x = self.x


    def draw(self, surface):
        pygame.draw.rect(surface, SHADOW_COLOR, (self.rect.x + 2, self.rect.y + 2, self.width, self.height))
        pygame.draw.rect(surface, WOOD_BROWN, self.rect)
        pygame.draw.rect(surface, GOLD, self.rect, 2)
        pygame.draw.line(surface, GOLD, (self.rect.x, self.rect.y), (self.rect.x + self.width, self.rect.y + self.height), 2)




# --- ASSETS (BACKGROUND GENERATORS) ---
BEACH_IMAGE_ID = "testbeach.jpg"
OCEAN_IMAGE_ID = "ocean.png"  
BG_BUFFER = 40


try:
    background_img = pygame.image.load(BEACH_IMAGE_ID).convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH + BG_BUFFER, SCREEN_HEIGHT + BG_BUFFER))
except (pygame.error, FileNotFoundError):
    background_img = pygame.Surface((SCREEN_WIDTH + BG_BUFFER, SCREEN_HEIGHT + BG_BUFFER))
    background_img.fill(LIGHT_BLUE)
    pygame.draw.rect(background_img, SAND, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH + BG_BUFFER, 150))


try:
    gameplay_ocean_img = pygame.image.load(OCEAN_IMAGE_ID).convert()
    gameplay_ocean_img = pygame.transform.scale(gameplay_ocean_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except (pygame.error, FileNotFoundError):
    gameplay_ocean_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    gameplay_ocean_img.fill((41, 128, 185))
    for i in range(0, SCREEN_WIDTH, 40):
        for j in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.arc(gameplay_ocean_img, LIGHT_BLUE, (i, j, 20, 10), 0, math.pi, 2)


# --- SHIP CATALOG DATA ---
SHIPS = [
    {
        "name": "THE SWIFT SLOOP",
        "desc": "Light, agile, and incredibly fast. Ideal for solo smugglers.",
        "speed": 9, "armor": 3, "cargo": 4,
        "starting_crew": 5, "prompt_interval": 10000,
        "img_path": "ship_sloop.png"
    },
    {
        "name": "GOLDEN BRIGANTINE",
        "desc": "A balanced hunter-gatherer vessel. Sturdy and reliable.",
        "speed": 7,
        "armor": 6, "cargo": 6,
        "starting_crew": 15, "prompt_interval": 15000,
        "img_path": "ship_brig.png"
    },
    {
        "name": "DREAD GALLEON",
        "desc": "A floating fortress. Massive cargo space, but moves like a brick.",
        "speed": 3, "armor": 10, "cargo": 10,
        "starting_crew": 30, "prompt_interval": 18000,
        "img_path": "ship_galleon.png"
    },
]


for ship in SHIPS:
    try:
        loaded_img = pygame.image.load(ship["img_path"])
        scaled_img = pygame.transform.scale(loaded_img, (260, 182))
        ship["surface"] = scaled_img.convert_alpha()
        bg_color = ship["surface"].get_at((0, 0))
        ship["surface"].set_colorkey(bg_color)
        ship["has_img"] = True
    except (pygame.error, FileNotFoundError):
        ship["has_img"] = False


current_ship_index = 0
player_ship_surface = None
player_ship_has_img = False




# --- BUTTON CLASS ---
class PixelButton:
    def __init__(self, text, x, y, width, height, base_color, hover_color, text_color=DARK_BLUE):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color
        self.text_color = text_color
        self.disabled = False
        self.update_text(text)


    def update_text(self, new_text):
        self.text = new_text
        self.text_surf = font_button.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)


    def draw(self, surface):
        pygame.draw.rect(surface, SHADOW_COLOR, (self.rect.x + 4, self.rect.y + 4, *self.rect.size))
       
        if self.disabled:
            pygame.draw.rect(surface, (70, 75, 85), self.rect)
            disabled_text = font_button.render(self.text, True, GRAY)
            surface.blit(disabled_text, self.text_rect)
        else:
            pygame.draw.rect(surface, self.current_color, self.rect)
            surface.blit(self.text_surf, self.text_rect)


    def check_hover(self, mouse_pos):
        if self.disabled:
            return False
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.base_color
            return False




# --- INITIALIZE UI BUTTONS ---
play_button = PixelButton("PLAY", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60, GOLD, WHITE)
prev_button = PixelButton("<", 50, SCREEN_HEIGHT // 2 - 30, 60, 60, GOLD, WHITE)
next_button = PixelButton((">"), SCREEN_WIDTH - 110, SCREEN_HEIGHT // 2 - 30, 60, 60, GOLD, WHITE)
select_button = PixelButton("CHOOSE SHIP", SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT - 90, 250, 50, GOLD, WHITE)
back_button = PixelButton("BACK", 30, 30, 100, 45, GOLD, WHITE)


# --- DYNAMIC EVENT BUTTON CONFIGS ---
event_btn_w = 440
event_btn_h = 42
event_center_x = SCREEN_WIDTH // 2 - (event_btn_w // 2)


# Grid layout buttons
btn_option_1 = PixelButton("OPTION 1", event_center_x, 340, event_btn_w, event_btn_h, GOLD, WHITE)
btn_option_2 = PixelButton("OPTION 2", event_center_x, 390, event_btn_w, event_btn_h, GOLD, WHITE)
btn_option_3 = PixelButton("OPTION 3", event_center_x, 440, event_btn_w, event_btn_h, GOLD, WHITE)
btn_option_4 = PixelButton("OPTION 4", event_center_x, 490, event_btn_w, event_btn_h, GOLD, WHITE)
btn_option_5 = PixelButton("OPTION 5", event_center_x, 540, event_btn_w, event_btn_h, GOLD, WHITE)


pay_tax_btn = PixelButton("PAY TAX & REST", SCREEN_WIDTH // 2 - 160, 430, 320, 55, RED, WHITE, text_color=WHITE)
restart_btn = PixelButton("RETURN TO MAIN MENU", SCREEN_WIDTH // 2 - 140, 480, 280, 55, GOLD, WHITE)




# --- HELPER DRAWING FUNCTIONS ---
def draw_stat_bar(surface, x, y, label, value, max_value=10):
    lbl_surf = font_ui.render(label, True, DARK_BLUE)
    surface.blit(lbl_surf, (x, y))
    bar_x = x + 100
    bar_width = 200
    bar_height = 20
    pygame.draw.rect(surface, SHADOW_COLOR, (bar_x, y + 2, bar_width, bar_height))
    fill_ratio = min(1.0, value / max_value)
    fill_width = int(fill_ratio * bar_width)
    pygame.draw.rect(surface, GREEN, (bar_x, y + 2, fill_width, bar_height))


def draw_top_bar(surface):
    stats_bg = pygame.Rect(0, 0, SCREEN_WIDTH, 45)
    pygame.draw.rect(surface, DARK_BLUE, stats_bg)
    pygame.draw.line(surface, GOLD, (0, 45), (SCREEN_WIDTH, 45), 3)
   
    day_lbl = font_ui.render(f"DAY: {current_day}", True, GOLD)
    gold_lbl = font_ui.render(f"GOLD: {player_gold}g", True, WHITE)
    crew_lbl = font_ui.render(f"CREW: {player_manpower}", True, GREEN)
    cargo_lbl = font_ui.render(f"CARGO: {player_cargo}/{max_cargo_capacity}", True, ORANGE)
    speed_lbl = font_ui.render(f"SPD: {player_speed}/30", True, LIGHT_BLUE)
   
    surface.blit(day_lbl, (15, 14))
    surface.blit(gold_lbl, (140, 14))
    surface.blit(crew_lbl, (310, 14))
    surface.blit(cargo_lbl, (480, 14))
    surface.blit(speed_lbl, (670, 14))




def wrap_text(text, font, max_width):
    if not text:
        return []


    lines = []
    for paragraph in str(text).splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue


        words = paragraph.split()
        current = []
        current_width = 0


        for word in words:
            test_text = (" ".join(current + [word])) if current else word
            test_width = font.size(test_text)[0]


            if current and test_width > max_width:
                lines.append(" ".join(current))
                current = [word]
                current_width = font.size(word)[0]
            else:
                current.append(word)
                current_width = test_width


        if current:
            lines.append(" ".join(current))


    return lines




def draw_wrapped_line(surface, font, color, text, center_x, y):
    if not text:
        return y


    rendered = font.render(text, True, color)
    surface.blit(rendered, (center_x - rendered.get_width() // 2, y))
    return y + font.get_linesize()




def draw_island_boarding_scene(surface, y_offset=0):
    return


def draw_reward_popups(surface):
    for index, popup in enumerate(crate_reward_popups):
        draw_y = SCREEN_HEIGHT - 36 - (index * 28)
        shadow = font_event.render(popup["text"], True, SHADOW_COLOR)
        text_surf = font_event.render(popup["text"], True, GOLD)
        surface.blit(shadow, (popup["x"] + 2, draw_y + 2))
        surface.blit(text_surf, (popup["x"], draw_y))





def setup_event_ui(event_type):
    global current_port_cargo_price, current_port_sail_price, current_port_hold_price, current_port_crew_price
   
    btn_option_1.disabled = False
    btn_option_2.disabled = False
    btn_option_3.disabled = False
    btn_option_4.disabled = False
    btn_option_5.disabled = False


    btn_option_1.rect.y = 300
    btn_option_2.rect.y = 350
    btn_option_3.rect.y = 400
    btn_option_4.rect.y = 450
    btn_option_5.rect.y = 500
    btn_option_1.update_text("")
    btn_option_2.update_text("")
    btn_option_3.update_text("")
    btn_option_4.update_text("")
    btn_option_5.update_text("")


    if event_type == "ISLAND":
        btn_option_1.update_text("EXPLORE THE ISLAND")
        btn_option_2.update_text("LEAVE THE ISLAND")
        btn_option_3.update_text("GO FISHING")
        btn_option_4.update_text("")
        btn_option_4.disabled = True
    elif event_type == "ISLAND_EXPLORE":
        btn_option_1.rect.y = 500
        btn_option_1.update_text("LEAVE ISLAND")
        btn_option_2.update_text("")
        btn_option_3.update_text("")
        btn_option_4.update_text("")
        btn_option_5.update_text("")
        btn_option_2.disabled = True
        btn_option_3.disabled = True
        btn_option_4.disabled = True
        btn_option_5.disabled = True
    elif event_type == "ISLAND_RESOLUTION":
        btn_option_1.update_text("CONTINUE VOYAGE")
        btn_option_2.update_text("")
        btn_option_3.update_text("")
        btn_option_2.disabled = True
        btn_option_3.disabled = True
    elif event_type == "ENEMY":
        required_crew = 18 + int(pirate_difficulty_modifier * 2)
        btn_option_1.update_text(f"FIRE CANNONS! (REQ. {required_crew} CREW)")
        btn_option_2.update_text("EVADE & FLEE (SPEED CHECK)")
        btn_option_3.update_text("SURRENDER 1 CARGO TO PASS")
           
    elif event_type == "PORT":
        # Generate new localized prices every time a port loads
        current_port_cargo_price = random.randint(85, 115)   # Base 100
        current_port_sail_price = random.randint(210, 245)   # Base 225
        current_port_hold_price = random.randint(165, 195)   # Base 180
        current_port_crew_price = random.randint(70, 85)     # Base 75
       
        btn_option_1.update_text(f"SELL ALL CARGO [{current_port_cargo_price}G EACH]")
        btn_option_2.update_text(f"UPGRADE SAILS (+1 SPEED) [-{current_port_sail_price}G]")
        btn_option_3.update_text(f"EXPAND HOLD (+2 CAP) [-{current_port_hold_price}G]")
        btn_option_4.update_text(f"RECRUIT HANDS (+3 CREW) [-{current_port_crew_price}G]")
        btn_option_5.update_text("DEPART DOCKS & CONTINUE VOYAGE")
       
        if player_cargo == 0:
            btn_option_1.disabled = True
        if player_gold < current_port_sail_price:
            btn_option_2.disabled = True
        if player_gold < current_port_hold_price:
            btn_option_3.disabled = True
        if player_gold < current_port_crew_price:
            btn_option_4.disabled = True
           
    elif event_type in ["SQUID_TRAP", "BATTLE_RESOLUTION", "ROGUE_WAVE", "KRAKEN"]:
        btn_option_1.update_text("CONTINUE VOYAGE")




# --- MAIN LOOP ---
title_bob_timer = 0
bg_wave_timer = 0
sea_scroll_x = 0
shake_x = 0
shake_y = 0
last_time_check = pygame.time.get_ticks()


while True:
    current_ticks = pygame.time.get_ticks()
    delta_time = current_ticks - last_time_check
    last_time_check = current_ticks
   
    mouse_pos = pygame.mouse.get_pos()


    if show_error_message:
        error_message_timer -= delta_time
        if error_message_timer <= 0:
            show_error_message = False


    for popup in crate_reward_popups[:]:
        popup["timer"] -= delta_time
        if popup["timer"] <= 0:
            crate_reward_popups.remove(popup)


    if screenshake_timer > 0:
        screenshake_timer -= delta_time
        shake_x = random.randint(-4, 4)
        shake_y = random.randint(-4, 4)
    else:
        shake_x = 0
        shake_y = 0


    # --- 1. EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if globals()['current_state'] == "MENU":
                if play_button.check_hover(mouse_pos):
                    globals()['current_state'] = "CUSTOMIZATION"


            elif globals()['current_state'] == "CUSTOMIZATION":
                if prev_button.check_hover(mouse_pos):
                    current_ship_index = (current_ship_index - 1) % len(SHIPS)
                elif next_button.check_hover(mouse_pos):
                    current_ship_index = (current_ship_index + 1) % len(SHIPS)
                elif back_button.check_hover(mouse_pos):
                    globals()['current_state'] = "MENU"
                elif select_button.check_hover(mouse_pos):
                    chosen_ship = SHIPS[current_ship_index]
                    player_ship_has_img = chosen_ship["has_img"]
                    if player_ship_has_img:
                        player_ship_surface = chosen_ship["surface"]
                   
                    max_cargo_capacity = chosen_ship["cargo"]
                    player_manpower = chosen_ship["starting_crew"]  
                    player_armor = chosen_ship["armor"]
                    player_speed = chosen_ship["speed"]
                    PROMPT_INTERVAL = chosen_ship["prompt_interval"]  
                   
                    sailing_timer = 0
                    current_day = 1
                    pirate_difficulty_modifier = 0.0
                    prompts_faced_today = 0
                    player_gold = 500
                    player_cargo = 0
                    current_tax_amount = 100
                    crates_list.clear()
                    show_error_message = False
                   
                    globals()['current_state'] = "PLAYING"


            elif globals()['current_state'] == "PLAYING":
                for crate in crates_list[:]:
                    if crate.rect.collidepoint(mouse_pos):
                        if random.random() < 0.15:
                            trap_gold_lost = int(player_gold * 0.05)
                            player_gold = max(0, player_gold - trap_gold_lost)
                            current_event_type = "SQUID_TRAP"
                            setup_event_ui(current_event_type)
                            globals()['current_state'] = "EVENT_PROMPT"
                        else:
                            added_gold = random.randint(10, 30)
                            player_gold += added_gold
                            crate_reward_popups.append({
                                "text": f"+{added_gold} GOLD",
                                "timer": 2200,
                                "x": 18,
                            })


                            crates_list.remove(crate)
                            break


            elif globals()['current_state'] == "EVENT_PROMPT":
                action_taken = False
               
                if current_event_type == "ISLAND":
                    if btn_option_1.check_hover(mouse_pos):
                        globals()['island_explore_gold'] = 0
                        globals()['island_explore_crew'] = player_manpower
                        globals()['island_explore_start_crew'] = player_manpower
                        globals()['island_explore_timer'] = 0
                        current_event_type = "ISLAND_EXPLORE"
                        setup_event_ui(current_event_type)
                        globals()['current_state'] = "ISLAND_EXPLORE"
                    elif btn_option_2.check_hover(mouse_pos):
                        resolution_text_lines = [
                            "SAILED AWAY",
                            "You turn the helm and leave the cursed shore behind.",
                            "The screams fade into the sea as your ship continues its voyage.",
                            ""
                        ]
                        current_event_type = "ISLAND_RESOLUTION"
                        setup_event_ui(current_event_type)


                elif current_event_type == "ISLAND_RESOLUTION":
                    if btn_option_1.check_hover(mouse_pos):
                        prompts_faced_today += 1
                        show_error_message = False
                        globals()['current_state'] = "PLAYING"


                elif current_event_type == "ENEMY":
                    required_crew = 18 + int(pirate_difficulty_modifier * 2)


                    if btn_option_1.check_hover(mouse_pos):
                        if player_manpower < required_crew:
                            game_over_reason = "FIREPOWER"
                            max_days_survived = current_day
                            max_gold_claimed = player_gold
                            globals()['current_state'] = "GAME_OVER"
                        else:
                            screenshake_timer = 400
                            loss = max(1, (8 + int(pirate_difficulty_modifier)) - player_armor)
                            player_manpower = max(0, player_manpower - loss)
                            player_gold += 30  
                            current_event_type = "BATTLE_RESOLUTION"
                            resolution_text_lines = [
                                "SUCCESSFUL BROADSIDE ATTACK!",
                                "Your cannons layout heavy damage. Enemy yields and scatters!",
                                "+30g transit bounty claimed.",
                                f"Battle casualties sustained: -{loss} Manpower due to elevated hostiles."
                            ]
                            setup_event_ui(current_event_type)
                           
                    elif btn_option_2.check_hover(mouse_pos):
                        escape_chance = (player_speed - pirate_difficulty_modifier) * 10
                        if random.randint(1, 100) <= escape_chance:
                            current_event_type = "BATTLE_RESOLUTION"
                            resolution_text_lines = [
                                "MANEUVER EVASION SUCCESSFUL!",
                                "You catch the wind line perfectly, twisting through",
                                "their target zone unharmed into open oceans.",
                                ""
                            ]
                            setup_event_ui(current_event_type)
                        else:
                            game_over_reason = "SPEED"
                            max_days_survived = current_day
                            max_gold_claimed = player_gold
                            globals()['current_state'] = "GAME_OVER"


                    elif btn_option_3.check_hover(mouse_pos):
                        if player_cargo < 1:
                            game_over_reason = "SPEED"
                            max_days_survived = current_day
                            max_gold_claimed = player_gold
                            globals()['current_state'] = "GAME_OVER"
                        else:
                            player_cargo -= 1
                            current_event_type = "BATTLE_RESOLUTION"
                            resolution_text_lines = [
                                "CARGO RANSOM ACCEPTED",
                                "The raiders hoist up your offered freight.",
                                "They disappear back into the mist, allowing you",
                                "uninhibited passage forward."
                            ]
                            setup_event_ui(current_event_type)


                elif current_event_type == "PORT":
                    if btn_option_1.rect.collidepoint(mouse_pos) and btn_option_1.disabled:
                        error_text_string = "ERROR: NO CARGO TO CONVERT!"
                        show_error_message = True
                        error_message_timer = 2000
                    elif btn_option_1.check_hover(mouse_pos):
                        player_gold += (player_cargo * current_port_cargo_price)
                        player_cargo = 0
                        setup_event_ui("PORT")
                       
                    elif btn_option_2.rect.collidepoint(mouse_pos) and btn_option_2.disabled:
                        error_text_string = "ERROR: NOT ENOUGH GOLD!"
                        show_error_message = True
                        error_message_timer = 2000
                    elif btn_option_2.check_hover(mouse_pos):
                        if player_speed < 30:
                            player_gold -= current_port_sail_price
                            player_speed += 1
                            setup_event_ui("PORT")
                       
                    elif btn_option_3.rect.collidepoint(mouse_pos) and btn_option_3.disabled:
                        error_text_string = "ERROR: NOT ENOUGH GOLD!"
                        show_error_message = True
                        error_message_timer = 2000
                    elif btn_option_3.check_hover(mouse_pos):
                        if max_cargo_capacity < 20:
                            player_gold -= current_port_hold_price
                            max_cargo_capacity += 2
                            setup_event_ui("PORT")
                           
                    elif btn_option_4.rect.collidepoint(mouse_pos) and btn_option_4.disabled:
                        error_text_string = "ERROR: NOT ENOUGH GOLD!"
                        show_error_message = True
                        error_message_timer = 2000
                    elif btn_option_4.check_hover(mouse_pos):
                        player_gold -= current_port_crew_price
                        player_manpower += 3
                        setup_event_ui("PORT")
                           
                    elif btn_option_5.check_hover(mouse_pos):
                        action_taken = True
                       
                elif current_event_type == "ROGUE_WAVE":
                    if btn_option_1.check_hover(mouse_pos):
                        if player_armor >= 6:
                            action_taken = True
                        else:
                            game_over_reason = "WAVE_CRUSH"
                            max_days_survived = current_day
                            max_gold_claimed = player_gold
                            globals()['current_state'] = "GAME_OVER"


                elif current_event_type == "KRAKEN":
                    if btn_option_1.check_hover(mouse_pos):
                        if player_speed >= 15:
                            action_taken = True
                        else:
                            game_over_reason = "KRAKEN"
                            max_days_survived = current_day
                            max_gold_claimed = player_gold
                            globals()['current_state'] = "GAME_OVER"


                elif current_event_type in ["SQUID_TRAP", "BATTLE_RESOLUTION"]:
                    if btn_option_1.check_hover(mouse_pos):
                        action_taken = True


                if action_taken and current_state != "GAME_OVER":
                    prompts_faced_today += 1
                    show_error_message = False
                    if prompts_faced_today >= 3:
                        pay_tax_btn.update_text(f"PAY {current_tax_amount}G TAX & REST")
                        globals()['current_state'] = "TAX_TIME"
                    else:
                        globals()['current_state'] = "PLAYING"


            elif globals()['current_state'] == "TAX_TIME":
                if pay_tax_btn.check_hover(mouse_pos):
                    if player_gold >= current_tax_amount:
                        player_gold -= current_tax_amount
                        current_day += 1
                        current_tax_amount += 15  
                        pirate_difficulty_modifier += 0.2  
                        prompts_faced_today = 0
                        globals()['current_state'] = "PLAYING"
                    else:
                        game_over_reason = "BANKRUPT"
                        max_days_survived = current_day
                        max_gold_claimed = player_gold
                        globals()['current_state'] = "GAME_OVER"
                   
            elif globals()['current_state'] == "ISLAND_EXPLORE":
                if btn_option_1.check_hover(mouse_pos):
                    player_gold += globals()['island_explore_gold']
                    player_manpower = globals()['island_explore_crew']
                    resolution_text_lines = [
                        "ISLAND RETREAT",
                        "You pull your crew back from the jungle with loot in hand.",
                        f"Gold recovered: {globals()['island_explore_gold']}g. Remaining crew: {player_manpower}.",
                        ""
                    ]
                    current_event_type = "ISLAND_RESOLUTION"
                    setup_event_ui(current_event_type)
                    globals()['current_state'] = "EVENT_PROMPT"

            elif globals()['current_state'] == "GAME_OVER":
                if restart_btn.check_hover(mouse_pos):
                    globals()['current_state'] = "MENU"


    # --- 2. UPDATE STATE/ANIMATIONS ---
    bg_wave_timer += 0.02
    title_bob_timer += 0.05


    if globals()['current_state'] == "MENU":
        play_button.check_hover(mouse_pos)
    elif globals()['current_state'] == "CUSTOMIZATION":
        prev_button.check_hover(mouse_pos)
        next_button.check_hover(mouse_pos)
        select_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
    elif globals()['current_state'] == "EVENT_PROMPT":
        btn_option_1.check_hover(mouse_pos)
        btn_option_2.check_hover(mouse_pos)
        btn_option_3.check_hover(mouse_pos)
        if current_event_type == "PORT":
            btn_option_4.check_hover(mouse_pos)
            btn_option_5.check_hover(mouse_pos)
    elif globals()['current_state'] == "ISLAND_EXPLORE":
        btn_option_1.check_hover(mouse_pos)
        
    elif globals()['current_state'] == "TAX_TIME":
        pay_tax_btn.check_hover(mouse_pos)
    elif globals()['current_state'] == "GAME_OVER":
        restart_btn.check_hover(mouse_pos)
       
    elif globals()['current_state'] == "PLAYING":
        sea_scroll_x += 1.5
        if sea_scroll_x >= SCREEN_WIDTH:
            sea_scroll_x = 0
           
        if random.random() < CRATE_SPAWN_CHANCE:
            crates_list.append(FloatingCrate())


        for crate in crates_list[:]:
            crate.update()
            if crate.x > SCREEN_WIDTH + 50:
                crates_list.remove(crate)


        sailing_timer += delta_time
        if sailing_timer >= PROMPT_INTERVAL:
            sailing_timer = 0  
            crates_list.clear()
           
            if current_day == 5 and prompts_faced_today == 0:
                current_event_type = "ROGUE_WAVE"
            elif current_day > 10:
                current_event_type = random.choice(["ISLAND", "ENEMY", "PORT", "ROGUE_WAVE", "KRAKEN"])
            elif current_day >= 5:
                current_event_type = random.choice(["ISLAND", "ENEMY", "PORT", "ROGUE_WAVE"])
            else:
                current_event_type = random.choice(["ISLAND", "ENEMY", "PORT"])
               
            setup_event_ui(current_event_type)
            globals()['current_state'] = "EVENT_PROMPT"
    elif globals()['current_state'] == "ISLAND_EXPLORE":
        globals()['island_explore_timer'] += delta_time
        if globals()['island_explore_timer'] >= ISLAND_EXPLORE_TICK_MS:
            globals()['island_explore_timer'] = 0
            if globals()['island_explore_crew'] > 0:
                globals()['island_explore_gold'] += random.randint(12, 18)
                globals()['island_explore_crew'] = max(0, globals()['island_explore_crew'] - 1)
            if globals()['island_explore_crew'] <= 0:
                game_over_reason = "CANNIBALS"
                max_days_survived = current_day
                max_gold_claimed = player_gold
                globals()['current_state'] = "GAME_OVER"

    # --- 3. DRAWING ---
    screen.fill(DARK_BLUE)

    if globals()['current_state'] == "MENU":
        screen.blit(background_img, (0, 0))
        title_y = title_base_y + math.sin(title_bob_timer) * 8
        screen.blit(title_shadow, (title_x + 4, title_y + 4))
        screen.blit(title_main, (title_x, title_y))
        play_button.draw(screen)
        
        subtitle = font_subtitle.render("Press PLAY to begin your adventure", True, LIGHT_BLUE)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT - 100))

    elif globals()['current_state'] == "CUSTOMIZATION":
        screen.blit(background_img, (0, 0))
        
        ship_title = font_title.render("CHOOSE YOUR VESSEL", True, GOLD)
        screen.blit(ship_title, (SCREEN_WIDTH // 2 - ship_title.get_width() // 2, 30))
        
        chosen_ship = SHIPS[current_ship_index]
        ship_name = font_subtitle.render(chosen_ship["name"], True, GOLD)
        screen.blit(ship_name, (SCREEN_WIDTH // 2 - ship_name.get_width() // 2, 90))
        
        if chosen_ship["has_img"]:
            screen.blit(chosen_ship["surface"], (SCREEN_WIDTH // 2 - 130, 130))
        else:
            pygame.draw.rect(screen, SHADOW_COLOR, (SCREEN_WIDTH // 2 - 70, 140, 140, 80))
            pygame.draw.rect(screen, GOLD, (SCREEN_WIDTH // 2 - 66, 136, 140, 80))
        
        desc_text = font_button.render(chosen_ship["desc"], True, DARK_BLUE)
        screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 330))
        
        draw_stat_bar(screen, SCREEN_WIDTH // 2 - 150, 380, "SPEED:", chosen_ship["speed"])
        draw_stat_bar(screen, SCREEN_WIDTH // 2 - 150, 410, "ARMOR:", chosen_ship["armor"])
        draw_stat_bar(screen, SCREEN_WIDTH // 2 - 150, 440, "CARGO:", chosen_ship["cargo"])
        
        prev_button.draw(screen)
        next_button.draw(screen)
        select_button.draw(screen)
        back_button.draw(screen)

    elif current_state in ["PLAYING", "EVENT_PROMPT", "TAX_TIME", "GAME_OVER", "ISLAND_EXPLORE"]:
        if gameplay_ocean_img:
            screen.blit(gameplay_ocean_img, (sea_scroll_x + shake_x, 0 + shake_y))
            screen.blit(gameplay_ocean_img, (sea_scroll_x - SCREEN_WIDTH + shake_x, 0 + shake_y))
           
        if globals()['current_state'] == "PLAYING":
            for crate in crates_list:
                crate.draw(screen)


        draw_reward_popups(screen)


        ship_center_x = SCREEN_WIDTH // 2 - 130
        ship_center_y = SCREEN_HEIGHT // 2 - 50
        game_bob = math.sin(title_bob_timer * 0.5) * 3
       
        if player_ship_has_img and current_state != "GAME_OVER":
            screen.blit(player_ship_surface, (ship_center_x + shake_x, ship_center_y + game_bob + shake_y))
        elif current_state != "GAME_OVER":
            pygame.draw.rect(screen, GOLD, (ship_center_x + 65 + shake_x, ship_center_y + 45 + game_bob + shake_y, 130, 91))


        draw_top_bar(screen)


        # --- RANDOM ENCOUNTER OVERLAY ---
        if globals()['current_state'] == "EVENT_PROMPT":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((11, 24, 44, 230))
            screen.blit(overlay, (0, 0))

            box_height = 420 if current_event_type in ["ISLAND", "ISLAND_RESOLUTION"] else 250 if current_event_type == "PORT" else 210
            pygame.draw.rect(screen, SHADOW_COLOR, (64, 54, 672, box_height))

            frame_color = GOLD
            if current_event_type == "ENEMY":
                frame_color = RED
            elif current_event_type == "PORT":
                frame_color = GREEN
            elif current_event_type in ["SQUID_TRAP", "BATTLE_RESOLUTION", "ROGUE_WAVE", "KRAKEN"]:
                frame_color = PURPLE
            pygame.draw.rect(screen, frame_color, (60, 50, 672, box_height), 4)

            prompt_left = 60
            prompt_top = 50
            prompt_width = 672
            prompt_center_x = prompt_left + prompt_width // 2
            prompt_inner_width = prompt_width - 40

            title_text = ""
            body_lines = []
            body_colors = []
            accent_lines = []
            accent_colors = []

        elif globals()['current_state'] == "ISLAND_EXPLORE":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((11, 24, 44, 230))
            screen.blit(overlay, (0, 0))

            box_height = 360
            pygame.draw.rect(screen, SHADOW_COLOR, (64, 54, 672, box_height))
            pygame.draw.rect(screen, GOLD, (60, 50, 672, box_height), 4)

            prompt_left = 60
            prompt_top = 50
            prompt_width = 672
            prompt_center_x = prompt_left + prompt_width // 2
            prompt_inner_width = prompt_width - 40

            title_text = "ISLAND EXPLORATION"
            body_lines = [
                "Your crew pushes deeper into the jungle, trading men for treasure.",
                "The longer you stay, the more gold you collect — but the more crew you lose.",
                "Leave before your manpower drops to zero or the island claims your ship."
            ]
            body_colors = [WHITE, WHITE, GOLD]
            accent_lines = []
            accent_colors = []
            title_color = GOLD

            title_lines = wrap_text(title_text, font_subtitle, prompt_inner_width)
            body_wrapped = []
            for idx, line in enumerate(body_lines):
                wrapped = wrap_text(line, font_event, prompt_inner_width)
                for wrapped_line in wrapped:
                    body_wrapped.append((wrapped_line, body_colors[idx]))

            current_y = prompt_top + 20
            for line in title_lines:
                title_surf = font_subtitle.render(line, True, title_color)
                screen.blit(title_surf, (prompt_center_x - title_surf.get_width() // 2, current_y))
                current_y += font_subtitle.get_linesize() + 2

            current_y += 20
            for line, color in body_wrapped:
                body_surf = font_event.render(line, True, color)
                screen.blit(body_surf, (prompt_center_x - body_surf.get_width() // 2, current_y))
                current_y += font_event.get_linesize() + 4

            current_y += 20
            bar_x = prompt_left + 30
            bar_width = prompt_width - 60
            bar_height = 30

            crew_ratio = globals()['island_explore_crew'] / globals()['island_explore_start_crew'] if globals()['island_explore_start_crew'] else 0
            pygame.draw.rect(screen, SHADOW_COLOR, (bar_x + 3, current_y + 3, bar_width, bar_height))
            pygame.draw.rect(screen, RED, (bar_x, current_y, int(bar_width * crew_ratio), bar_height))
            crew_label = font_event.render(f"Crew Remaining: {globals()['island_explore_crew']}/{globals()['island_explore_start_crew']}", True, WHITE)
            screen.blit(crew_label, (bar_x + 8, current_y + 4))

            current_y += bar_height + 20
            gold_goal = max(200, globals()['island_explore_start_crew'] * 120)
            gold_ratio = min(1.0, globals()['island_explore_gold'] / gold_goal)
            pygame.draw.rect(screen, SHADOW_COLOR, (bar_x + 3, current_y + 3, bar_width, bar_height))
            pygame.draw.rect(screen, GOLD, (bar_x, current_y, int(bar_width * gold_ratio), bar_height))
            gold_label = font_event.render(f"Gold Collected: {globals()['island_explore_gold']}g", True, WHITE)
            screen.blit(gold_label, (bar_x + 8, current_y + 4))

            current_y += bar_height + 24
            next_tick = max(0.0, (ISLAND_EXPLORE_TICK_MS - globals()['island_explore_timer']) / 1000.0)
            next_tick_text = f"Next search in: {next_tick:.1f}s"
            tick_label = font_event.render(next_tick_text, True, WHITE)
            screen.blit(tick_label, (bar_x + 8, current_y))

            current_y += font_event.get_linesize() + 12
            btn_option_1.draw(screen)

        if globals()['current_state'] == "EVENT_PROMPT":
            if current_event_type == "ISLAND":
                title_text = "BOARDING THE ISLAND"
                body_lines = [
                    "You steer toward the beach. The jungle shivers and distant screams drift over the water.",
                    "Choose to explore the island or turn back before the shore swallows your crew.",
                ]
                body_colors = [WHITE, WHITE]
                accent_lines = ["The sea is calm, but the island feels cursed."]
                accent_colors = [GOLD]
            elif current_event_type == "ISLAND_RESOLUTION":
                title_text = resolution_text_lines[0]
                body_lines = [resolution_text_lines[1], resolution_text_lines[2]]
                body_colors = [WHITE, WHITE]
                accent_lines = [resolution_text_lines[3]] if resolution_text_lines[3] else []
                accent_colors = [GOLD] * len(accent_lines)
            elif current_event_type == "ENEMY":
                title_text = "ENEMY STANDOFF!"
                body_lines = [
                    "Hostile interceptors block your trajectory!",
                    "Defeating or evading them gets harder every surviving day.",
                ]
                body_colors = [WHITE, WHITE]
            elif current_event_type == "PORT":
                title_text = "LOCAL PORT MARKET"
                body_lines = [
                    "Prices fluctuate based on local resource scarcity at this dock.",
                    f"YOUR VAULT: {player_gold}g | HOLD: {player_cargo}/{max_cargo_capacity} | CREW: {player_manpower} | SPEED: {player_speed}/30",
                ]
                body_colors = [WHITE, GOLD]
            elif current_event_type == "SQUID_TRAP":
                title_text = "CRATE TRAP!"
                body_lines = [
                    "A giant toxic sea squid burst directly out of the box cargo!",
                    f"It smashed into your vaults and sank {trap_gold_lost}g (5%) into the sea!",
                ]
                body_colors = [WHITE, RED]
            elif current_event_type == "ROGUE_WAVE":
                title_text = "⚠️ ROGUE WAVE APPROACHING! ⚠️"
                body_lines = [
                    "A towering wall of dark water crashes down onto your hull!",
                    "Click 'CONTINUE VOYAGE' to brace. Sturdy structural armor is required.",
                ]
                body_colors = [WHITE, GOLD]
            elif current_event_type == "KRAKEN":
                title_text = "THE KRAKEN AWAKENS!"
                body_lines = [
                    "Colossal dark leviathan tentacles rise from the abyssal ocean deep!",
                    "You must maintain a tactical engine speed of 15 to escape its grasp.",
                ]
                body_colors = [WHITE, GOLD]
            elif current_event_type == "BATTLE_RESOLUTION":
                title_text = resolution_text_lines[0]
                body_lines = [resolution_text_lines[1], resolution_text_lines[2]]
                body_colors = [WHITE, WHITE]
                accent_lines = [resolution_text_lines[3]] if resolution_text_lines[3] else []
                accent_colors = [GOLD] * len(accent_lines)

            title_color = GOLD
            if current_event_type == "ENEMY":
                title_color = RED
            elif current_event_type == "PORT":
                title_color = GREEN
            elif current_event_type in ["SQUID_TRAP", "KRAKEN"]:
                title_color = PURPLE if current_event_type == "SQUID_TRAP" else RED
            elif current_event_type == "ISLAND_RESOLUTION":
                title_color = GOLD if "TREASURE" in title_text else ORANGE
            elif current_event_type == "BATTLE_RESOLUTION":
                title_color = GREEN if "SUCCESS" in title_text or "MANEUVER" in title_text else ORANGE

            title_lines = wrap_text(title_text, font_subtitle, prompt_inner_width)
            body_wrapped = []
            for idx, line in enumerate(body_lines):
                wrapped = wrap_text(line, font_event, prompt_inner_width)
                for wrapped_line in wrapped:
                    body_wrapped.append((wrapped_line, body_colors[idx]))

            accent_wrapped = []
            for idx, line in enumerate(accent_lines):
                wrapped = wrap_text(line, font_event, prompt_inner_width)
                for wrapped_line in wrapped:
                    accent_wrapped.append((wrapped_line, accent_colors[idx]))

            prompt_art_height = 0
            box_height = max(210, 28 + (len(title_lines) * font_subtitle.get_linesize()) + 10 + prompt_art_height + 10 + (len(body_wrapped) * (font_event.get_linesize() + 4)) + 8 + (len(accent_wrapped) * (font_event.get_linesize() + 4)) + 20)
            if current_event_type in ["ISLAND", "ISLAND_RESOLUTION"]:
                box_height = max(box_height, 520)

            prompt_box = pygame.Rect(prompt_left, prompt_top, prompt_width, box_height)
            pygame.draw.rect(screen, SHADOW_COLOR, (prompt_box.x + 4, prompt_box.y + 4, prompt_box.width, prompt_box.height))
            pygame.draw.rect(screen, frame_color, prompt_box, 4)

            current_y = prompt_top + 20
            for line in title_lines:
                title_surf = font_subtitle.render(line, True, title_color)
                screen.blit(title_surf, (prompt_center_x - title_surf.get_width() // 2, current_y))
                current_y += font_subtitle.get_linesize() + 2

            current_y += 20
            for line, color in body_wrapped:
                body_surf = font_event.render(line, True, color)
                screen.blit(body_surf, (prompt_center_x - body_surf.get_width() // 2, current_y))
                current_y += font_event.get_linesize() + 4

            current_y += 6
            for line, color in accent_wrapped:
                accent_surf = font_event.render(line, True, color)
                screen.blit(accent_surf, (prompt_center_x - accent_surf.get_width() // 2, current_y))
                current_y += font_event.get_linesize() + 4

            if show_error_message:
                error_surf = font_event.render(error_text_string, True, RED)
                screen.blit(error_surf, (SCREEN_WIDTH // 2 - error_surf.get_width() // 2, 210 if current_event_type == "PORT" else 190))

            btn_option_1.draw(screen)
            if current_event_type == "ISLAND":
                btn_option_2.draw(screen)
            elif current_event_type == "ISLAND_RESOLUTION":
                pass
            elif current_event_type in ["ENEMY", "PORT"]:
                btn_option_2.draw(screen)
                btn_option_3.draw(screen)
            if current_event_type == "PORT":
                btn_option_4.draw(screen)
                btn_option_5.draw(screen)

            if current_event_type in ["ISLAND", "ISLAND_RESOLUTION"]:
                pass
        elif globals()['current_state'] == "TAX_TIME":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((11, 24, 44, 180))
            screen.blit(overlay, (0, 0))
           
            pygame.draw.rect(screen, SHADOW_COLOR, (144, 144, 512, 312))
            pygame.draw.rect(screen, GOLD, (140, 140, 512, 312), 4)
           
            t_text1 = font_subtitle.render("SAFE ANCHORAGE REACHED", True, GOLD)
            t_text2 = font_event.render(f"End of Day {current_day}. The Royal Fleet requires customs tax.", True, WHITE)
            t_text3 = font_event.render("Failing to pay results in immediate ship impounding.", True, WHITE)
           
            screen.blit(t_text1, (SCREEN_WIDTH // 2 - t_text1.get_width() // 2, 175))
            screen.blit(t_text2, (SCREEN_WIDTH // 2 - t_text2.get_width() // 2, 250))
            screen.blit(t_text3, (SCREEN_WIDTH // 2 - t_text3.get_width() // 2, 290))
            pay_tax_btn.draw(screen)


        elif globals()['current_state'] == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 10, 10, 225))
            screen.blit(overlay, (0, 0))
           
            pygame.draw.rect(screen, SHADOW_COLOR, (144, 104, 512, 392))
            pygame.draw.rect(screen, RED, (140, 100, 512, 392), 4)
           
            go_title = font_title.render("SHIPWRECKED", True, RED)
            screen.blit(go_title, (SCREEN_WIDTH // 2 - go_title.get_width() // 2, 120))
           
            reason_string = "Your manpower dropped to absolute zero inside the crossfires."
            if game_over_reason == "SPEED":
                reason_string = "Tactical escape speed failure. Raiders overrun your decks."
            elif game_over_reason == "BANKRUPT":
                reason_string = "You lacked the funds for Royal customs tax. Ship confiscated."
            elif game_over_reason == "WAVE_CRUSH":
                reason_string = "Hull broken. Massive rogue wave split your structural frame."
            elif game_over_reason == "KRAKEN":
                reason_string = "Dragged into the abyss. Sunk under the pressure of the beast."
            elif game_over_reason == "CANNIBALS":
                reason_string = "Cannibals overwhelmed your shore party. The island claimed the crew."


            go_reason = font_event.render(reason_string, True, WHITE)
            go_stat1 = font_event.render(f"Days Navigated: {max_days_survived}", True, GOLD)
            go_stat2 = font_event.render(f"Gold Saved in Vault: {max_gold_claimed}g", True, GOLD)
           
            screen.blit(go_reason, (SCREEN_WIDTH // 2 - go_reason.get_width() // 2, 220))
            screen.blit(go_stat1, (SCREEN_WIDTH // 2 - go_stat1.get_width() // 2, 280))
            screen.blit(go_stat2, (SCREEN_WIDTH // 2 - go_stat2.get_width() // 2, 320))
            restart_btn.draw(screen)


    pygame.display.flip()
    clock.tick(60)
