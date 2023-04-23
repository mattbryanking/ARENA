# raycasting engine was extended from https://www.youtube.com/watch?v=4gqPv7A_YRY&t=448.
# drawing the walls and floor was all from this video, as well as some movement and sprite
# positioning, basically everything else was done by me.
#
# added support for ceiling rendering, multiple wall textures,
# custom level structures, and of course gameplay elements.
#
# uses custom implementations of sprite sorting, animation handling, sprite angle correction,
# collision detection, a more robust shading system, and detection to see if sprite is behind
# a wall.
#
# this code is a mess. i'm sorry.

import pygame
import numpy
import re
from numba import njit  # free RTX 4090 GPU :D


def main():
    pygame.init()
    pygame.font.init()

    # used for fps managment
    clock = pygame.time.Clock()

    # window name + icon
    pygame.display.set_caption('The Elder Scrolls: Arena')
    pygame.display.set_icon(pygame.image.load(
        './Assets/System/window icon.png'))

    # window size
    screen = pygame.display.set_mode((1066, 800))

    # false when time to close game
    running = True

    # horizontal and vertical (half) resolutions
    h_res = 120
    v_res = 120

    # enter menu
    name = menu(screen, running)

    # enter dungeon
    dungeon(screen, running, clock, h_res, v_res, name)


