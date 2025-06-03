import pygame
import sys
import random
import math

#MQTT########################################################################################################
import threading
import paho.mqtt.client as mqtt

mqtt_broker = "192.168.0.157"
mqtt_topic = "GAME/Bert"
left_pressed = False
right_pressed = False



################################################################################################


pygame.init()

#Variables###########################################################################################

screen_width = 400
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PONG")

spawn_x = random.randint(40, 360)
spawn_y = random.randint(40, 360)

wall_size = 20

ball_radius = 10
ball_x = 0
ball_y = 0
ball_mx = 0
ball_my = 0
ball_speed_magnitude = 0

lives = 0

Color_Black = (0, 0, 0)
Color_White = (255, 255, 255)
Color_Blue = (0, 0, 255)
Corner_Max = 75.0
name_input = ""

mode_selection = 0

player_score_file = "player_scores.txt"

game_start_time = None
game_time = 0.0

player_height = 40
player_thickness = 5
player_x_coord = screen_width - wall_size - (player_thickness / 2)
player_y_center = screen_height / 2
player_speed = 5

color = (255, 255, 255)
color_dark = (100, 100, 100)

width = screen.get_width()
height = screen.get_height()
bigfont = pygame.font.SysFont('Corbel', 50)
middlefont = pygame.font.SysFont('Corbel', 35)
smallfont = pygame.font.SysFont('Corbel', 28)
smallerfont = pygame.font.SysFont('Corbel', 20)

easy = middlefont.render('easy', True, color)
medium = middlefont.render('medium', True, color)
hard = middlefont.render('hard', True, color)

mode = 0

clock = pygame.time.Clock()

#FUNCTIONS SCORE###########################################################################################
def random_ball_spawn(target_speed):
    # SPAWN BALL RANDOMIZER
    global ball_x, ball_y, ball_mx, ball_my, ball_speed_magnitude
    ball_speed_magnitude = target_speed


    ball_x = random.randint(wall_size + ball_radius, screen_width - wall_size - ball_radius - 100)
    ball_y = random.randint(wall_size + ball_radius, screen_height - wall_size - ball_radius - 1)
    angle_offset = random.uniform(-math.pi / 4.5, math.pi / 4.5)

    ball_mx = -abs(ball_speed_magnitude * math.cos(angle_offset))
    ball_my = ball_speed_magnitude * math.sin(angle_offset)
#SCORE SAVE TXT FILE
def save_score(name, score):
    try:
        with open(player_score_file, "a") as f:
            f.write(f"{name.strip()},{score:.2f}\n")

        print(f"Score for '{name.strip()}' saved: {score:.2f}s")
    except Exception as e:
        print(f"Error saving score: {e}")

#LEADERBOARD
def load_leaderboard():
    scores = []
    try:
        with open(player_score_file, "r") as f:
            for line in f:

                parts = line.strip().split(',')


                if len(parts) == 2:
                    try:
                        name = parts[0]
                        score_val = float(parts[1])
                        scores.append((name, score_val))
                    except ValueError:
                        print(f"error in line: {line.strip()}")
    except Exception as e:
        print(f"Error loading scores: {e}")

    scores.sort(key=lambda item: item[1], reverse=True)
    return scores

#MQTT CONNECTION
def on_connect(client, userdata, flags, rc):
    print(f"connected{rc}")
    client.subscribe(mqtt_topic)
#MESSAGE RECEIVER ON MQTT
def on_message(client, userdata, msg):
    global left_pressed, right_pressed
    payload = msg.payload.decode()

    print("MQTT:", payload)
    parts = payload.strip().split()



    if len(parts) == 2:
        left_pressed = parts[0].strip() == '0'
        right_pressed = parts[1].strip() == '0'

    print("PRESS:", left_pressed, right_pressed)



def mqtt_loop():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, 1883, 60)
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()
#LOOP###########################################################################################

run = True

