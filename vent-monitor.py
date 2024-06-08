#!/usr/bin/env python3

import gpiod
import time
import argparse
import sys

VERSION = '1.0'
SLEEP_TIME = 5

def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
	parser.add_argument('--chip', dest='chip', required=True, help='gpio chip, see gpioinfo')
	parser.add_argument('--line', dest='line', required=True, type=int, help='gpio line, see gpioinfo')
	parser.add_argument('--temp-on', dest='tempOn', required=True, type=int, help='temperature to start fan')
	parser.add_argument('--temp-off', dest='tempOff', required=True, type=int, help='temperature to stop fan. Must be smaller than --temp-on')
	return parser.parse_args()

def readTemp():
	with open('/sys/class/thermal/thermal_zone0/temp') as file:
		return int(int(file.read()) / 1000)

args = parseArguments()
if args.tempOn <= args.tempOff:
	print("--temp-on must be greater than --temp-off", file=sys.stderr)
	sys.exit(1)

with gpiod.Chip(args.chip, gpiod.Chip.OPEN_BY_NAME) as chip:
	ventLine = chip.get_line(args.line)
	ventLine.request("FanManagement", gpiod.LINE_REQ_DIR_OUT)
	
	ventOn = None
	while True:
		curTemp = readTemp()
		if curTemp >= args.tempOn and ventOn != True:
			ventLine.set_value(1)
			ventOn = True
			print("Temperature is", curTemp, ". Fan enabled.")
		elif curTemp <= args.tempOff and ventOn != False:
			ventLine.set_value(0)
			ventOn = False
			print("Temperature is", curTemp, ". Fan disabled.")
		time.sleep(SLEEP_TIME)