def dungeon(screen, running, clock, h_res, v_res, name):

    # scaling factor / fov
    fov = h_res / 60

    # position and rotation of camera
    pos_x, pos_y, rot = 2.5, 2.5, 0

    # level size (size x size)
    size = 30
    
    # for the LIFE of me I cannot figure out why, but the level array mirrors itself on both axis. Only the changes in 
    # the upper left quadrant matter, and they're mirrored across the x and y axis. for now, i'm just making the area of 
    # the level 4x bigger than it needs to be, and then only using the upper left quadrant.
    level = numpy.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 5, 1, 1, 1, 1, 1, 1, 3, 4, 4, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 1, 0, 0, 0, 2, 0, 0, 5, 0, 5, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 3, 0, 2, 0, 0, 0, 1, 0, 0, 5, 0, 5, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 4, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 1, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 5, 0, 0, 5, 1, 1, 4, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0, 0, 0, 5, 2, 5, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 2, 3, 2, 0, 0, 0, 5, 0, 5, 1, 3, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    # use numpy uniform distribution to create pixel arrays
    floor_frame = numpy.random.uniform(0, 1, (h_res, v_res * 2, 3))
    ceiling_frame = numpy.random.uniform(0, 1, (h_res, v_res * 2, 3))

    # gets textures for surfaces
    floor, ceiling, floor_walls, ceiling_walls = get_textures()

    # gets sprites and info about them
    enemy_sprites, sprite_size, sprites_sword = get_sprites()

    # randomly spawns specified amount of enemies
    enemies = spawn_enemies(10, level, 15)

    # UI stuff
    ui_base, name_bg, name, fatigue, health, magicka = get_ui(name)

    # mouse stuff
    cursor, cursor_rect, cursor_sword, cursor_sword_rect = get_mouse()

    # sound stuff (but a lot of it is handled elsewhere)
    walk_sound, sword_sound, damage_sound, death_sound = get_sounds()


    last_update = pygame.time.get_ticks()
    sprite_frame = 0
    sprite_frame_dir = 0

    last_update_sword = pygame.time.get_ticks()
    swinging = False
    sword_frame = 0

    over_enemy = False

    in_enemy = False
    last_update_damage = pygame.time.get_ticks()\
    
    alive = True

    # MAIN GAME LOOP!!!!
    while running:

        # checks if mouse was clicked last frame
        clicked = False

        for event in pygame.event.get():
            # close window
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pygame.mouse.get_pos()[1] < 600:
                clicked = True
                if alive:
                    sword_sound.play()
                swinging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                clicked = False

        # updates pixel array for graphics every frame
        # this is paramater hell. i am ashamed.
        floor_frame = new_frame(
            pos_x, pos_y, rot, floor_frame, floor, h_res, v_res, fov, level, size, floor_walls, 100, 100)
        ceiling_frame = new_frame(
            pos_x, pos_y, rot, ceiling_frame, ceiling, h_res, v_res, fov, level, size, ceiling_walls, 100, 100)

        # applies pixel array to surface
        floor_surface = pygame.transform.scale(
            pygame.surfarray.make_surface(floor_frame*255), (1066, 800))
        ceiling_surface = pygame.transform.scale(
            pygame.surfarray.make_surface(ceiling_frame*255), (1066, 800))

        # flips ceiling subsurface to mirror floor (wildly inefficient but works well enough for this)
        floor_subsurface = floor_surface.subsurface((0, 400, 1066, 400))
        ceiling_subsurface = ceiling_surface.subsurface((0, 400, 1066, 400))
        ceiling_subsurface = pygame.transform.flip(
            pygame.transform.rotate(ceiling_subsurface, 180), True, False)

        # draws onto screen
        screen.blit(floor_subsurface, (0, 300))
        screen.blit(ceiling_subsurface, (0, -100))

        # sort enemies by distance
        enemies_sorted = sorted(enemies, key=lambda en: numpy.sqrt(
            (en[0] - pos_x) ** 2 + (en[1] - pos_y) ** 2), reverse=True)
        if alive:
            # this whole current_time thing is kind of convoluted
            current_time = pygame.time.get_ticks()
            next_frame = False

            # if it's been 200 ms since last frame, update sprite frame
            if current_time - last_update > 200:

                # enemies increment thru sprites and then decrement 
                # back to original. this is probably way more complicated 
                # than it needs to be
                if sprite_frame >= 4:
                    sprite_frame -= 1
                    sprite_frame_dir = 1
                elif sprite_frame_dir == 0:
                    sprite_frame += 1
                elif sprite_frame <= 1:
                    sprite_frame -= 1
                    sprite_frame_dir = 0
                else:
                    sprite_frame -= 1
                
                # tells program to update sprite frame
                last_update = current_time
                next_frame = True

            # arguably even more convoluted than the above
            if current_time - last_update_sword > 40:
                if swinging:

                    # ends animation after 3 frames
                    if sword_frame >= 3:
                        sword_frame = 0
                        swinging = False
                    else:
                        sword_frame += 1
                last_update_sword = current_time

            if current_time - last_update_damage > 400:
                if in_enemy and alive:
                    damage_sound.play()
                    health = pygame.rect.Rect((225, health.top + 33, 15, health.height - 32))
                last_update_damage = current_time

            if health.height <= 0 and alive:
                death_sound.play()
                alive = False
                

            # moves enemies by adjusting their x,y coordinates
            enemies = move_enemies(enemies, level, size)

            # draws enemies, checks if mouse is over enemy, handles attacked enemies, and deals player damage
            # parameter hell
        
            over_enemy, enemies, in_enemy = draw_enemies(screen, enemies_sorted, pos_x, pos_y, rot, level, size,
                                            enemy_sprites, sprite_size, sprite_frame, next_frame,
                                            over_enemy, clicked)

            # character movement
            pos_x, pos_y, rot, moved = movement(
                    pos_x, pos_y, rot, pygame.key.get_pressed(), clock.tick(30), level, size)

            # play walking sfx while moving
            if moved and walk_sound.get_num_channels() < 1:
                walk_sound.play()

        # update mouse position
        cursor_rect.center = pygame.mouse.get_pos()
        cursor_sword_rect.center = pygame.mouse.get_pos()

        # depending on frame of sword, blit different position
        if sword_frame == 0:
            screen.blit(sprites_sword[0], (600, -200))
        elif sword_frame == 3:
            screen.blit(sprites_sword[3], (500, 0))
        else:
            screen.blit(sprites_sword[sword_frame], (200, 150))
        
        # draw onto screen
        screen.blit(ui_base, (0, 600))
        screen.blit(name_bg, (57, 628))
        screen.blit(name, (60, 628))
        pygame.draw.rect(screen, (48, 213, 19), fatigue)
        pygame.draw.rect(screen, (219, 20, 7), health)
        pygame.draw.rect(screen, (4, 3, 228), magicka)

        # if mouse is over UI, use sword cursor
        if pygame.mouse.get_pos()[1] > 600:
            screen.blit(cursor_sword, cursor_sword_rect)
        else:
            screen.blit(cursor, cursor_rect)

        # pushes new frame
        pygame.display.set_caption('The Elder Scrolls: Arena - FPS: ' + str(round(clock.get_fps(), 2)))
        pygame.display.update()


