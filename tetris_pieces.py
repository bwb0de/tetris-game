#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#

import pygame, itertools
import numpy as np
import itertools

from tetris_config import *

square_count = itertools.count()

def x_pos_matrix(arr, escala):
    counter = itertools.count()
    a = arr.copy()
    while True:
        idx = next(counter)
        x_val = idx*escala
        try: 
            a_mask = a[:,idx] > 0
            a[:,idx][a_mask] = x_val
        except IndexError: 
            break
    return a


def y_pos_matrix(arr, escala):
    counter = itertools.count()
    a = arr.copy()
    while True:
        idx = next(counter)
        y_val = idx*escala
        try: 
            a_mask = a[idx,:] > 0
            a[idx,:][a_mask] = y_val
        except IndexError: 
            break
    return a            

def vector_pos(arr, escala):
    x = x_pos_matrix(arr.copy(), escala)
    y = y_pos_matrix(arr.copy(), escala)
    counter = itertools.count()
    
    while True:
        try:
            x_pos = next(counter)
            line = np.vstack((arr[x_pos,:], x[x_pos,:], y[x_pos,:]))
            yield line
        except IndexError:
            break

def select_valid_vectors(arr, escala):
    vectors = vector_pos(arr, escala)
    for v in vectors:
        if v.any():
            v_mask = v[0] > 0
            v_out = np.vstack((v[1][v_mask], v[2][v_mask]))
            yield v_out

def return_vector(arr, escala):
    vectors = select_valid_vectors(arr, escala)
    for v_line in vectors:
        counter = itertools.count()
        while True:
            try: yield v_line[:,next(counter)]
            except IndexError: break




class BaseSquare:
    def __init__(self, cor, init_pos, relative_x, relative_y):
        self.idx = next(square_count)
        self.posicao_x = init_pos[0] + relative_x
        self.posicao_y = init_pos[1] + relative_y
        self.posicao = (self.posicao_x, self.posicao_y)
        self.pele = pygame.Surface((escala, escala))
        self.pele.fill(cor)

    def check_colision(self, fixed_squares):
        for idx in fixed_squares.keys():
            if self.posicao_x == fixed_squares[idx].posicao_x and self.posicao_y + escala >= fixed_squares[idx].posicao_y:
                return True

    def check_flor_colision(self):
        if self.posicao_y >= altura - escala:
            return True
        return False

    def check_left_square_colision(self, fixed_squares):
        for idx in fixed_squares.keys():
            if self.posicao_x - escala == fixed_squares[idx].posicao_x and self.posicao_y == fixed_squares[idx].posicao_y:
                return True
        return False

    def check_right_square_colision(self, fixed_squares):
        for idx in fixed_squares.keys():
            if self.posicao_x + escala == fixed_squares[idx].posicao_x and self.posicao_y == fixed_squares[idx].posicao_y:
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
        self.sprite = []
        valid_vectors = return_vector(self.shape[self.image_index], escala)

        for valid_vector in valid_vectors:
            relative_x = valid_vector[0]
            relative_y = valid_vector[1]
            self.sprite.append(BaseSquare(self.color, self.posicao, relative_x, relative_y))
        self.sprite.reverse()

    def check_colision(self, game_field, escala):
        result = []
        for square in self.sprite:
            idx_x = square.posicao[0] // escala
            idx_y = (square.posicao[1] + escala) // escala
            print(game_field[idx_x, idx_y])
            if game_field[idx_y, idx_x] != 0: result.append(True)
            else: result.append(False)

        return any(result)

    def push_to_game(self):
        self.posicao = ((largura // 2) - escala, -2*escala)
        self.criate_sprite()

    def fall(self, fixed_squares, game_field, escala):
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

    def get_squares_position(self):
        for square in self.sprite:
            yield square.posicao

    def move(self, side, fixed_squares):
        if side == 'esquerda':
            for squares in self.sprite:
                if squares.check_left_wall_colision():
                    return False
                elif squares.check_left_square_colision(fixed_squares):
                    return False


            for squares in self.sprite:
                squares.posicao_x -= escala
                squares.posicao = (squares.posicao_x, squares.posicao_y)
            self.posicao = (self.posicao[0] - escala, self.posicao[1])
            
        elif side == 'direita':
            for squares in self.sprite:
                if squares.check_right_wall_colision():
                    return False
                elif squares.check_right_square_colision(fixed_squares):
                    return False


            for squares in self.sprite:
                squares.posicao_x += escala
                squares.posicao = (squares.posicao_x, squares.posicao_y)
            self.posicao = (self.posicao[0] + escala, self.posicao[1])
        return True
    
    def rotate(self, sentido, fixed_squares):
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
                self.move('direita', fixed_squares)
            if squares.check_transpassing_right_wall():
                self.move('esquerda', fixed_squares)

    


class O(TetrisPiece):
    def __init__(self):
        super(O, self).__init__(azul)
        self.shape = np.array([
            [[1,1],
             [1,1]]
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 0
        self.image_index = 0
        self.criate_sprite()


class I(TetrisPiece):
    def __init__(self):
        super(I, self).__init__(verde_marinho)
        self.shape = np.array([
            [[0,1,0,0],
             [0,1,0,0],
             [0,1,0,0],            
             [0,1,0,0]],

            [[0,0,0,0],
             [1,1,1,1],
             [0,0,0,0],            
             [0,0,0,0]],
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 1
        self.image_index = 0
        self.criate_sprite()



class T(TetrisPiece):
    def __init__(self):
        super(T, self).__init__(verde)
        self.shape = np.array([
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
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()

class L(TetrisPiece):
    def __init__(self):
        super(L, self).__init__(marrom)
        self.shape = np.array([
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
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()


class S(TetrisPiece):
    def __init__(self):
        super(S, self).__init__(vermelho)
        self.shape = np.array([
            [[0,1,1],
             [1,1,0],
             [0,0,0]],

            [[1,0,0],
             [1,1,0],
             [0,1,0]],            
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 1
        self.image_index = 0
        self.criate_sprite()


class U(TetrisPiece):
    def __init__(self):
        super(U, self).__init__(branco)
        self.shape = np.array([
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
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()


class J(TetrisPiece):
    def __init__(self):
        super(J, self).__init__(violeta)
        self.shape = np.array([
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
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 3
        self.image_index = 0
        self.criate_sprite()


class Z(TetrisPiece):
    def __init__(self):
        super(Z, self).__init__(cinza_claro)
        self.shape = np.array([
            [[1,1,0],
             [0,1,1],
             [0,0,0]],

            [[0,1,0],
             [1,1,0],
             [1,0,0]],            
        ], dtype='int8')
        self.min_image_index = 0
        self.max_image_index = 1
        self.image_index = 0
        self.criate_sprite()