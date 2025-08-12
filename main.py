import pygame as py
import random
from random import randint
from sys import exit
import os
import sys

py.init()
py.mixer.init()

# Helper function for resource paths (PyInstaller safe)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set up display early — BEFORE loading images with convert_alpha()
screen = py.display.set_mode((800, 400))
py.display.set_caption("Pixel Sprinter")
py.display.set_icon(py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Player", "player_stand.png"))))

# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "Game Assets", "Audio")
GRAPHICS_DIR = os.path.join(BASE_DIR, "Game Assets", "graphics")
FONT_DIR = os.path.join(BASE_DIR, "Game Assets", "Font")

# Load sounds
jump = py.mixer.Sound(resource_path(os.path.join("Game Assets", "Audio", "jump.mp3")))
jump.set_volume(0.5)

game_over = py.mixer.Sound(resource_path(os.path.join("Game Assets", "Audio", "game-over.mp3")))
game_over.set_volume(0.7)

bg_music_path = resource_path(os.path.join("Game Assets", "Audio", "music.wav"))
py.mixer.music.load(bg_music_path)
py.mixer.music.set_volume(0.7)
py.mixer.music.play(-1)  # Loop background music

# Load obstacle graphics
snail1 = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "snail", "snail1.png"))).convert_alpha()
snail2 = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "snail", "snail2.png"))).convert_alpha()
snail_frames = [snail1, snail2]
snail_index = 0

fly1 = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Fly", "Fly1.png"))).convert_alpha()
fly2 = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Fly", "Fly2.png"))).convert_alpha()
fly_frames = [fly1, fly2]
fly_index = 0

animation_speed = 0.1  # Speed of obstacle animation

# Load background
sky_surf = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Sky.png")))
ground_surf = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Ground.png")))

# Load player graphics
player_jump = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Player", "jump.png"))).convert_alpha()
player_walk1 = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Player", "player_walk_1.png"))).convert_alpha()
player_walk2 = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Player", "player_walk_2.png"))).convert_alpha()
player_walk = [player_walk1, player_walk2]
player_index = 0
player_surf = player_walk[player_index]
player_rect = player_surf.get_rect(midbottom=(180, 300))

# Fonts and UI
color = "#23A078"
font = py.font.Font(resource_path(os.path.join("Game Assets", "Font", "Pixeltype.ttf")), 50)
intro_player = py.image.load(resource_path(os.path.join("Game Assets", "graphics", "Player", "player_stand.png"))).convert_alpha()
scaled_intro_player = py.transform.scale2x(intro_player)
scaled_intro_player_rect = scaled_intro_player.get_rect(center=(400, 200))
game_name = font.render('Pixel Sprinter', False, color)
game_name_rect = game_name.get_rect(center=(400, 50))
start_text = font.render('Press Space To Start', False, (0, 0, 0))
start_text_rect = start_text.get_rect(center=(400, 350))

# Functions
def player_animation():
    global player_surf, player_index
    if player_rect.bottom < 300:
        player_surf = player_jump
    else:
        player_index += 0.1
        if player_index >= len(player_walk):
            player_index = 0
        player_surf = player_walk[int(player_index)]

def display_score():
    current_time = 0
    if game_active:
        current_time = int((py.time.get_ticks() - start_time) / 1000)
        score_text = font.render(f'Score: {current_time}', False, (0, 0, 0))
        score_text_rect = score_text.get_rect(center=(400, 50))
        screen.blit(score_text, score_text_rect)
    return current_time

def obstacle_spawn():
    obstacle_type = random.choice(["snail", "fly"])
    if obstacle_type == "snail":
        rect = snail_frames[0].get_rect(midbottom=(randint(900, 1100), 300))
    else:
        rect = fly_frames[0].get_rect(midbottom=(randint(900, 1100), 180))
    return (obstacle_type, rect)

def obstacle_movement(obstacle_list):
    global snail_index, fly_index
    for i, (obstacle_type, rect) in enumerate(obstacle_list):
        speed = 5
        if score >= 20: speed = 6.5
        if score >= 40: speed = 8
        if score >= 60: speed = 10
        if score >= 80: speed = 12
        if score >= 100: speed = 15
        rect.x -= speed
        obstacle_list[i] = (obstacle_type, rect)
    snail_index += animation_speed
    if snail_index >= len(snail_frames):
        snail_index = 0
    fly_index += animation_speed
    if fly_index >= len(fly_frames):
        fly_index = 0
    for obstacle_type, rect in obstacle_list:
        if obstacle_type == "snail":
            image = snail_frames[int(snail_index)]
        else:
            image = fly_frames[int(fly_index)]
        screen.blit(image, rect)
    return [ob for ob in obstacle_list if ob[1].x > -100]

def collision():
    global game_active, final_score
    for obstacle_type, rect in obstacle_list:
        if player_rect.colliderect(rect):
            final_score = score
            game_active = False
            py.mixer.music.stop()
            game_over.play()
            player_rect.bottom = 300
            obstacle_list.clear()
            break

def update_obstacles():
    global obstacle_list
    obstacle_list.append(obstacle_spawn())

# Variables
clock = py.time.Clock()
game_active = False
player_gravity = 0
start_time = 0
score = 0
final_score = 0
obstacle_list = []
obstacle_timer = py.USEREVENT + 1
py.time.set_timer(obstacle_timer, 1500)

# Main game loop
while True:
    for event in py.event.get():
        if event.type == py.QUIT:
            exit()

        if not game_active:
            if event.type == py.KEYDOWN and event.key == py.K_SPACE:
                game_active = True
                start_time = py.time.get_ticks()
                score = 0
                game_over.stop()
                py.mixer.music.play(-1)
        else:
            if event.type == py.KEYDOWN and event.key == py.K_SPACE and player_rect.bottom >= 300:
                player_gravity = -20
                jump.play()
            if event.type == py.MOUSEBUTTONDOWN and player_rect.bottom >= 300:
                player_gravity = -20
                jump.play()
            if event.type == obstacle_timer:
                update_obstacles()

    if game_active:
        player_gravity += 1
        player_rect.y += player_gravity
        if player_rect.bottom >= 300:
            player_rect.bottom = 300
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, 300))
        obstacle_list = obstacle_movement(obstacle_list)
        collision()
        player_animation()
        screen.blit(player_surf, player_rect)
        score = display_score()
    else:
        screen.fill((76, 180, 250))
        screen.blit(scaled_intro_player, scaled_intro_player_rect)
        screen.blit(game_name, game_name_rect)
        credits_text = font.render('Made By Ezz', False, (0, 0, 0))
        credits_text_rect = credits_text.get_rect(topright=(785, 370))
        if final_score == 0:
            screen.blit(start_text, start_text_rect)
            screen.blit(credits_text, credits_text_rect)
        else:
            score_text = font.render(f'You Died, Your Score: {final_score}', False, (7, 245, 245))
            score_text_rect = score_text.get_rect(center=(400, 350))
            screen.blit(score_text, score_text_rect)

    py.display.update()
    clock.tick(60)