while run:

    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if mode == "INPUT_NAME":
                if event.key == pygame.K_RETURN:
                    if len(name_input.strip()) > 0:

                        mode = mode_selection
                        lives = 3
                        game_start_time = pygame.time.get_ticks()
                        game_time = 0.0
                        if mode == 1:
                            player_height = 50; random_ball_spawn(4)
                        if mode == 2:
                            player_height = 40; random_ball_spawn(6)
                        if mode == 3:
                            player_height = 30; random_ball_spawn(8)
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                else:
                    if len(name_input) < 20:
                        name_input += event.unicode



        if event.type == pygame.MOUSEBUTTONDOWN:
            # Chooser if mode not chosen
            if mode == 0:
                # EASY 1
                if width / 2 - 100 <= mouse[0] <= width / 2 + 100 and height / 2 - 100 <= mouse[1] <= height / 2 - 40:
                    mode_selection = 1
                    mode = "INPUT_NAME"
                    name_input = ""
                if width / 2 - 100 <= mouse[0] <= width / 2 + 100 and height / 2 - 30 <= mouse[1] <= height / 2 + 30:
                    mode_selection = 2
                    mode = "INPUT_NAME"
                    name_input = ""
                if width / 2 - 100 <= mouse[0] <= width / 2 + 100 and height / 2 + 40 <= mouse[1] <= height / 2 + 100:
                    mode_selection = 3
                    mode = "INPUT_NAME"
                    name_input = ""
    if (mode == 1 or mode == 2 or mode == 3 and game_start_time != None):
        game_time = (pygame.time.get_ticks() - game_start_time) / 1000.0

#MENU
    if mode == 0:
        screen.fill(Color_Black)
        #1#############################################################
        pygame.draw.rect(screen, color_dark, [width / 2 - 100, height / 2 - 100, 200, 60])
        screen.blit(easy, (width / 2 - 30, height / 2 - 85))
        #2##############################################################
        pygame.draw.rect(screen, color_dark, [width / 2 - 100, height / 2 - 30, 200, 60])
        screen.blit(medium, (width / 2 - 55, height / 2 - 15))
        #3#############################################################
        pygame.draw.rect(screen, color_dark, [width / 2 - 100, height / 2 + 40 , 200, 60])
        screen.blit(hard, (width / 2 - 30, height / 2 +55))