def menu(screen, running):

    # background, logo, and text
    paper = pygame.transform.scale(pygame.image.load(
        "./Assets/Menu/paper.jpg").convert(), (1066, 800))
    arena_logo = pygame.transform.scale(pygame.image.load(
        "./Assets/Menu/arena_logo.png"), (800, 200))
    font = pygame.font.Font('./Assets/Menu/MorrisRoman-Black.ttf', 60)
    prompt = font.render("What is your name?", False, (0, 0, 0))

    # background music and sfx
    pygame.mixer.music.load('./Assets/Audio/menu_music.mp3')
    pygame.mixer.music.play(-1)
    select_sound = pygame.mixer.Sound('./Assets/Audio/select.WAV')
    select_sound.set_volume(0.5)

    # user selected name
    name = ''

    while running:
        for event in pygame.event.get():
            # close window
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                # get list of keys pressed
                keys = pygame.key.get_pressed()

                # if room, backspace name
                if keys[pygame.K_BACKSPACE] and len(name) > 0:
                    name = name[:-1]

                # use regex to check for valid input - letters and spaces
                elif len(name) < 9 and re.search("[a-zA-Z ]", event.unicode):
                    select_sound.play()

                    # adds character to name
                    name += event.unicode

                # enter key starts game
                elif keys[pygame.K_RETURN] and len(name) > 0:
                    running = False

        # check for new name every frame
        input = font.render(name, False, (0, 0, 0))

        # this is really bad practice, but i'm too lazy to clear screen each time a
        # char is entered so i just redraw the whole menu ;-;
        screen.blit(paper, (0, 0))
        screen.blit(arena_logo, arena_logo.get_rect(center=(533, 250)))
        screen.blit(prompt, prompt.get_rect(center=(533, 500)))
        screen.blit(input, input.get_rect(center=(533, 600)))

        # pushes new frame
        pygame.display.update()

    return name


def movement(pos_x, pos_y, rot, keys, delta, level, size):
    
    # used to handle audio and other stuff in main loop
    moved = False

    # temp variables used to check for collisions after movement
    temp_x, temp_y = pos_x, pos_y

    # movement uses delta to stay framerate independent
    # turn left
    if keys[pygame.K_a]:
        rot -= 0.002 * delta

    # turn right
    if keys[pygame.K_d]:
        rot += 0.002 * delta

    # walk forward
    if keys[pygame.K_w]:
        temp_x, temp_y = pos_x + \
            numpy.cos(rot) * 0.002 * delta, pos_y + \
            numpy.sin(rot) * 0.002 * delta
        moved = True

    # walk backward
    if keys[pygame.K_s]:
        temp_x, temp_y = pos_x - \
            numpy.cos(rot) * 0.002 * delta, pos_y - \
            numpy.sin(rot) * 0.002 * delta
        moved = True

    if moved:

        # check for collisions
        if (keys[pygame.K_s] or keys[pygame.K_w]) and \
            level[int(temp_x) % (size - 1)][int(temp_y)% (size - 1)]:
                moved = False

        # no collisions, update position
        else:
            pos_x, pos_y = temp_x, temp_y

    return pos_x, pos_y, rot, moved


