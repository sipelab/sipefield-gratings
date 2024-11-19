﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.1.5),
    on August 01, 2024, at 23:06
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# Run 'Before Experiment' code from nidaq_parameters
import nidaqmx

NIDAQ_DEVICE = 'Dev1'
CHANNELS = ['port2/line0']
# Run 'Before Experiment' code from code_nidaq_trigger
class NIDAQ:
    '''
    Class to handle NI-DAQ operations for digital output. The class is used as a context manager to ensure proper initialization and cleanup of the NI-DAQ task. 
    The send_signal method is used to send a digital signal to the specified channels
    The trigger method is a convenience method to send a high signal followed by a low signal to the channels.
    
    Parameters:
    - device_name (str): Name of the NI-DAQ device (default: 'Dev2')
    - channels (list): List of channel names to use for digital output (default: ['port0/line0', 'port0/line1'])
    '''
    def __init__(self, device_name=NIDAQ_DEVICE, channels=CHANNELS):
        self.device_name = device_name
        self.channels = channels if channels else ['port0/line0', 'port0/line1']
        self.task = None

    def __enter__(self):
        self.task = nidaqmx.Task()
        for channel in self.channels:
            full_channel_name = f'{self.device_name}/{channel}'
            self.task.do_channels.add_do_chan(full_channel_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.task:
            self.task.close()

    def send_signal(self, signal_values):
        if not self.task:
            raise RuntimeError("Task not initialized. Use 'with NIDAQ(...) as nidaq:' context.")
        self.task.write(signal_values)
        print(f"Signal {'High' if all(signal_values) else 'Low'} on {self.device_name} for channels {self.channels}")

    def trigger(self, state):
        signal_values = [state] * len(self.channels)
        self.send_signal(signal_values)
        
    def pulse(self, duration=1):
        self.trigger(True)
        time.sleep(duration)
        self.trigger(False)

# Run 'Before Experiment' code from generate_grating_angles
import random


grating_angles_array = [0, 45, 90, 135, 180, 225, 270, 315]

# Run 'Before Experiment' code from read_encoder
"""jgronemeyer 2024 custom code block"""
import serial
import time
from datetime import datetime # for BIDS saving
import pandas as pd
import os
import threading

# For BIDS file saving
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # get current timestamp (BIDS)

# Constants
WHEEL_DIAMETER = 0.1  # in meters, example value
ENCODER_CPR = 1200    # encoder counts per revolution
SAMPLE_WINDOW = 0.05  # sample window in seconds, matching the Arduino sample window
SAVE_DIR = r'C:/dev/devOutput/encoder'  # Directory to save data
PORT = 'COM4'

# Set up the serial port connection to arduino
arduino = serial.Serial(port=PORT, baudrate=57600, timeout=1)

# Initialize DataFrame to store encoder data
columns = ['timestamp', 'speed', 'distance', 'direction']
encoder_data = pd.DataFrame(columns=columns)

# Shared variable for clicks (raw value received from encoder)
clicks_lock = threading.Lock() #thread locked for synchronization
shared_clicks = 0 #cross-thread accessible variable

def read_encoder():
    global shared_clicks
    while True:
        try:
            data = arduino.readline().decode('utf-8').strip()
            if data:
                with clicks_lock:
                    shared_clicks = int(data)
        except ValueError:
            pass

#NOTE: time_interval value should use PsychoPy's core.Clock() 
def calculate_metrics(clicks, time_interval):
    rotations = clicks / ENCODER_CPR
    distance = rotations * (3.1416 * WHEEL_DIAMETER)
    speed = distance / time_interval  # m/s
    return speed, distance

def determine_direction(clicks):
    if clicks == 0:
        return 0  # Stationary
    elif clicks > 0:
        return 1  # Forward
    else:
        return 2  # Backward

def save_data(timestamp, speed, distance, direction):
    global encoder_data
    new_data = pd.DataFrame([[timestamp, speed, distance, direction]], columns=encoder_data.columns)
    encoder_data = pd.concat([encoder_data, new_data], ignore_index=True)
# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.1.5'
expName = 'Gratings_vis_devJG_v0.6'  # from the Builder filename that created this script
# information about this experiment
expInfo = {
    'Protocol ID': 'devJG',
    'Subject ID': '01',
    'Session ID': '01',
    'Wait for Trigger': False,
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [2560, 1440]
_loggingLevel = logging.getLevel('warning')
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']
    # override logging level
    _loggingLevel = logging.getLevel(
        prefs.piloting['pilotLoggingLevel']
    )

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    filename = u'data/%s/sub-%s/ses-%s/beh/sub-%s_ses-%s_%s' % (expInfo['Protocol ID'], expInfo['Subject ID'], expInfo['Session ID'], expInfo['Subject ID'], expInfo['Session ID'], timestamp)
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        originPath='C:\\dev\\sipefield-gratings\\PsychoPy\\Gratings_vis_stim_devSB-JG_v0.7_lastrun.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # this outputs to the screen, not a file
    logging.console.setLevel(_loggingLevel)


def setupWindow(expInfo=None, win=None):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=0,
            winType='pyglet', allowStencil=False,
            monitor='wfieldMonitor', color=[0,0,0], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height', 
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0,0,0]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # get/measure frame rate if not already in expInfo
        if win._monitorFrameRate is None:
            win.getActualFrameRate(infoMsg='Attempting to measure frame rate of screen, please wait...')
        expInfo['frameRate'] = win._monitorFrameRate
    win.mouseVisible = False
    win.hideMessage()
    # show a visual indicator if we're in piloting mode
    if PILOTING and prefs.piloting['showPilotingIndicator']:
        win.showPilotingIndicator()
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    ioSession = '1'
    if 'session' in expInfo:
        ioSession = str(expInfo['session'])
    ioServer = io.launchHubServer(window=win, **ioConfig)
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    if deviceManager.getDevice('key_resp') is None:
        # initialise key_resp
        key_resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp',
        )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], playbackComponents=[]):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    playbackComponents : list, tuple
        List of any components with a `pause` method which need to be paused.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # pause any playback components
    for comp in playbackComponents:
        comp.pause()
    # prevent components from auto-drawing
    win.stashAutoDraw()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # flip the screen
        win.flip()
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    for comp in playbackComponents:
        comp.play()
    # restore auto-drawn components
    win.retrieveAutoDraw()
    # reset any timers
    for timer in timers:
        timer.reset()


