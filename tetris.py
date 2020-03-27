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
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
score = 0
lines_destroyed = 0
level = 0
info_field = pygame.Surface((info, altura))
info_field.fill(color_info_background)

  
def get_new_piece(piece_set):
    if piece_set == 'classic':
        piece = random.randint(0,11)
        if piece in (0, 1): return T()
        elif piece in (2, 3): return L()
        elif piece in (4, 5): return L_reversed()
        elif piece in (6, 7): return S()
        elif piece in (8, 9): return Z()
        elif piece == 10: return I()
        elif piece == 11: return Square()

def line_check(fixed_squares, fixed_squares_map):
    lines = list(range(0, altura+1, escala))
    lines.reverse()
    num_of_lines_destroyed = 0
    for line_val in lines:
        if fixed_squares_map.get(line_val):
            if fixed_squares_map[line_val] >= numero_colunas:
                num_of_lines_destroyed += 1
                fixed_squares_map[line_val] -= numero_colunas
    return num_of_lines_destroyed
    

def level_check(score):
    steps = list(range(0,1001,100))
    steps_idx = len(steps)-2
    while steps_idx:
        if score < steps[steps_idx+1] and score >= steps[steps_idx]:
            return steps_idx+1
        steps_idx -= 1
    return 0



fixed_squares_map = collections.Counter()
fixed_squares = []
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
                    falling_piece.rotate('sentido horário')
                elif event.key == pygame.K_SPACE:
                    falling_piece.rotate('sentido anti-horário')
                    falling_piece.criate_sprite()
                elif event.key == pygame.K_DOWN:
                    falling_piece.fall_faster()
                elif event.key == pygame.K_LEFT:
                    falling_piece.move('esquerda')
                elif event.key == pygame.K_RIGHT:
                    falling_piece.move('direita')
               
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        ### Movendo a peça para baixo (regras de colisão no objeto)
        still_falling = falling_piece.fall(fixed_squares)

        if not still_falling:
            for square in falling_piece.sprite:
                fixed_squares.append(square)
                fixed_squares_map.update([square.posicao_y])
            falling_piece = next_piece
            falling_piece.push_to_game()
            next_piece = get_new_piece(game_set)
            num_of_lines_destroyed = line_check(fixed_squares, fixed_squares_map)
            
            if num_of_lines_destroyed > 0:
                lines_destroyed += num_of_lines_destroyed
                score += num_of_lines_destroyed ** num_of_lines_destroyed
                level = level_check(score)

        ### Limpa a tela para redesenhar os objetos
        screen.fill(color_background)
        screen.blit(info_field, (largura, 0))
        
  
        ### Desenhando objetos 
        pygame.display.set_caption('Tetris | score: {} | lines: {} | level: {}'.format(score, lines_destroyed, level))

        for square in falling_piece.sprite:
            screen.blit(square.pele, square.posicao)
        for square in fixed_squares:
            screen.blit(square.pele, square.posicao)
        for square in next_piece.sprite:
            screen.blit(square.pele, square.posicao)
        

        pygame.display.update()
    
    else:
        ### Limpa a tela para redesenhar os objetos
        screen.fill(color_background)
        clock.tick(10)
        game_over_font = pygame.font.Font('freesansbold.ttf', largura // 10)
        game_over_screen = game_over_font.render('Fim de jogo!', True, verde)
        restart_font = pygame.font.Font('freesansbold.ttf', largura // 25)
        restart_screen = restart_font.render('F2 para recomeçar,  ESC para sair...', True, verde)
        game_over_rect = game_over_screen.get_rect()
        game_over_rect.midtop = (largura / 2, (altura / 2) - escala * 5)
        restart_rect = restart_screen.get_rect() 
        restart_rect.midtop = (largura / 2, escala * 2 + (altura / 2))
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
        
        pygame.display.update()