def get_sprites():

    # list of sprites used to animate them
    sprites_forward = []
    sprites_backward = []
    sprites_left = []
    sprites_right = []
    sprites_death = []
    sprites_sword = []

    # load enemy sprites (sideways is just flipped on y axis)
    for i in range(5):
        sprites_forward.append(pygame.transform.scale(pygame.image.load(
            "./Assets/Sprites/Enemy/Forward/" + str(i) + ".png"), (330, 500)))
        sprites_right.append(pygame.transform.scale(pygame.image.load(
            "./Assets/Sprites/Enemy/Sideways/" + str(i) + ".png"), (330, 500)))
        sprites_left.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(
            "./Assets/Sprites/Enemy/Sideways/" + str(i) + ".png"), (330, 500)), True, False))
        sprites_backward.append(pygame.transform.scale(pygame.image.load(
            "./Assets/Sprites/Enemy/Backward/" + str(i) + ".png"), (330, 500)))

    # standstill sword sprite, non-animated
    sprites_sword.append(pygame.transform.scale(pygame.image.load(
        "./Assets/Sprites/Sword/sword.png"), (800, 600)))
    sprites_sword[0] = pygame.transform.rotate(sprites_sword[0], 50)

    # load enemy death and sword attack sprites
    for i in range(3):
        sprites_death.append(pygame.transform.scale(pygame.image.load(
            "./Assets/Sprites/Enemy/Death/" + str(i) + ".png"), (330, 500)))
        sprites_sword.append(pygame.transform.scale(pygame.image.load(
            "./Assets/Sprites/Sword/" + str(i) + ".png"), (800, 600)))
        
    # collect sprites enemy sprites into single list
    enemy_sprites = [sprites_forward, sprites_backward,
                     sprites_left, sprites_right, sprites_death]
    
    # grab size of first enemy sprite (all the same size)
    sprite_size = numpy.asarray(enemy_sprites[0][0].get_size())

    # 2d array of enemy sprites and their animations, enemy sprite size, sword sprites
    return enemy_sprites, sprite_size, sprites_sword

def get_textures():

    # floor and ceiling textures
    floor = pygame.surfarray.array3d(
        pygame.image.load('./Assets/Environment/floor.png'))/255
    ceiling = pygame.surfarray.array3d(
        pygame.image.load('./Assets/Environment/ceiling.png'))/255

    # wall textures
    floor_walls = [pygame.surfarray.array3d(pygame.image.load('./Assets/Environment/wall.png'))/255,
                   pygame.surfarray.array3d(pygame.image.load('./Assets/Environment/wall_2.png'))/255,
                   pygame.surfarray.array3d(pygame.image.load('./Assets/Environment/wall_moss.png'))/255,
                   pygame.surfarray.array3d(pygame.image.load('./Assets/Environment/wall_moss_2.png'))/255,
                   pygame.surfarray.array3d(pygame.image.load('./Assets/Environment/wall_special.png'))/255]
    
    # these need to flip on the X axis because the ceiling is just upside down floor frame
    ceiling_walls = [pygame.surfarray.array3d(pygame.transform.flip(pygame.image.load('./Assets/Environment/wall.png'), False, True))/255,
                     pygame.surfarray.array3d(pygame.transform.flip(pygame.image.load('./Assets/Environment/wall_2.png'), False, True))/255,
                     pygame.surfarray.array3d(pygame.transform.flip(pygame.image.load('./Assets/Environment/wall_moss.png'), False, True))/255,
                     pygame.surfarray.array3d(pygame.transform.flip(pygame.image.load('./Assets/Environment/wall_moss_2.png'), False, True))/255,
                     pygame.surfarray.array3d(pygame.transform.flip(pygame.image.load('./Assets/Environment/wall_special.png'), False, True))/255]
    
    return floor, ceiling, floor_walls, ceiling_walls

def get_ui(name):

    # base ui image to add detail onto
    ui_base = pygame.transform.scale(pygame.image.load(
        "./Assets/HUD/UI_base.jpg").convert(), (1066, 200))
    
    # add a rectangle over default name to allow for inputted name
    name_bg = pygame.transform.scale(pygame.image.load(
        "./Assets/HUD/name_bg.png").convert(), (100, 27))
    
    # font and user inputted name
    sans = pygame.font.Font('./Assets/HUD/arena_font.ttf', 25)
    name = sans.render(name, False, (183, 124, 66))

    # status bars
    fatigue = pygame.rect.Rect((192, 680, 16, 98))
    health = pygame.rect.Rect((225, 680, 15, 98))
    magicka = pygame.rect.Rect((259, 680, 15, 98))

    return ui_base, name_bg, name, fatigue, health, magicka