def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # enter 'rush' mode (raise CPU priority)
    if not PILOTING:
        core.rush(enable=True)
    # mark experiment as started
    thisExp.status = STARTED
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    
    # Start Code - component code to be run after the window creation
    
    # --- Initialize components for Routine "nidaqTrigger" ---
    text_waiting_message = visual.TextStim(win=win, name='text_waiting_message',
        text='Waiting for NIDAQ trigger to begin visual stim...',
        font='Arial',
        pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    # Run 'Begin Experiment' code from code_nidaq_trigger
    wait_for_trigger = False
    key_resp = keyboard.Keyboard(deviceName='key_resp')
    
    # --- Initialize components for Routine "display_gratings" ---
    # Run 'Begin Experiment' code from generate_grating_angles
    grating_index = 0
    stim_grayScreen = visual.ImageStim(
        win=win,
        name='stim_grayScreen', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), size=(1, 1),
        color=[0.0000, 0.0000, 0.0000], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    stim_grating = visual.GratingStim(
        win=win, name='stim_grating',
        tex='sin', mask=None, anchor='center',
        ori=1.0, pos=(0, 0), size=(2, 2), sf=8.0, phase=1.0,
        color=[1,1,1], colorSpace='rgb',
        opacity=2.0, contrast=1.0, blendmode='avg',
        texRes=256.0, interpolate=True, depth=-2.0)
    # Run 'Begin Experiment' code from read_encoder
    """jgronemeyer 2024 custom code block"""
    total_distance = 0
    
    # Start the encoder reading thread
    encoder_thread = threading.Thread(target=read_encoder, daemon=True)
    encoder_thread.start()
    
    # create some handy timers
    
    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    win.flip()  # flip window to reset last flip timer
    # store the exact time the global clock started
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    # --- Prepare to start Routine "nidaqTrigger" ---
    continueRoutine = True
    # update component parameters for each repeat
    thisExp.addData('nidaqTrigger.started', globalClock.getTime(format='float'))
    # Run 'Begin Routine' code from code_nidaq_trigger
    if wait_for_trigger:
        with NIDAQ() as nidaq:
            print("Waiting for trigger...")
            nidaq.trigger(False)
            while not nidaq.task.read():
                time.sleep(0.1)
    
    
    # create starting attributes for key_resp
    key_resp.keys = []
    key_resp.rt = []
    _key_resp_allKeys = []
    # keep track of which components have finished
    nidaqTriggerComponents = [text_waiting_message, key_resp]
    for thisComponent in nidaqTriggerComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "nidaqTrigger" ---
    routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_waiting_message* updates
        
        # if text_waiting_message is starting this frame...
        if text_waiting_message.status == NOT_STARTED and frameN >= 0:
            # keep track of start time/frame for later
            text_waiting_message.frameNStart = frameN  # exact frame index
            text_waiting_message.tStart = t  # local t and not account for scr refresh
            text_waiting_message.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_waiting_message, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'text_waiting_message.started')
            # update status
            text_waiting_message.status = STARTED
            text_waiting_message.setAutoDraw(True)
        
        # if text_waiting_message is active this frame...
        if text_waiting_message.status == STARTED:
            # update params
            pass
        # Run 'Each Frame' code from code_nidaq_trigger
        ## Check the condition each frame
        #with nidaqmx.Task() as nidaq: 
        #    # Configure the task to listen for a digital input signal on a specific port and line
        #    nidaq.di_channels.add_di_chan("Dev1/port2/line0")
        #    print("Waiting for trigger signal...")
        #    
        #    nidaq_trigger = nidaq.read()
        #    
        #    if nidaq_trigger:
        #        continueRoutine = False  # Ends the routine if the condition is met
        #
        
        # *key_resp* updates
        waitOnFlip = False
        
        # if key_resp is starting this frame...
        if key_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp.frameNStart = frameN  # exact frame index
            key_resp.tStart = t  # local t and not account for scr refresh
            key_resp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'key_resp.started')
            # update status
            key_resp.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp.status == STARTED and not waitOnFlip:
            theseKeys = key_resp.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_allKeys.extend(theseKeys)
            if len(_key_resp_allKeys):
                key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                key_resp.rt = _key_resp_allKeys[-1].rt
                key_resp.duration = _key_resp_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in nidaqTriggerComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "nidaqTrigger" ---
    for thisComponent in nidaqTriggerComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('nidaqTrigger.stopped', globalClock.getTime(format='float'))
    # Run 'End Routine' code from code_nidaq_trigger
    print("Starting immediately...")
    with NIDAQ() as nidaq:
        nidaq.trigger(True)
    
    # check responses
    if key_resp.keys in ['', [], None]:  # No response was made
        key_resp.keys = None
    thisExp.addData('key_resp.keys',key_resp.keys)
    if key_resp.keys != None:  # we had a response
        thisExp.addData('key_resp.rt', key_resp.rt)
        thisExp.addData('key_resp.duration', key_resp.duration)
    thisExp.nextEntry()
    # the Routine "nidaqTrigger" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=1.0, method='sequential', 
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial:
            globals()[paramName] = thisTrial[paramName]
    
    for thisTrial in trials:
        currentLoop = trials
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
        )
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]
        
        # --- Prepare to start Routine "display_gratings" ---
        continueRoutine = True
        # update component parameters for each repeat
        thisExp.addData('display_gratings.started', globalClock.getTime(format='float'))
        # Run 'Begin Routine' code from generate_grating_angles
        #grating_angle = random.choice(grating_angles_array)
        
        print("!!!!! Start of routine angle index:", grating_index)
        
            #print("2. else:", grating_index)
        grating_angle = grating_angles_array[grating_index]
        print("Displaying angle:", grating_angle, " with index: ", grating_index)
        grating_index += 1
        print("grating_index += 1:", grating_index)
            
        if grating_index == len(grating_angles_array):
            print(grating_index, " is >= ", len(grating_angles_array))
            grating_index = 0
            #print("if statement: index reset")
        
        stim_grating.setOri(grating_angle)
        # Run 'Begin Routine' code from read_encoder
        # This value provides the encoder thread with 
        #   the timestamp for the start of each Routine
        prev_time = core.getTime()
        
        # keep track of which components have finished
        display_gratingsComponents = [stim_grayScreen, stim_grating]
        for thisComponent in display_gratingsComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "display_gratings" ---
        routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 5.0:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *stim_grayScreen* updates
            
            # if stim_grayScreen is starting this frame...
            if stim_grayScreen.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                stim_grayScreen.frameNStart = frameN  # exact frame index
                stim_grayScreen.tStart = t  # local t and not account for scr refresh
                stim_grayScreen.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(stim_grayScreen, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'stim_grayScreen.started')
                # update status
                stim_grayScreen.status = STARTED
                stim_grayScreen.setAutoDraw(True)
            
            # if stim_grayScreen is active this frame...
            if stim_grayScreen.status == STARTED:
                # update params
                pass
            
            # if stim_grayScreen is stopping this frame...
            if stim_grayScreen.status == STARTED:
                if frameN >= 300:
                    # keep track of stop time/frame for later
                    stim_grayScreen.tStop = t  # not accounting for scr refresh
                    stim_grayScreen.tStopRefresh = tThisFlipGlobal  # on global time
                    stim_grayScreen.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'stim_grayScreen.stopped')
                    # update status
                    stim_grayScreen.status = FINISHED
                    stim_grayScreen.setAutoDraw(False)
            
            # *stim_grating* updates
            
            # if stim_grating is starting this frame...
            if stim_grating.status == NOT_STARTED and tThisFlip >= 3.0-frameTolerance:
                # keep track of start time/frame for later
                stim_grating.frameNStart = frameN  # exact frame index
                stim_grating.tStart = t  # local t and not account for scr refresh
                stim_grating.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(stim_grating, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'stim_grating.started')
                # update status
                stim_grating.status = STARTED
                stim_grating.setAutoDraw(True)
            
            # if stim_grating is active this frame...
            if stim_grating.status == STARTED:
                # update params
                stim_grating.setPhase(t, log=False)
            
            # if stim_grating is stopping this frame...
            if stim_grating.status == STARTED:
                if frameN >= 300:
                    # keep track of stop time/frame for later
                    stim_grating.tStop = t  # not accounting for scr refresh
                    stim_grating.tStopRefresh = tThisFlipGlobal  # on global time
                    stim_grating.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'stim_grating.stopped')
                    # update status
                    stim_grating.status = FINISHED
                    stim_grating.setAutoDraw(False)
            # Run 'Each Frame' code from read_encoder
            """jgronemeyer 2024 custom code block"""
            
            current_time = core.getTime()
            time_interval = current_time - prev_time
            #Time must have passed to collect encoder clicks
            if time_interval >= SAMPLE_WINDOW:
                with clicks_lock:
                    clicks = shared_clicks
            
                speed, distance = calculate_metrics(clicks, time_interval)
                total_distance += distance
                direction = determine_direction(clicks)
            
                timestamp = current_time
                save_data(timestamp, speed, total_distance, direction)
                
                #comment out/in for debugging
                print(f"Time: {timestamp:.2f}s, Speed: {speed:.2f} m/s, Total Distance: {total_distance:.2f} m, Direction: {direction}")
            
                prev_time = current_time
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in display_gratingsComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "display_gratings" ---
        for thisComponent in display_gratingsComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        thisExp.addData('display_gratings.stopped', globalClock.getTime(format='float'))
        # Run 'End Routine' code from read_encoder
        #save the dataframe trial by trial
        #thisExp.addData('encoder_data', encoder_data)
        
        #TODO: instantiate new dataframe at beginning of each
        #routine. Currently, this just incrementally appends
        #resulting in duplicate data. 
        
        #For now, data is exported separately on End Experiment
        #in a .csv
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if routineForceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-5.000000)
        thisExp.nextEntry()
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
    # completed 1.0 repeats of 'trials'
    
    # get names of stimulus parameters
    if trials.trialList in ([], [None], None):
        params = []
    else:
        params = trials.trialList[0].keys()
    # save data for this loop
    trials.saveAsExcel(filename + '.xlsx', sheetName='trials',
        stimOut=params,
        dataOut=['n','all_mean','all_std', 'all_raw'])
    trials.saveAsText(filename + 'trials.csv', delim=',',
        stimOut=params,
        dataOut=['n','all_mean','all_std', 'all_raw'])
    # Run 'End Experiment' code from code_nidaq_trigger
    with NIDAQ() as nidaq:
        nidaq.trigger(False)
    # Run 'End Experiment' code from read_encoder
    #Export encoder_data to .csv file
    save_to = u'data/%s/sub-%s/ses-%s/beh' % (expInfo['Protocol ID'], expInfo['Subject ID'], expInfo['Session ID'])
    new_dir = os.path.join(_thisDir, save_to)
    
    # Create the path if it does not exist
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    
    # Sipelab standard BIDS protocol file naming for 
    #   future batch analysis and data wrangling
    protocol_id = expInfo['Protocol ID']
    subject_id = expInfo['Subject ID']
    session_id = expInfo['Session ID']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # get current timestamp (BIDS)
    
    filename = os.path.join(new_dir, f"sub-{subject_id}_ses-{session_id}_{timestamp}_wheeldf.csv")
    
    encoder_data.to_csv(filename, index=False)
    
    
    
    # mark experiment as finished
    endExperiment(thisExp, win=win)
    # end 'rush' mode
    core.rush(enable=False)


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='comma')
    thisExp.saveAsPickle(filename)


def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # mark experiment handler as finished
    thisExp.status = FINISHED
    # shut down eyetracker, if there is one
    if deviceManager.getDevice('eyetracker') is not None:
        deviceManager.removeDevice('eyetracker')


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    # shut down eyetracker, if there is one
    if deviceManager.getDevice('eyetracker') is not None:
        deviceManager.removeDevice('eyetracker')
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)