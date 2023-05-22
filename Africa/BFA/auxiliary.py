#!/usr/bin/env python
# -*- coding: utf-8 -*-

def userPaths(user):
    if user=='sami':
        (DTA_ROOT, SIM_ROOT) = (
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_show/', 
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_show/'
        )
    return {'data': DTA_ROOT, 'sim': SIM_ROOT}