def get_mouse():

    # makes system cursor invisible to allow cool custom cursor
    pygame.mouse.set_visible(False)

    # standard cursor 
    cursor = pygame.image.load('./Assets/HUD/cursor.png')
    cursor_rect = cursor.get_rect()

    # sword cursor when hovering over UI
    cursor_sword = pygame.image.load('./Assets/HUD/cursor_sword.png')
    cursor_sword_rect = cursor_sword.get_rect()

    return cursor, cursor_rect, cursor_sword, cursor_sword_rect

def get_sounds():
    # background music
    pygame.mixer.music.load('./Assets/Audio/dungeon_music.mp3')
    pygame.mixer.music.play(-1)

    # walking sfx
    walk_sound = pygame.mixer.Sound('./Assets/Audio/footstep.WAV')
    walk_sound.set_volume(0.5)

    # sword sfx
    sword_sound = pygame.mixer.Sound('./Assets/Audio/swoosh.wav')

    # player damage sfx
    damage_sound = pygame.mixer.Sound('./Assets/Audio/oof.wav')

    # player death sfx
    death_sound = pygame.mixer.Sound('./Assets/Audio/death.wav')

    return walk_sound, sword_sound, damage_sound, death_sound

def spawn_enemies(amount, level, size):

    # empty list to store enemies
    enemies = []

    # specified amount of enemies to spawn
    for i in range(amount):

        # choose random location for enemy
        x, y = numpy.random.uniform(
            1, size - 2), numpy.random.uniform(1, size - 2)
        
        # if position is invalid, choose a new random location
        while (level[int(x - 0.1) % (size - 1)][int(y - 0.1) % (size - 1)] or
               level[int(x - 0.1) % (size - 1)][int(y + 0.1) % (size - 1)] or
               level[int(x + 0.1) % (size - 1)][int(y - 0.1) % (size - 1)] or
               level[int(x + 0.1) % (size - 1)][int(y + 0.1) % (size - 1)]):
            x, y = numpy.random.uniform(
                1, size - 1), numpy.random.uniform(1, size - 1)
            
        # choose random direction and speed for enemy
        direction = numpy.random.choice(
            [0, numpy.pi/2, numpy.pi, 3*numpy.pi/2])
        speed = numpy.random.uniform(0.01, 0.03)

        # is enemy dead?
        dead = False

        # THIS IS DUMB, but other implementations are more complex. I should've
        # stored all the other frame data in the enemies too, but I am too far into
        # the project to change it now.
        death_frame = 0

        # append enemy to list
        enemies.append([x, y, direction, speed, dead, death_frame])

    return numpy.asarray(enemies)