#INPUT
    elif mode == "INPUT_NAME":

        screen.fill(Color_Black)
        prompt_text_surface = middlefont.render("Enter your name:", True, Color_White)
        input_box_rect = pygame.Rect(width // 2 - 100, height // 2 - 20, 200, 40)

        name_text_surface = smallfont.render(name_input, True, Color_White)
        screen.blit(prompt_text_surface, (width / 2 - prompt_text_surface.get_width() / 2, height / 2 - 60))


        screen.blit(name_text_surface, (input_box_rect.x + 5, input_box_rect.y + (input_box_rect.height - name_text_surface.get_height()) / 2))

        if pygame.time.get_ticks() // 500 % 2 == 0:
            cursor_x = input_box_rect.x + 5 + name_text_surface.get_width()
            pygame.draw.line(screen, Color_White, (cursor_x, input_box_rect.y + 5), (cursor_x, input_box_rect.bottom - 5), 2)
#LEADERBOARD
    elif mode == "LEADERBOARD":
        screen.fill(Color_Black)
        loaded_scores = load_leaderboard()
        y_offset = 100
        for i, (name, score_val) in enumerate(loaded_scores[:10]):  # Toon top 10
            rank_text = f"{i + 1}. {name}: {score_val:.2f}s"
            score_surface = middlefont.render(rank_text, True, Color_White)
            screen.blit(score_surface, (width / 2 - score_surface.get_width() / 2, y_offset))
            y_offset += 30



#MOVEMENT
    if mode == 1 or mode == 2 or mode == 3:
        keys = pygame.key.get_pressed()



        if (keys[pygame.K_UP] or left_pressed) and (player_y_center - player_height / 2) > wall_size:
            player_y_center -= player_speed
        if (keys[pygame.K_DOWN] or right_pressed) and (player_y_center + player_height / 2) < (screen_height - wall_size):
            player_y_center += player_speed
#BALL MOVELENT
        ball_x += ball_mx
        ball_y += ball_my


            # Left wall
        if ball_x - ball_radius < wall_size:
            ball_x = wall_size + ball_radius
            ball_mx *= -1
            # Top wall
        if ball_y - ball_radius < wall_size:
            ball_y = wall_size + ball_radius
            ball_my *= -1
            # Bottom wall
        if ball_y + ball_radius > screen_height - wall_size:
            ball_y = screen_height - wall_size - ball_radius
            ball_my *= -1
        #DRAWING###########################################################################################
        if mode == 1:
            screen.fill((100, 200, 100))
        if mode == 2:
            screen.fill((255, 255, 0))
        if mode == 3:
            screen.fill((255, 50, 50))

        # Draw Walls
        pygame.draw.rect(screen, Color_Black, (0, 0, screen_width, wall_size))
        pygame.draw.rect(screen, Color_Black, (0, screen_height - wall_size, screen_width, wall_size))
        pygame.draw.rect(screen, Color_Black, (0, 0, wall_size, screen_height))
        goal_rect = pygame.draw.rect(screen, (255, 0, 0), (screen_width - 2, 0, 2, screen_height))

        # Draw Ball
        ball_rect = pygame.draw.circle(screen, Color_Black, (int(ball_x), int(ball_y)), ball_radius)

        #Draw Player

        player_top_y = player_y_center - player_height / 2
        player_rect = pygame.Rect(player_x_coord - player_thickness / 2, player_top_y, player_thickness, player_height)
        pygame.draw.line(screen, Color_Blue, (player_x_coord, player_top_y),(player_x_coord, player_y_center + player_height / 2), player_thickness)

        #COLLISSION###########################################################################################

        if ball_rect.colliderect(player_rect):
            hitpoint_pallet = ball_y - player_top_y
            middle = hitpoint_pallet - (player_height / 2)

            if player_height > 0:
                abs_lengt = max(-1.0, min(1.0, middle / (player_height / 2)))
            else:
                abs_lengt = 0


            radials = math.radians(abs_lengt * 75)
            ball_my = ball_speed_magnitude * math.sin(radials)
            ball_mx = -abs(ball_speed_magnitude * math.cos(radials))
            ball_x = player_rect.left - ball_radius - 1

        if ball_rect.colliderect(goal_rect):
            lives -= 1
            if lives <= 0:
                final_score = game_time
                if len(name_input.strip()) > 0:
                    save_score(name_input, final_score)
                else:
                    save_score("NONAME", final_score)

                lose_text_surf = bigfont.render('YOU LOSE!', True, Color_Black)




                losescreen = screen.get_at((width // 2, height // 2))
                screen.fill(losescreen)
                screen.blit(lose_text_surf,
                            (width / 2 - lose_text_surf.get_width() / 2, height / 2 - lose_text_surf.get_height() / 2))
                pygame.display.flip()
                pygame.time.wait(1000)

                mode = "LEADERBOARD"
                game_start_time = None
                name_input = ""
            else:
                if mode == 1:
                    random_ball_spawn(4)
                elif mode == 2:
                    random_ball_spawn(6)
                elif mode == 3:
                    random_ball_spawn(8)

        if mode == 1 or mode == 2 or mode == 3:
            lives_text = smallerfont.render(f'Lives: {lives}', True, Color_Black)
            screen.blit(lives_text, (wall_size + 10, screen_height - wall_size - lives_text.get_height() - 5))

            timer_text = smallerfont.render(f'Time: {game_time:.1f}s', True, Color_Black)
            screen.blit(timer_text, (width - timer_text.get_width() - wall_size - 10,
                                     screen_height - wall_size - timer_text.get_height() - 5))

    pygame.display.flip()


    clock.tick(60)

pygame.quit()