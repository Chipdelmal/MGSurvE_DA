#!/usr/bin/env python
# -*- coding: utf-8 -*-

KMS_PER_RADIAN = 6371.0088

###############################################################################
# Available cluster colors
###############################################################################
# RCOLORS = ('#f72585', '#b5e48c', '#4361ee', '#eeeeee', '#f8f32b', '#f80000')
RCOLORS = (
    '#b5e48c', '#4361ee', '#9b287b', '#ff6b6b', '#f72585',
    '#f80000', '#457b9d', '#8d99ae', '#80ed99', '#ff99c8'
)
CLUSTER_PALETTE= [
    '#f72585', '#b5179e', '#7209b7', '#560bad', '#3a0ca3',
    '#3f37c9', '#4361ee', '#4895ef', '#4cc9f0', '#80ed99',
    '#b8f2e6', '#e9ff70', '#fe6d73', '#ffc6ff', '#ffd670',
    '#a1b5d8', '#9e0059', '#f88dad', '#dfdfdf', '#ffeedd',
    '#d7e3fc', '#ef233c', '#eac4d5', '#04e762', '#ca7df9',
    '#ffff3f', '#edc4b3', '#fe5d9f', '#639fab', '#9cbfa7'
]
CLUSTER_PALETTE_MAPPED = {
    '#f72585', '#b5179e', '#7209b7', '#560bad', 
    '#3a0ca3', '#3f37c9', '#4361ee', '#4895ef', 
    '#4cc9f0', '#80ed99', '#b8f2e6', '#e9ff70', 
    '#fe6d73', '#ffc6ff', '#ffd670', '#a1b5d8', 
    '#9e0059', '#f88dad', '#dfdfdf', '#ffeedd',
    '#d7e3fc', '#ef233c', '#eac4d5', '#04e762', 
    '#ca7df9', '#ffff3f', '#edc4b3', '#fe5d9f', 
    '#639fab', '#9cbfa7'   
}

RCOLORS = (
    '#02AD9A', '#B36FA0', '#E16D5D', '#E84E73', '#C8C4E4', 
    '#89C074', '#6F566B', '#FF9293', '#1541AE', '#9DB4AF'
)

# CLUSTER_PALETTE = (
#     '#8AA7AB', '#F1DDC0', '#EDA543', '#C25F7B', '#3B8863', '#3C62A8'
# )

###############################################################################
# Map Style A
###############################################################################
STYLE_GD_A = {'color': '#8da9c4', 'alpha': 0.5, 'width': 0.5, 'step': 0.01, 'range': 1, 'style': ':'}
STYLE_BG_A = {'color': '#0b2545'}
STYLE_TX_A = {'color': '#faf9f9', 'size': 40}
STYLE_CN_A = {'color': '#faf9f9', 'alpha': 0.20, 'size': 200}
STYLE_BD_A = {'color': '#faf9f9', 'alpha': 0.900}
STYLE_RD_A = {'color': '#ede0d4', 'alpha': 0.125, 'width': 1.5}
MAP_STYLE_A = (
    STYLE_GD_A, STYLE_BG_A, STYLE_TX_A, STYLE_CN_A, STYLE_BD_A, STYLE_RD_A
)

###############################################################################
# Map Style B
###############################################################################
STYLE_GD_B = {'color': '#8da9c4', 'alpha': 0.35, 'width': 0.5, 'step': 0.01, 'range': 1, 'style': ':'}
STYLE_BG_B = {'color': '#ffffff'}
STYLE_TX_B = {'color': '#cae9ff', 'size': 40}
STYLE_CN_B = {'color': '#3d405b', 'alpha': 0.20, 'size': 200}
STYLE_BD_B = {'color': '#3d405b', 'alpha': 0.900}
STYLE_RD_B = {'color': '#3d405b', 'alpha': 0.025, 'width': 1.25}
MAP_STYLE_B = (
    STYLE_GD_B, STYLE_BG_B, STYLE_TX_B, STYLE_CN_B, STYLE_BD_B, STYLE_RD_B
)
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = MAP_STYLE_B

###############################################################################
# Map Style C
###############################################################################
STYLE_GD_C = {'color': '#8da9c4', 'alpha': 0.35, 'width': 0.5, 'step': 0.01, 'range': 1, 'style': ':'}
STYLE_BG_C = {'color': '#FFFFFF'}
STYLE_TX_C = {'color': '#3d405b', 'size': 40}
STYLE_CN_C = {'color': '#3d405b', 'alpha': 0.20, 'size': 200}
STYLE_BD_C = {'color': '#304c89', 'alpha': 0.30}
STYLE_RD_C = {'color': '#292f36', 'alpha': 0.5, 'width': 0.25}
MAP_STYLE_C = (
    STYLE_GD_C, STYLE_BG_C, STYLE_TX_C, STYLE_CN_C, STYLE_BD_C, STYLE_RD_C
)

###############################################################################
# Map Style D
###############################################################################
STYLE_GD_D = {'color': '#9BBFCE', 'alpha': 0.5, 'width': 0.5, 'step': 0.01, 'range': 1, 'style': ':'}
STYLE_BG_D = {'color': '#F0E6D9'}
STYLE_TX_D = {'color': '#faf9f9', 'size': 40}
STYLE_CN_D = {'color': '#faf9f9', 'alpha': 0.20, 'size': 200}
STYLE_BD_D = {'color': '#75393E', 'alpha': 0.250}
STYLE_RD_D = {'color': '#58586B', 'alpha': 0.150, 'width': 0.75}
MAP_STYLE_D = (
    STYLE_GD_D, STYLE_BG_D, STYLE_TX_D, STYLE_CN_D, STYLE_BD_D, STYLE_RD_D
)