def draw_enemies(screen, enemies, pos_x, pos_y, rot, level, size, enemy_sprites, sprite_size, frame, next_frame, over_enemy, clicked):

    # this is the most convoluted function i've ever written

    # sfx that don't belong in here
    enemy_death_sound = pygame.mixer.Sound("./Assets/Audio/fall.wav")
    hit_sound = pygame.mixer.Sound("./Assets/Audio/hit.wav")

    # boolean to make sure only one enemy is hit per swing. set to false when an enemy is hit
    # so every enemy rendered doesn't also die
    loop = True

    # boolean to check if player is in inside of an enemy
    in_enemy = False
    

    # loop through all enemies
    for i, en in enumerate(list(enemies)):
        # check if enemy is dead (more accurately if it's dying)
        dead = en[4]

        # get enemy position
        enx, eny = en[0], en[1]

        # get angle between enemy and player
        angle = numpy.arctan((eny-pos_y) / (enx - pos_x))

        # if enemy is behind player, flip angle
        if abs(pos_x + numpy.cos(angle)-enx) > abs(pos_x - enx):
            angle = (angle - numpy.pi) % (2 * numpy.pi)

        # get difference between enemy angle and player angle
        anglediff = (rot - angle) % (2 * numpy.pi)

        # draw enenmy if with in FOV
        if anglediff > 11 * numpy.pi / 6 or anglediff < numpy.pi / 6:
            # get distance of enemy
            distance = numpy.sqrt((pos_x - enx) ** 2 + (pos_y - eny) ** 2)

            # check if enemy is behind a wall
            behind = behind_wall(pos_x, pos_y, enx, eny, level, size)

            # if too close, set to true and don't draw (avoids weird clipping)
            if distance < 0.6 and not dead:
                in_enemy = True

            # if outside of fog, not behind a wall, and not too close, draw enemy
            if distance > 0.5 and distance < 3.5 and not behind:
                # fisheye correction
                cos2 = numpy.cos(anglediff)

                # scale enemy based on distance and angle
                scaling = min(1/distance, 2) / cos2
                vert = 300 + 400 * scaling - scaling * sprite_size[1]
                hor = 533 - 1066 * numpy.sin(anglediff) - scaling * sprite_size[0]/2

                if not dead:
                    # calculate enemy angle relative to player
                    true_angle = ((angle - en[2]) % (2 * numpy.pi))

                    # facing away from player
                    if true_angle >= numpy.pi / 4 and true_angle < 3 * numpy.pi / 4:
                        sprite_image = enemy_sprites[2][frame]

                    # facing towards player
                    elif true_angle >= 5 * numpy.pi / 4 and true_angle < 7 * numpy.pi / 4:
                        sprite_image = enemy_sprites[3][frame]

                    # facing toward the left
                    elif true_angle >= 3 * numpy.pi / 4 and true_angle < 5 * numpy.pi / 4:
                        sprite_image = enemy_sprites[0][frame]

                    # facing towards the right
                    elif true_angle > 7 * numpy.pi / 4 or true_angle < numpy.pi / 4:
                        sprite_image = enemy_sprites[1][frame]

                # if dead, play death animation
                else:
                    # animation is over, delete enemy from list
                    if en[5] >= 2:
                        sprite_image = enemy_sprites[4][2]
                        enemies = numpy.delete(enemies, i, axis=0)

                    # play death animation
                    else:
                        if next_frame:
                            en[5] += 1
                        sprite_image = enemy_sprites[4][int(en[5])]

                # push sprite to screen
                spsurf = pygame.transform.scale(
                    sprite_image, scaling * sprite_size)
                screen.blit(spsurf, (hor, vert))

                # check if mouse is over enemy
                sprite_rect = spsurf.get_rect()
                sprite_rect.x, sprite_rect.y = hor, vert
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # if mouse is over enemy in range, set over_enemy to true
                if sprite_rect.collidepoint(mouse_x, mouse_y) and distance < 1:
                    over_enemy = True
                    loop = False
                elif loop:
                    over_enemy = False

                # if enemy is clicked, kill it
                if over_enemy and clicked:
                    en[4] = True
                    enemy_death_sound.play()
                    hit_sound.play()

    return over_enemy, enemies, in_enemy


def move_enemies(enemies, level, size):
    for i, en in enumerate(list(enemies)):

        # if not dead
        if not en[4]:

            # get enemy x and y coordinates
            en_x, en_y = en[0], en[1]

            # get enemy direction and speed
            direction = en[2]
            speed = en[3]

            # randomly change direction if number is less than 0.01
            random_num = numpy.random.uniform()
            if random_num < 0.01:
                direction = numpy.random.choice([0, numpy.pi / 2, numpy.pi, 3 * numpy.pi / 2])

            # Restrict movement to four directions: forward, backward, left, and right
            if direction == 0:  
                dx, dy = speed, 0
            elif direction == numpy.pi / 2: 
                dx, dy = 0, speed
            elif direction == numpy.pi: 
                dx, dy = -speed, 0
            elif direction == 3 * numpy.pi / 2:
                dx, dy = 0, -speed
         
            # checks if new position will collide with wall, or is outside level bounds
            new_x, new_y = en_x + dx, en_y + dy
            if (not 0 < new_x < size - 1 or
                not 0 < new_y < size - 1 or
                level[int(new_x)][int(new_y)]):

                # if collision, reverse direction (and loop back to start of radian circle)
                direction = (numpy.pi + direction) % (2 * numpy.pi)

                # move player back to previous position
                dx = -dx
                dy = -dy
                new_x, new_y = en_x + dx, en_y + dy
            
            # update enemy position and direction
            enemies[i][0], enemies[i][1], enemies[i][2] = new_x, new_y, direction
    return enemies


