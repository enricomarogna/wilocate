# -*- coding: utf-8 -*-

force_log = True

def log(lvl = 1, *args):
  if lvl>0 or force_log:
    print (' '.join(map(str, args)))