#!/usr/bin/python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))
from common.entity.entities import Type

if __name__ == '__main__':
    for i in range(1,25):
        if i == 21:
            # Fontes das  LT
            print(u'10.128.{0}.101 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.102 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.103 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.104 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))

        elif i == 22:
            # Sala de Conectividade
            pass
        elif i == 23:
            # Sala de Fontes
            print(u'10.128.{0}.101 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.102 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.103 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.104 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.105 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.106 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))

        elif i == 24:
            # Sala de Fontes
            pass

        else:
            print(u'10.128.{0}.101 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.MKS937B).code))
            print(u'10.128.{0}.102 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.AGILENT4UHV).code))
            print(u'10.128.{0}.103 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.AGILENT4UHV).code))
            print(u'10.128.{0}.104 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.105 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.POWER_SUPPLY).code))
            print(u'10.128.{0}.106 10.128.{0}.0/24 {1}'.format(i+100,Type(code=Type.MBTEMP).code))

        if i == 1:
            # EPP
            print(u'10.128.101.107 10.128.101.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.101.108 10.128.101.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.101.109 10.128.101.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.101.110 10.128.101.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.101.111 10.128.101.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.101.112 10.128.101.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.101.113 10.128.101.0/24 {}'.format(Type.SPIXCONV))
        if i == 20:
            # EPP
            print(u'10.128.120.107 10.128.120.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.120.108 10.128.120.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.120.109 10.128.120.0/24 {}'.format(Type.SPIXCONV))
            print(u'10.128.120.110 10.128.120.0/24 {}'.format(Type.SPIXCONV))