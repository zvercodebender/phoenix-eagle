#!/usr/bin/python

import os
import json
import getopt
import sys
import signal
import time 
import logging
import piplates.RELAYplate as RELAY
import eaglelog

#--------------------------------------------------------------------------------------
def signal_handler( signal, frame ):
    global ppADDR
    print('You pressed Ctrl-C!')
    logger.critical('Caught signal.... Exiting')
    RELAY.RESET( ppADDR )
    sys.exit(0)
# End signal_handler

#--------------------------------------------------------------------------------------
def readFile( fileName ):
   with open( fileName ) as infile:
      x = json.load( infile )
   infile.close()
   return x
# End readFile

#--------------------------------------------------------------------------------------
def writeFile( fileName, data ):
   with open( fileName, 'w' ) as outfile:
      json.dump( data, outfile )
   outfile.close()
# End writeFile

#--------------------------------------------------------------------------------------
def toggleBankState( switch ):
   global ppADDR
   swArray = [0,0,0,0,0,0,0]
   switch['state'] = 'ON'
   logger.info( "Setting %s = %s" % ( switch['name'], switch['state'] ) )
   for DO in switch['DOList']:
      logger.debug("  > Turn ON  DO %s " % DO )
      swArray[ DO - 1] = 1
   # End for
   bitStr = "%s%s%s%s%s%s%s" % (swArray[6], swArray[5], swArray[4], swArray[3], swArray[2], swArray[1], swArray[0] )
   logger.debug( " > Setting all bits %s " % bitStr )
   sw = int( bitStr, 2 )
   RELAY.relayALL( ppADDR, sw )
   return switch
# End toggleSwitchState


#--------------------------------------------------------------------------------------
def usage():
   print "help"
# End usage

#--------------------------------------------------------------------------------------
#######################################################################################
#######################################################################################
#######################################################################################
####
####    S T A R T  M A I N  F U N C T I O N
####
#######################################################################################
#######################################################################################
#######################################################################################
logger = eaglelog.getLogging()
ppADDR = 0
def main():
  global ppADDR
  #------------------------------------------------------------------------------------
  #  Read command line options
  #
  try:
     opts, args = getopt.getopt( sys.argv[1:], "hfs:v", ["help", "file=", "state="])
  except getopt.GetoptError as err:
     usage()
     sys.exit(2)
  fileName = "config.json"
  stateFile = "state.json"
  verbose = False
  for o, a in  opts:
     if o == "-v":
        verbose = True
     elif o in ( "-h", "--help" ):
        usage()
        sys.exit()
     elif o in ( "-f", "--file" ):
        fileName = a
     elif o in ( "-s", "--state" ):
        stateFile = a
     else:
        assert False, "unhandled option"
     # End if
  # End for

  config = readFile( fileName )
  running = True
  #------------------------------------------------------------------------------------
  # Initialize the state of the switches
  state = []
  ppADDR=config['ppADDR']
  RELAY.RESET( ppADDR )
  #####################################################################################
  ##
  ##    S T A R T  M A I N  L O O P
  ##
  #####################################################################################
  signal.signal( signal.SIGINT, signal_handler)
  signal.signal( signal.SIGTERM, signal_handler)
  while running:
      for switch in config['switches']:
         switch = toggleBankState( switch )
         time.sleep( config['sleepTime'] )
         switch['state'] = 'OFF'
         logger.info( "Setting %s = %s" % ( switch['name'], switch['state'] ) )
      # End foreach 
  # End While


# End Main

if __name__ == "__main__":
    main()


