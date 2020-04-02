#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


import pygame, random, itertools, collections

from tetris_pieces import *
from tetris_config import *

#Definição da janela do jogo
pygame.init()
screen = pygame.display.set_mode((largura+info, altura))
pygame.display.set_caption('Tetris | score: 0 | lines: 0 | level: 0')
clock = pygame.time.Clock()
score = 0
lines_destroyed = 0
level = 0
last_level = 0
info_field = pygame.Surface((info, altura))
info_field.fill(color_info_background)

  
def get_new_piece(piece_set):
    if piece_set == 'classic':
        piece = random.randint(0,11)
        if piece in (0, 1): return T()
        elif piece in (2, 3): return L()
        elif piece in (4, 5): return J()
        elif piece in (6, 7): return S()
        elif piece in (8, 9): return Z()
        elif piece == 10: return I()
        elif piece == 11: return O()


game_field = np.zeros((numero_linhas, numero_colunas), dtype="int16")

def fix_on_game_field(piece_squares_list, game_field, fixed_squares, move_up=False, check_error=True):
    
    new_game_field = game_field.copy()
    new_fixed_squares = fixed_squares.copy()

    for square in piece_squares_list:
        idx_x = square.posicao[0] // escala
        idx_y = square.posicao[1] // escala
        new_game_field[idx_y, idx_x] = square.idx
        new_fixed_squares[square.idx] = square
    
    print(new_game_field)
    print(new_fixed_squares.keys())

    return new_game_field, new_fixed_squares


def line_check(game_field, numero_linhas, fixed_squares, escala):
    n = numero_linhas
    n -= 1
    lines_destroyed = 0
    new_fixed_squares = fixed_squares.copy()

    if not (game_field[n,:] > 0).any():
        return game_field, fixed_squares
    
    else:
        if game_field[n,:].all():
            for idx in game_field[n,:].flatten():
                if new_fixed_squares.get(idx):
                    del(new_fixed_squares[idx])

            upper_mask = game_field[:n,:] > 0
            for idx in game_field[:n,:][upper_mask].flatten():
                new_fixed_squares[idx].posicao = (new_fixed_squares[idx].posicao[0], new_fixed_squares[idx].posicao[1] + escala)
                new_fixed_squares[idx].posicao_x = new_fixed_squares[idx].posicao[0]
                new_fixed_squares[idx].posicao_y = new_fixed_squares[idx].posicao[1] + escala

            new_first_line = np.zeros((1, numero_colunas), dtype='int16')
            new_game_field = np.vstack((new_first_line, game_field[:n,:], game_field[n+1:,:]))
            lines_destroyed += 1
            return line_check(new_game_field, n, new_fixed_squares, escala)
        return line_check(game_field, n, new_fixed_squares, escala)
        


def level_check(score):
    steps = list(range(0,1001,50))
    steps_idx = len(steps)-2
    while steps_idx:
        if score < steps[steps_idx+1] and score >= steps[steps_idx]:
            return steps_idx+1
        steps_idx -= 1
    return 0



fixed_squares = {}
falling_piece = get_new_piece('classic')
falling_piece.push_to_game()
next_piece = get_new_piece('classic')

#Variáveis globais
font = pygame.font.Font('freesansbold.ttf', 18)
game_speed = init_game_speed
game_over = False
restart = False
game_set = 'classic'

while True:
    if not game_over:
        clock.tick(game_speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    falling_piece.rotate('sentido horário', fixed_squares)
                elif event.key == pygame.K_SPACE:
                    falling_piece.rotate('sentido anti-horário', fixed_squares)
                    falling_piece.criate_sprite()
                elif event.key == pygame.K_DOWN:
                    falling_piece.fall_faster()
                elif event.key == pygame.K_LEFT:
                    falling_piece.move('esquerda', fixed_squares)
                elif event.key == pygame.K_RIGHT:
                    falling_piece.move('direita', fixed_squares)
               
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        ### Movendo a peça para baixo (regras de colisão no objeto)
        still_falling = falling_piece.fall(fixed_squares, game_field, escala)

        if not still_falling:
            game_field, fixed_squares = fix_on_game_field(falling_piece.sprite, game_field, fixed_squares)
            game_field, fixed_squares = line_check(game_field, numero_linhas, fixed_squares, escala)

            falling_piece = next_piece
            falling_piece.push_to_game()
            next_piece = get_new_piece(game_set)

            '''
            num_of_lines_destroyed = 0

            
            if num_of_lines_destroyed > 0:
                lines_destroyed += num_of_lines_destroyed
                score += num_of_lines_destroyed ** 3
                level = level_check(score)
                if level > last_level:
                    dif = level - last_level
                    last_level = level
                    game_speed += dif*4 
            '''        
                

        ### Limpa a tela para redesenhar os objetos
        screen.fill(color_background)
        screen.blit(info_field, (largura, 0))

        # Desenha a grade 
        for x in range(0, largura, escala):
            pygame.draw.line(screen, cinza, (x, 0), (x, altura))
        for y in range(0, altura, escala):
            pygame.draw.line(screen, cinza, (0, y), (largura, y))        
        
  
        ### Desenhando objetos 
        pygame.display.set_caption('Tetris | score: {} | lines: {} | level: {}'.format(score, lines_destroyed, level))

        for square in falling_piece.sprite:
            screen.blit(square.pele, square.posicao)
        for idx in fixed_squares.keys():
            screen.blit(fixed_squares[idx].pele, fixed_squares[idx].posicao)
        for square in next_piece.sprite:
            screen.blit(square.pele, square.posicao)
        

        pygame.display.update()
    
    else:
        ### Limpa a tela para redesenhar os objetos
        screen.fill(color_background)
        clock.tick(10)
        game_over_font_size = largura // (escala // 4) 
        game_over_font = pygame.font.Font('freesansbold.ttf', game_over_font_size)
        game_over_screen = game_over_font.render('Fim de jogo!', True, verde)
        restart_font_size = largura // int(escala // 1.4 )
        restart_font = pygame.font.Font('freesansbold.ttf', restart_font_size)
        restart_screen = restart_font.render('F2 para recomeçar,  ESC para sair...', True, verde)
        game_over_rect = game_over_screen.get_rect()
        game_over_rect.midtop = ((largura + info) / 2, (altura / 2) - escala * 5)
        restart_rect = restart_screen.get_rect() 
        restart_rect.midtop = ((largura + info) / 2, escala * 2 + (altura / 2))
        screen.blit(game_over_screen, game_over_rect)
        screen.blit(restart_screen, restart_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    restart = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()


        if restart:
            game_over = False
            restart = False
            game_speed = init_game_speed
            score = 0
            lines_destroyed = 0
            score = 0
            level = 0
            fixed_squares_map = collections.Counter()
            fixed_squares = []
            falling_piece = get_new_piece('classic')
            falling_piece.push_to_game()
            next_piece = get_new_piece('classic')


        
        pygame.display.update()