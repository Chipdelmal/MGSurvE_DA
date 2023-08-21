#!/usr/bin/env python
# -*- coding: utf-8 -*-

JOBS = 8
KMS_PER_RADIAN = 6371.0088
(IX_SPLIT, NOT_ACCESSIBLE) = (27, [51, 239])
SAO_LIMITS = ((6.41, 6.79), (-0.0475, .45))
EXP_ID = 'STC'
PATHS = {
    'data': './DTA', 
    'geo': './GEO', 
    'optimization': './OPT'
}

CLUSTER_PALETTE= [
    '#f72585', '#b5179e', '#7209b7', '#560bad', '#3a0ca3',
    '#3f37c9', '#4361ee', '#4895ef', '#4cc9f0', '#80ed99',
    '#b8f2e6', '#e9ff70', '#fe6d73', '#ffc6ff', '#ffd670',
    '#a1b5d8', '#9e0059', '#f88dad', '#dfdfdf', '#ffeedd',
    '#d7e3fc', '#ef233c', '#eac4d5', '#04e762', '#ca7df9',
    '#ffff3f', '#edc4b3', '#fe5d9f', '#639fab', '#9cbfa7'
]