@njit
def behind_wall(pos_x, pos_y, sprite_x, sprite_y, level, size):
    # calculate distance and angle to sprite
    dist = numpy.sqrt((pos_x - sprite_x) ** 2 + (pos_y - sprite_y) ** 2)
    angle = numpy.arctan2(sprite_y - pos_y, sprite_x - pos_x)

    # cast a ray towards the sprite
    x, y = pos_x, pos_y
    while True:
        x, y = x + 0.02 * numpy.cos(angle), y + 0.02 * numpy.sin(angle)
        if level[int(x) % (size - 1)][int(y % (size - 1))] > 0:
            # intersection with wall, sprite is behind wall
            return True
        if numpy.sqrt((x - pos_x) ** 2 + (y - pos_y) ** 2) >= dist:
            # reached sprite without intersecting any walls, sprite is visible
            return False


@njit
def new_frame(pos_x, pos_y, rot, frame, texture, h_res, v_res, fov, level, size, walls, x_dim, y_dim):
    for i in range(h_res):
        # calculates current camera rotation in radians
        rot_rad = rot + numpy.deg2rad(i / fov - 30)

        # takes sin and cos of camera rotation, and cos of the
        # fov in relation to the current pixel being scanned
        sin, cos, cos_fov = numpy.sin(rot_rad), numpy.cos(
            rot_rad), numpy.cos(numpy.deg2rad(i / fov - 30))

        # creates origin point of rays to cast
        x, y = pos_x, pos_y

        # casts rays until a wall is hit
        while level[int(x) % (size - 1)][int(y % (size - 1))] == 0:
            x, y = x + 0.02 * cos, y + 0.02 * sin

        # calculates which wall texture it should be rendering on current pixel
        num = level[int(x) % (size - 1)][int(y % (size - 1))]
        wall_texture = walls[num - 1]

        # distance between player and wall to be rendered
        distance = abs((x - pos_x) / cos)

        # height of current wall to be rendered
        height = int(v_res / ((distance * cos_fov) + 0.001))

        # current horizontal pixel on wall texture
        xx = int(x * x_dim) % x_dim

        # if too close to wall,
        if x % 1 < 0.02 or x % 1 > 0.98:
            xx = int(y * y_dim) % y_dim

        # array of coordinates to draw texture upwards
        yy = numpy.linspace(0, 99, height * 2)

        # used to add depth by dimming textures, only starts dimming when distance is > 2
        if distance > 2:
            shade_factor = min(1, (distance - 2) / 2)
            shade = (1 - shade_factor) + shade_factor * \
                (0.4 * (height / v_res))
        else:
            shade = 1

        # fixes crash when getting too close to walls
        if shade > 1:
            shade = 1

        # renders wall with texture and shading
        for k in range(height * 2):
            if v_res - height + k >= 0 and v_res - height + k < 2*v_res:
                frame[i][v_res - height + k] = shade * \
                    wall_texture[xx][int(yy[k])]

        # renders floor or ceiling texture (depending on which call we're in)
        for j in range(v_res - height):
            # calculates distance from player to floor or ceiling
            distance = (v_res / (v_res - j)) / cos_fov

            # current pixel on floor or ceiling texture
            x, y = pos_x + cos * distance, pos_y + sin * distance
            xx = int(x * (x_dim * (h_res / v_res))) % x_dim
            yy = int(y * (y_dim * (h_res / v_res))) % y_dim

            # used to add depth by dimming textures, only starts dimming when distance is > 2
            if distance > 2:

                # so dimming actually begins at 2, rather than jumps to where it would be at 2
                shade_factor = min(1, (distance - 2) / 2)
                shade = (1 - shade_factor) + shade_factor * \
                    (0.4 * (1 - j / v_res))
            else:
                shade = 1

            # applies shading and textures to floor and ceiling
            frame[i][v_res * 2 - j - 1] = shade * texture[xx][yy]
    return frame

# python pet peeve
if __name__ == '__main__':
    main()
    pygame.quit()
