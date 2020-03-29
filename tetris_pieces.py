#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#

import pygame, itertools

from tetris_config import *

class BaseSquare:
    def __init__(self, cor, init_pos, relative_x, relative_y):
        self.posicao_x = init_pos[0] + (escala * relative_x)
        self.posicao_y = init_pos[1] + (escala * relative_y)
        self.posicao = (self.posicao_x, self.posicao_y)
        self.pele = pygame.Surface((escala, escala))
        self.pele.fill(cor)

    def check_colision(self, fixed_squares):
        for element in fixed_squares:
            if self.posicao_x == element.posicao_x and self.posicao_y + escala == element.posicao_y:
                return True

    def check_flor_colision(self):
        if self.posicao_y >= altura - escala:
            return True
        return False

    def check_left_wall_colision(self):
        if self.posicao_x - escala < 0:
            return True
        return False
    
    def check_right_wall_colision(self):
        if self.posicao_x + escala == largura:
            return True
        return False

    def check_transpassing_right_wall(self):
        if self.posicao_x == largura:
            return True
        return False

    def check_transpassing_left_wall(self):
        if self.posicao_x < 0:
            return True
        return False



class TetrisPiece:
    def __init__(self, cor, next_piece=True):
        self.posicao = ((largura + (escala * 5) // 4, escala * 2))
        self.shape = [[[1]]]
        self.sprite = []
        self.color = cor
        self.min_steps = 5
        self.max_steps = 20
        self.min_image_index = 0
        self.max_image_index = 0
        self.image_index = 0
        self.fall_delay_max_steps = 36
        self.fall_steps = 0
        self.stop_fall = False
        self.step_size = escala * 1
    
    def criate_sprite(self):
        if self.shape == False:
            pass
        else:
            self.sprite = []
            relative_y_counter = itertools.count(0)
            for line in self.shape[self.image_index]:
                relative_y = next(relative_y_counter)
                relative_x_counter = itertools.count(0)
                for col in line:
                    relative_x = next(relative_x_counter)
                    if col:
                        self.sprite.append(BaseSquare(self.color, self.posicao, relative_x, relative_y))
            self.sprite.reverse()

    def push_to_game(self):
        self.posicao = ((largura // 2), 0)
        self.criate_sprite()

    def fall(self, fixed_squares):
        if self.stop_fall:
            pass
        else:
            self.fall_steps += 1
            if self.fall_steps >= self.fall_delay_max_steps:
                self.fall_steps = 0

                for squares in self.sprite:
                    if squares.check_flor_colision() or squares.check_colision(fixed_squares):
                        self.stop_fall = True
                        return False

                if not self.stop_fall:
                    self.posicao = (self.posicao[0], self.posicao[1] + escala)
                    for squares in self.sprite:
                        squares.posicao_y += escala
                        squares.posicao = (squares.posicao_x, squares.posicao_y)
            return True
        
    
    def fall_faster(self):
        self.fall_delay_max_steps = 0

    def move(self, side):
        if side == 'esquerda':
            for squares in self.sprite:
                if squares.check_left_wall_colision():
                    return False

            for squares in self.sprite:
                squares.posicao_x -= escala
                squares.posicao = (squares.posicao_x, squares.posicao_y)
            self.posicao = (self.posicao[0] - escala, self.posicao[1])
            
        elif side == 'direita':
            for squares in self.sprite:
                if squares.check_right_wall_colision():
                    return False

            for squares in self.sprite:
                squares.posicao_x += escala
                squares.posicao = (squares.posicao_x, squares.posicao_y)
            self.posicao = (self.posicao[0] + escala, self.posicao[1])
        return True
    
    def rotate(self, sentido):
        if sentido == 'sentido horário':
            self.image_index += 1
            if self.image_index > self.max_image_index:
                self.image_index = 0

        elif sentido == 'sentido anti-horário':
            self.image_index -= 1
            if self.image_index < self.min_image_index:
                self.image_index = self.max_image_index

        self.criate_sprite()

        for squares in self.sprite:
            if squares.check_transpassing_left_wall():
                self.move('direita')
            if squares.check_transpassing_right_wall():
                self.move('esquerda')

    


class Square(TetrisPiece):
    def __init__(self):
        super(Square, self).__init__(azul)
        self.shape = [
            [[1,1],
             [1,1]]
        ]
        self.min_image_index = 0
        self.max_image_index = 0
        self.image_index = 0
        self.criate_sprite()


class I(TetrisPiece):
    def __init__(self):
        super(I, self).__init__(verde_marinho)
        self.shape = [
            [[0,1,0,0],
             [0,1,0,0],
             [0,1,0,0],            
             [0,1,0,0]],

            [[0,0,0,0],
             [1,1,1,1],
             [0,0,0,0],            
             [0,0,0,0]],
        ]
        self.min_image_index = 0
        self.max_image_index = 1
        self.image_index = 0
        self.criate_sprite()



class T(TetrisPiece):
    def __init__(self):
        super(T, self).__init__(verde)
        self.shape = [
            [[0,1,0],
             [1,1,1],
             [0,0,0]],

            [[0,1,0],
             [0,1,1],
             [0,1,0]],            

            [[0,0,0],
             [1,1,1],
             [0,1,0]],

            [[0,1,0],
             [1,1,0],
             [0,1,0]],
        ]
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()

class L(TetrisPiece):
    def __init__(self):
        super(L, self).__init__(marrom)
        self.shape = [
            [[0,1,0],
             [0,1,0],
             [0,1,1]],

            [[0,0,0],
             [1,1,1],
             [1,0,0]],            

            [[1,1,0],
             [0,1,0],
             [0,1,0]],

            [[0,0,1],
             [1,1,1],
             [0,0,0]],
        ]
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()


class S(TetrisPiece):
    def __init__(self):
        super(S, self).__init__(vermelho)
        self.shape =[
            [[0,1,1],
             [1,1,0],
             [0,0,0]],

            [[1,0,0],
             [1,1,0],
             [0,1,0]],            
        ]
        self.min_image_index = 0
        self.max_image_index = 1
        self.image_index = 0
        self.criate_sprite()


class U(TetrisPiece):
    def __init__(self):
        super(U, self).__init__(branco)
        self.shape =[
            [[1,0,1],
             [1,1,1],
             [0,0,0]],

            [[0,1,1],
             [0,1,0],
             [0,1,1]],            

            [[0,0,0],
             [1,1,1],
             [1,0,1]],

            [[1,1,0],
             [0,1,0],
             [1,1,0]],
        ]
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()


class L_reversed(TetrisPiece):
    def __init__(self):
        super(L_reversed, self).__init__(violeta)
        self.shape = [
            [[0,1,0],
             [0,1,0],
             [1,1,0]],

            [[1,0,0],
             [1,1,1],
             [0,0,0]],            

            [[0,1,1],
             [0,1,0],
             [0,1,0]],

            [[0,0,0],
             [1,1,1],
             [0,0,1]],
        ]
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()


class Z(TetrisPiece):
    def __init__(self):
        super(Z, self).__init__(cinza_claro)
        self.shape =[
            [[1,1,0],
             [0,1,1],
             [0,0,0]],

            [[0,1,0],
             [1,1,0],
             [1,0,0]],            
        ]
        self.min_image_index = 0
        self.max_image_index = 1
        self.image_index = 0
        self.criate_sprite()