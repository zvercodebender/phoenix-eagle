#!/usr/bin/python

import os
import json
import getopt
import sys
import signal
import time 
import piplates.RELAYplate as RELAY

#--------------------------------------------------------------------------------------
def signal_handler( signal, frame ):
    global ppADDR
    print('You pressed Ctrl-C!')
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
def toggleSwitchState( state, DO ):
   global ppADDR
   if (state == 'OFF') :
      RELAY.relayON( ppADDR, DO )
      state = 'ON'
   else: 
      RELAY.relayOFF( ppADDR, DO )
      state = 'OFF'
   # End if
   print "Setting DO %s = %s" % ( DO, state )
   return state
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
  state = {}
  ppADDR=config['ppADDR']
  RELAY.RESET( ppADDR )
  for switch in config['switches']:
      state[ switch['name'] ] = { "DO": switch['DO'], "state": switch['state'] }
  # End for each
  writeFile( stateFile, state )
  #####################################################################################
  ##
  ##    S T A R T  M A I N  L O O P
  ##
  #####################################################################################
  signal.signal( signal.SIGINT, signal_handler)
  while running:
      for switch in config['switches']:
         state[ switch['name'] ]['state'] = toggleSwitchState( state[ switch['name'] ]['state'], switch['DO'] )
         writeFile( stateFile, state )
         time.sleep( config['sleepTime'] )
         state[ switch['name'] ]['state'] = toggleSwitchState( state[ switch['name'] ]['state'], switch['DO'] )
      # End foreach 
      print "======"
  # End While


# End Main

if __name__ == "__main__":
    main()


