from stage.ctrl_msg import *
from stage.motor_ctrl.stage_info import _print_stage_detection_improve_message,stage_name_from_get_hw_info
import weakref
import time
import pkgutil
from ast import literal_eval as make_tuple
import os, configparser

class MotorCtrl:
    '''
        Class MotorCtrl to manipulate an APT controller.
        ================================================
        
        Parameters
        ----------
        port : class stage.motor_ini.SingleControllerPort
            SingleControllerPort('PORT_ENTRY',SERIAL_NO)
            
        chan_ident : int 
            channel identity 0x01
            
        ini_section : str
            model name of a detected stage
            
        '''
    
    def __init__(self, port, chan_ident, ini_section):
        
        self._port = port # call the class Port in port.py with arguments 
        self._chan_ident = chan_ident
        self._config = configparser.ConfigParser()
        self._config.read_string(pkgutil.get_data('stage.motor_ctrl','MG17APTServer.ini').decode('ascii'))
        
        self._name = ini_section
        
        self._conf_stage_id = self._config.getint(ini_section, 'Stage ID')
        self._conf_axis_id = self._config.getint(ini_section, 'Axis ID')
        self._conf_units = self._config.getint(ini_section, 'Units')
        self._conf_pitch = self._config.getfloat(ini_section, 'Pitch')
        self._conf_dir_sense = self._config.getint(ini_section, 'Dir Sense')
        self._conf_min_pos = self._config.getfloat(ini_section, 'Min Pos')
        self._conf_max_pos = self._config.getfloat(ini_section, 'Max Pos')
        self._conf_def_min_vel = self._config.getfloat(ini_section, 'Def Min Vel')
        self._conf_def_accn = self._config.getfloat(ini_section, 'Def Accn')
        self._conf_def_max_vel = self._config.getfloat(ini_section, 'Def Max Vel')
        self._conf_max_accn = self._config.getfloat(ini_section, 'Max Accn')
        self._conf_max_vel = self._config.getfloat(ini_section, 'Max Vel')
        self._conf_backlash_dist = self._config.getfloat(ini_section, 'Backlash Dist')
        self._conf_move_factor = self._config.getint(ini_section, 'Move Factor')
        self._conf_rest_factor = self._config.getint(ini_section, 'Rest Factor')
        self._conf_cw_hard_limit = self._config.getint(ini_section, 'CW Hard Limit')
        self._conf_ccw_hard_limit = self._config.getint(ini_section, 'CCW Hard Limit')
        self._conf_cw_soft_limit = self._config.getfloat(ini_section, 'CW Soft Limit')
        self._conf_ccw_soft_limit = self._config.getfloat(ini_section, 'CCW Soft Limit')        
        self._conf_soft_limit_mode = self._config.getint(ini_section, 'Soft Limit Mode')
        self._conf_home_dir = self._config.getint(ini_section, 'Home Dir')
        self._conf_home_limit_switch = self._config.getint(ini_section, 'Home Limit Switch')
        self._conf_home_vel = self._config.getfloat(ini_section, 'Home Vel')
        self._conf_home_zero_offset = self._config.getfloat(ini_section, 'Home Zero Offset')
        self._conf_jog_mode = self._config.getint(ini_section, 'Jog Mode')
        self._conf_jog_step_size = self._config.getfloat(ini_section, 'Jog Step Size')
        self._conf_jog_min_vel = self._config.getfloat(ini_section, 'Jog Min Vel')
        self._conf_jog_accn = self._config.getfloat(ini_section, 'Jog Accn')
        self._conf_jog_max_vel = self._config.getfloat(ini_section, 'Jog Max Vel')
        self._conf_jog_stop_mode = self._config.getint(ini_section, 'Jog Stop Mode')
        self._conf_steps_per_rev = self._config.getint(ini_section, 'Steps Per Rev')
        self._conf_gearbox_ratio = self._config.getint(ini_section, 'Gearbox Ratio')
        self._conf_dc_servo = self._config.getboolean(ini_section, 'DC Servo', fallback = False)
        
        if self._conf_dc_servo:
            self._conf_dc_prop = self._config.getint(ini_section, 'DC Prop')
            self._conf_dc_int = self._config.getint(ini_section, 'DC Int')
            self._conf_dc_diff = self._config.getint(ini_section, 'DC Diff')
            self._conf_dc_intlim = self._config.getint(ini_section, 'DC IntLim')
        
        self._conf_fp_controls = self._config.getboolean(ini_section, 'FP Controls', fallback = False)
        if self._conf_fp_controls:
            self._conf_pot_zero_wnd = self._config.getint(ini_section, 'Pot Zero Wnd')
            self._conf_pot_vel_1 = self._config.getfloat(ini_section, 'Pot Vel 1')
            self._conf_pot_wnd_1 = self._config.getint(ini_section, 'Pot Wnd 1')
            self._conf_pot_vel_2 = self._config.getfloat(ini_section, 'Pot Vel 2')
            self._conf_pot_wnd_2 = self._config.getint(ini_section, 'Pot Wnd 2')
            self._conf_pot_vel_3 = self._config.getfloat(ini_section, 'Pot Vel 3')
            self._conf_pot_wnd_3 = self._config.getint(ini_section, 'Pot Wnd 3')
            self._conf_pot_vel_4 = self._config.getfloat(ini_section, 'Pot Vel 4')
            self._conf_button_mode = self._config.getint(ini_section, 'Button Mode')
            self._conf_button_pos_1 = self._config.getfloat(ini_section, 'Button Pos 1')
            self._conf_button_pos_2 = self._config.getfloat(ini_section, 'Button Pos 2')
            
        self._conf_js_params = self._config.getboolean(ini_section, 'JS Params', fallback = False)
        
        if self._conf_js_params:
            
            self._conf_js_gearlow_maxvel = self._config.getfloat(ini_section, 'JS GearLow MaxVel')
            self._conf_js_gearlow_accn = self._config.getfloat(ini_section, 'JS GearLow Accn')
            self._conf_js_dir_sense = self._config.getfloat(ini_section, 'JS Dir Sense')
            
        self._last_ack_sent = time.time()
        
        self._port.send_message(MGMSG_MOD_SET_CHANENABLESTATE(chan_ident = self._chan_ident, chan_enable_state = 0x01))
        
        self._extr_str = make_tuple(self.__repr__().strip('SingleControllerPort'))
        print('Success: Stage {0} is detected and a controller with serial number {1}'.format(self._name,self._extr_str[1]), \
              'is connected via port',self._extr_str[0],'\n')     
        
        #STATUS UPDATE
        self._state_position = None
        self._state_velocity = None
        self._state_status_bits = None
        
        #VEL PARAMS
        self._state_min_vel = None
        self._state_max_vel = None
        self._state_accn = None
        
        #HOME PARAMS
        self._state_home_velocity = None
        self._state_home_direction = None
        self._state_home_limit_switch = None
        self._state_home_offset_distance = None
        
        
    def _handle_message(self, msg):
        if self._last_ack_sent < time.time() - 0.5:
            self._port.send_message(MGMSG_MOT_ACK_DCSTATUSUPDATE())
            self._last_ack_sent = time.time()
            
        if isinstance(msg, MGMSG_MOT_GET_DCSTATUSUPDATE) or \
           isinstance(msg, MGMSG_MOT_GET_STATUSUPDATE) or \
           isinstance(msg, MGMSG_MOT_MOVE_COMPLETED):
            
            self._state_position = msg['position']
            if isinstance(msg, MGMSG_MOT_GET_DCSTATUSUPDATE):
                self._state_velocity = msg['velocity']
            self._state_status_bits = msg['status_bits']
            return True
        
        if isinstance(msg, MGMSG_MOT_MOVE_HOMED):
            return True
        
        if isinstance(msg, MGMSG_MOT_GET_VELPARAMS):
            self._state_min_vel = msg['min_velocity']
            self._state_max_vel = msg['max_velocity']
            self._state_accn = msg['acceleration']
            return True
        
        if isinstance(msg, MGMSG_MOT_GET_HOMEPARAMS):
            self._state_home_direction = msg['home_direction']
            self._state_home_limit_switch = msg['limit_switch']
            self._state_home_velocity = msg['home_velocity']
            self._state_home_offset_distance = msg['offset_distance']
            return True
    
        return False
    

#####  STATUS UPDATE  #######################################################################################################
    
    @property
    def status(self):
        '''
        Returns current status of the stage.
        
        Returns
        -------
        out : NoneType
        
            - stage name
            - real-time position of the stage
            - real-time velocity of the stage
            - type of motion ongoing and if channel is enabled
            - general velocity setting
            - homing velocity setting
            
        List of useful attributes
        -------------------------
        stage_model: returns name of the stage
        pos : returns real-time position of stage
        set_pos(float/int) : sets new position
        vel : returns real-time velocity of the stage
        accn : returns current acceleration of the stage
        set_accn : sets new acceleration
        
        '''
        print("Stage name: {0}".format(self._name))
        print("Real-time position: {0:0.03f} {1}".format(self.pos, self.units))
        # Velocity information not available with some stages, e.g. LTS300
        #print("Velocity: {0:0.03f}{1}/s".format(self.vel, self.units))
        if self.vel is not None:
            print("Real-time velocity: {0:0.03f} {1}/s".format(self.vel, self.units))
        
        flags = []
        if self.status_forward_hardware_limit_switch_active:
            flags.append("forward hardware limit switch is active")
        if self.status_reverse_hardware_limit_switch_active:
            flags.append("reverse hardware limit switch is active")
        if self.status_in_motion_forward or self.status_in_motion_reverse or self.status_in_motion_jogging_forward or self.status_in_motion_jogging_reverse or self.status_in_motion_homing:
            flags.append('in motion')
        if self.status_in_motion_forward:
            flags.append('moving forward')
        if self.status_in_motion_reverse:
            flags.append('moving reverse')
        if self.status_in_motion_jogging_forward:
            flags.append('jogging forward')
        if self.status_in_motion_jogging_reverse:
            flags.append('jogging reverse')
        if self.status_in_motion_homing:
            flags.append('homing')
        if self.status_homed:
            flags.append('static')
        if self.status_tracking:
            flags.append('tracking')
        if self.status_settled:
            flags.append('settled')
        if self.status_motion_error:
            flags.append('motion error')
        if self.status_motor_current_limit_reached:
            flags.append('motor current limit reached')
        if self.status_channel_enabled:
            flags.append('channel enabled')
            
        print("Motor motion: {0}".format(' and '.join(flags)))
        print("Velocity setting: moving velocity is between {0.min_vel:0.3f}-{0.max_vel:0.3f}{0.units}/s and acceleration is {0.accn:0.3f}{0.units}/s²".format(self))
        print("Homing setting: homing velocity is between {0.home_vel:0.3f}{0.units}/s {0.home_dir_str}, limit switch is {0.home_limit_switch} and offset distance is {0.home_offset_dist:0.3f} {0.units}".format(self))    
    
    @property
    def pos_lim(self):
        """
        Returns lower and upper limits of motor position.
        
        Returns
        -------
        out : tuple
            (minimum position, maximum position)
        """
        return (self._conf_min_pos,self._conf_max_pos)
    
    @property
    def pos(self):
        '''
        Returns position of stage in mm or degrees dependent of unit setting.
        
        Returns
        -------
        out : float
            position
            
        Examples
        --------
        s.pos
        
        '''
        self._wait_for_properties(('_state_position', ), timeout = 3, message = \
                                  MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return self._state_position / self._EncCnt

    def set_pos(self, new_value, blocking = False):
        '''
        Move to absolute position.
        
        Parameters:
        -----------
        new_value : float or int
            absolute position the stage will be moved to
        blocking  : bool
            not wait unil completion of moving
            Default: False
        
        Examples
        --------
        s.set_pos(2)
        
        Note : do check allowed minimum and maximum values for
               position before setting it.
               
        '''
        # check if the input value for position is a float or an integer
        if isinstance(new_value,(int,float)):
            try:
                # add a parameter value restriction
                assert (new_value >= self._conf_min_pos) and (new_value <= self._conf_max_pos)
            except AssertionError:
                print('Oops! Try a different value for position and it should be within [{0},{1}] {2}'. \
                      format(self._conf_min_pos,self._conf_max_pos,self.units))
                new_value = self.pos
        else:
            raise TypeError('Position value must be an integer or a float')
        # convert position using EncCnt scaling factor
        abs_dist = int(new_value * self._EncCnt)
        if not blocking:
            # if the desired position is the same as the current position of the stage, no command sent out in this case
            if abs_dist == self._state_position:
                pass
            
            else:
                pos_ini = self.pos
                self._port.send_message(MGMSG_MOT_MOVE_ABSOLUTE_long(chan_ident = self._chan_ident, \
                                                                         absolute_distance = abs_dist))
                time_ini = time.time()
                while not self.is_in_motion:
                    if abs(abs_dist - pos_ini*self._EncCnt) == 1:
                        break
                    if time.time() - time_ini >= 2:
                        break
                time_ini = time.time()
                while True:
                    if not bool(sum([self.is_in_motion for i in range(10)])):
                        break
                    if time.time() - time_ini >= 20:
                        raise Exception('Unable to move the stage to the new position')
                param_ini = 0
                while True:
                    if sum([self._state_position for i in range(10)])/10 == abs_dist:
                        break
                    elif time.time() - time_ini >= 30:
                        raise Exception('Unable to move the stage to the new position')
                    else:
                        if param_ini == 0 and abs_dist != 0:
                            self._port.send_message(MGMSG_MOT_MOVE_ABSOLUTE_long(chan_ident = \
                                                self._chan_ident, absolute_distance = abs_dist))
                        if param_ini == 0 and abs_dist == 0:
                            self.move_home()
                        param_ini += 1
        if blocking:
            self._port.send_message(MGMSG_MOT_MOVE_ABSOLUTE_long(chan_ident = self._chan_ident, \
                                                                         absolute_distance = abs_dist))
                    
            '''
            # if the desired position is different from the stage's current position
            else:
                # initial position
                pos_ini = self.pos
                # send out command
                self._port.send_message(MGMSG_MOT_MOVE_ABSOLUTE_long(chan_ident = self._chan_ident, absolute_distance = absolute_distance))
                # 1. setting new position command takes some time to reach the controller
                # and it also takes some time for the controller to execute
                # the command. we let the subsequent motion status check
                # happen until the motor starts moving
                print('0: ',self.vel)
                time_ini = time.time()
                while (abs(pos_ini - self.pos) == 0) or self.vel == 0:
                    if abs(absolute_distance - pos_ini*self._EncCnt) == 1:
                        break
                    elif (time.time() - time_ini) >= 20:
                        raise Exception('Setting new position failed')
                print('1: ',self.vel, self.pos)
                # 2. then we wait until stage arrives at the new position
                while self.is_in_motion:
                    pass
                print('2: ',self.is_in_motion)
                print('3: ',self.pos)
                # 3. when controller says stage isn't in motion, it doesn't necessarily
                # mean the stage has arrived at the desired position. The motion may
                # still continue for a little while, in a small scale, trying to carry out
                # some fine adjustments on stage position. We here use a while loop
                # to wait until everything is done.
                while abs(absolute_distance - self._state_position)/self._EncCnt < 1e-1:
                    if ((absolute_distance == self._state_position) and (self.vel == 0)) or \
                       abs(absolute_distance - pos_ini*self._EncCnt) == 1:
                        break
                # 4. unfornately, should the controller becomes slightly faulty,
                # namely that the stage is not at position 0 mm, we have to manually
                # move the stage home using property set_pos
                while not (self._state_position == absolute_distance):
                    # type I error: if the controller says it's static when it's not,
                    # an error is thrown in this case.
                    if self.is_in_motion and (self.vel == 0):
                        raise Exception('Setting new position error: your controller is faulty.')
                    # type II error: maybe the controller is still doing fine adjustment
                    # on the stage position. In this case, we wait until everything is done
                else:
                    pass
                
                '''
    def move_by(self, new_value, blocking = False):
        """
        Move relative to current position.
        
        Parameters
        ----------
        new_value : float or int
            relative distance for the stage to travel
        blocking : bool
            not wait until moving is finished
            Default: False
        
        Examples
        --------
        s.move_by(2)
        s.move_by(-2)
        
        """
        rel_dist = int(new_value * self._EncCnt)
        # check if the input value for travelling distance is a float or an integer
        if isinstance(new_value,(int,float)):
            try:
                # add a parameter value restriction
                assert (self.pos + new_value >= self._conf_min_pos) and \
                       (self.pos + new_value <= self._conf_max_pos)
            except AssertionError:
                print('Oops! Try a different value for jogging distance and it should be within [{0},{1}] {2}'. \
                      format(self._conf_min_pos - self.pos, self._conf_max_pos - self.pos, self.units))
                new_value = None
        else:
            raise TypeError('Position value must be an integer or a float')
        
        if not blocking:
            # if the desired position is the same as the current position of the stage, no command sent out in this case
            if new_value == None:
                return
            if rel_dist == 0:
                return
            
            else:
                pos_ini = int(self.pos * self._EncCnt)
                self._port.send_message(MGMSG_MOT_MOVE_RELATIVE_long(chan_ident = self._chan_ident, \
                                        relative_distance = rel_dist))
                time_ini = time.time()
                while not self.is_in_motion:
                    if abs(rel_dist) == 1:
                        break
                    if time.time() - time_ini >= 2:
                        break
                time_ini = time.time()
                while True:
                    if not bool(sum([self.is_in_motion for i in range(10)])):
                        break
                    if time.time() - time_ini >= 20:
                        raise Exception('Unable to move the stage to the new position')
                param_ini = 0
                while True:
                    if sum([self._state_position for i in range(10)])/10 == rel_dist + pos_ini:
                        break
                    elif time.time() - time_ini >= 30:
                        raise Exception('Unable to move the stage to the new position')
                    else:
                        '''
                        if param_ini == 0 and rel_dist + pos_ini != 0:
                            self._port.send_message(MGMSG_MOT_MOVE_RELATIVE_long(chan_ident = self._chan_ident, \
                                        relative_distance = rel_dist))
                            print('1')'''
                        if param_ini == 0 and rel_dist + pos_ini == 0:
                            self.move_home()
                            print('Unknown error occured')
                        param_ini += 1
        if blocking:
            if new_value == None:
                pass
            else:
                self._port.send_message(MGMSG_MOT_MOVE_RELATIVE_long(chan_ident = self._chan_ident, \
                                        relative_distance = rel_dist))
        
        
        '''
        if not blocking:
            if new_value != None:
                self._port.send_message(MGMSG_MOT_MOVE_RELATIVE_long(chan_ident = self._chan_ident, \
                                        relative_distance = relative_distance))
                # 1. setting new position command takes some time to reach the controller
                # and it also takes some time for the controller to execute
                # the command. we let the subsequent motion status check
                # happen until the motor starts moving
                while self.vel == 0:
                    pass
                print('1: ',self.vel)
                # 2. then we wait until stage arrives at the new position
                while self.is_in_motion:
                    pass
                print('2: ',self.is_in_motion)
                print('3: ',self.pos)
                # 3. when controller says stage isn't in motion, it doesn't necessarily
                # mean the stage has arrived at the desired position. The motion may
                # still continue for a little while, in a small scale, trying to do
                # some fine adjustments on stage position. We here use a while loop
                # to wait until everything is done.
                while (pos_ini + relative_distance - self._state_position)/self._EncCnt < 1e-1:
                    if pos_ini + relative_distance == self._state_position:
                        break
                # 4. unfornately, should the controller becomes slightly faulty,
                # namely that the stage is not at position 0 mm, we have to manually
                # move the stage home using property set_pos
                while not (self._state_position == absolute_distance):
                    # type I error: if the controller says it's static when it's not,
                    # an error is thrown in this case.
                    if self.is_in_motion and (self.vel == 0):
                        raise Exception('Setting jogging distance error: your controller is faulty.')
                    # type II error: maybe the controller is still doing fine adjustment
                    # on the stage position. In this case, we wait until everything is done
                else:
                    pass
                
        '''       
        
        
    @property
    def backlash_dist(self):
        """
        Backlash distance.
        
        Returns
        -------
        out : float
            backlash distance
            
        """
        return self._conf_backlash_dist
    
    @property
    def get_stage_axis_info(self):
        """
        Returns axis information of stage.
        Returns
        -------
        out : tuple
            (minimum position, maximum position, stage units, pitch)
        
        Information
        -----------    
        min_pos : float
        minimum position
        
        max_pos : float
        maximum position
        
        units : int
        stage units:
              - STAGE_UNITS_MM = 1 : Stage units in mm
              - STAGE_UNITS_DEG = 2 : Stage units in degrees
              
        pitch : float
                pitch
                
        """
        min_pos = self._conf_min_pos
        max_pos = self._conf_max_pos
        units = self._conf_units
        pitch = self._conf_pitch
        
        return (min_pos, max_pos, units, pitch)    
    
    @property
    def status_forward_hardware_limit_switch_active(self):
        """
        Returns whether forward hardware limit switch is active.
        
        Returns
        -------
        out : bool
            True if forwards and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000001)

    @property
    def status_reverse_hardware_limit_switch_active(self):
        """
        Returns whether reverse hardware limit switch is active.
        
        Returns
        -------
        out : bool
            True if backwards and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000002)
    
    @property
    def get_hardware_limit_switches(self):
        """
        Returns hardware limit switch modes for reverse and forward direction.
        
        Returns
        -------
        out : tuple
            (reverse limit switch, forward limit switch)
            HWLIMSWITCH_IGNORE = 1 : Ignore limit switch (e.g. for stages
                with only one or no limit switches).
            HWLIMSWITCH_MAKES = 2   : Limit switch is activated when electrical
                continuity is detected.
            HWLIMSWITCH_BREAKS = 3 : Limit switch is activated when electrical
                continuity is broken.
            HWLIMSWITCH_MAKES_HOMEONLY = 4 : As per HWLIMSWITCH_MAKES except
                switch is ignored other than when homing (e.g. to support
                rotation stages).
            HWLIMSWITCH_BREAKS_HOMEONLY = 5 : As per HWLIMSWITCH_BREAKS except
                switch is ignored other than when homing (e.g. to support
                rotation stages).
                
        See also
        --------
        set_hardware_limit_switches
        
        """
        rev = self._conf_ccw_hard_limit
        fwd = self._conf_cw_hard_limit
        return (rev, fwd)

    @property
    def status_in_motion_forward(self):
        """
        Returns whether motor is moving forwards.
        
        Returns
        -------
        out : bool
            True if forwards and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000010)

    @property
    def status_in_motion_reverse(self):
        """
        Returns whether motor is moving backwards.
        
        Returns
        -------
        out : bool
            True if backwards and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000020)

    @property
    def status_in_motion_jogging_forward(self):
        """
        Returns whether motor is jogging forwards.
        
        Returns
        -------
        out : bool
            True if forwards and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000040)

    @property
    def status_in_motion_jogging_reverse(self):
        """
        Returns whether motor is jogging backwards.
        
        Returns
        -------
        out : bool
            True if backwards and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000080)

    @property
    def status_tracking(self):
        """
        Returns whether motor is tracking.
        
        Returns
        -------
        out : bool
            True if motor is tracking and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00001000)

    @property
    def status_settled(self):
        """
        Returns whether motor is settled.
        
        Returns
        -------
        out : bool
            True if motor is settled and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00002000)

    @property
    def status_motion_error(self):
        """
        Returns whether there is a motion error (= excessing position error).
        
        Returns
        -------
        out : bool
            True if there is a motion error and False if there is not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00004000)

    @property
    def status_motor_current_limit_reached(self):
        """
        Returns whether motor current limit has been reached.
        
        Returns
        -------
        out : bool
            True if the limit is reached and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x01000000)

    @property
    def status_channel_enabled(self):
        """
        Returns whether active motor channel is enabled.
        
        Returns
        -------
        out : bool
            True if motor channel is enabled and False if not.
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x80000000)
    
    @property
    def is_in_motion(self):
        """
        Returns whether motor is in motion.
        
        Returns
        -------
        out : bool
            True for in motion and False for not in motion
            
        """
        motion_status = self.status_in_motion_forward or self.status_in_motion_reverse or self.status_in_motion_jogging_forward or \
                        self.status_in_motion_jogging_reverse
        return motion_status
    
    @property
    def status_homed(self):
        """
        Returns whether motor is homed at some point.
        
        Returns
        -------
        out : bool
            True for homed and False for not
            
        """
        # we now abondon the using message bits given by Thorlabs as it's pretty much not reliable. Sometimes status_homed returns False when
        # the stage is already homed and sometimes the other way around. So instead we now use position to verify if the stage is homed.
        # self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        # return bool(self._state_status_bits & 0x00000400)
        return self.pos == 0.0
    
    @property
    def status_in_motion_homing(self):
        """
        Returns whether motor is being homed.
        
        Returns
        -------
        out : bool
            True for being homed and False for not
            
        """
        self._wait_for_properties(('_state_status_bits', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return bool(self._state_status_bits & 0x00000200)
    
    @property
    def home_check(self):
        """
        Returns whether stage homing is completed.
        
        Returns
        -------
        out : bool
            True when homing is completely finished.
            
        Information
        -----------
        there are four conditions to be checked:
        
         - if stage is starting to move
         - if homing is completed
         - if stage is still
         - if controller is faulty
           i)  'manually' move stage to home
           ii) wait until stage arrives at 0 mm
           
        See also
        --------
        move_home()
            
        """
        pos_ini = self.pos
        # homing command takes some time to reach the controller
        # and it also takes some time for the controller to execute
        # the command. we let the subsequent motion status check
        # happen until the motor starts moving
        while (self.pos - pos_ini) == 0:
            pass
        # then we wait until homing is finished 
        while not self.status_homed:
            pass
        # also, we have to check if the motor is still in motion; if it is,
        # we wait until it's absolutely static.
        while True:
            if not bool(sum([self.is_in_motion for i in range(10)])):
                break
        # unfornately, should the controller becomes slightly faulty,
        # namely that the stage is not at position 0 mm, we have to manually
        # move the stage home using property set_pos
        time_ini = time.time()
        param_ini = 0
        while (not self.pos == 0.0) or self.is_in_motion:
            # type I error: if the controller says it's homed when it's not,
            # we move the stage to position 0 'manually'.
            if self.status_homed and (not sum([self.is_in_motion for i in range(20)])) \
               and (param_ini == 0):
                self.set_pos(0)
                param_ini += 1
            if time.time() - time_ini >= 20:
                raise Exception('Homing error: your controller maybe faulty.')
            # type II error: maybe the controller is still doing fine adjustment
            # on the stage position. In this case, we wait until everything is
            # done.
        return True
    
#####  VEL PARAMS  ###################################################################################################################
    
    @property
    def vel(self):
        """
        Returns motor's real-time velocity.
        
        Returns
        -------
        out : float
            velocity
            
        Note : if output is positive, motor is moving forwards;
               if output is negative, motor is moving backwards.
               
        """
        self._wait_for_properties(('_state_velocity', ), timeout = 3, message = MGMSG_MOT_REQ_DCSTATUSUPDATE(chan_ident = self._chan_ident))
        return self._state_velocity / (self._EncCnt * self._T)  # Dropped the 65536 factor, which resulted in false results.

    @property
    def accn_max_lim(self):
        """
        Returns motor's upper limit of acceleration.
        
        Returns
        -------
        out : float
            upper limit
            
        """
        return self._conf_max_accn

    @property
    def vel_max_lim(self):
        """
        Returns motor's upper limit of velocity.
        
        Returns
        -------
        out : float
            upper limit
            
        """
        return self._conf_max_vel
    
    @property
    def accn_dflt(self):
        """
        Returns motor's default acceleration.
        
        Returns
        -------
        out : float
            default acceleration
            
        """
        return self._conf_def_accn
    
    @property
    def min_vel_dflt(self):
        """
        Returns motor's default minimum velocity.
        
        Returns
        -------
        out : float
            default minimum velocity
            
        """
        return self._conf_def_min_vel
    
    @property
    def max_vel_dflt(self):
        """
        Returns motor's default maximum velocity.
        
        Returns
        -------
        out : float
            default maximum velocity
            
        """
        return self._conf_def_max_vel
    
    @property
    def min_vel(self):
        """
        Returns current minimum velocity.
        
        Returns
        -------
        out : float
            minimum velocity
            
        """
        self._wait_for_properties(('_state_min_vel', ), timeout = 3, message = MGMSG_MOT_REQ_VELPARAMS(chan_ident = self._chan_ident))
        return self._state_min_vel / (self._EncCnt * self._T * 65536)
    
    @property
    def max_vel(self):
        """
        Returns current maximum velocity.
        
        Returns
        -------
        out : float
            maximum velocity
            
        """
        self._wait_for_properties(('_state_max_vel', ), timeout = 3, message = MGMSG_MOT_REQ_VELPARAMS(chan_ident = self._chan_ident))
        return self._state_max_vel / (self._EncCnt * self._T * 65536)
    
    @property
    def accn(self):
        """
        Returns current acceleration.
        
        Returns
        -------
        out : float
            acceleration
            
        """
        self._wait_for_properties(('_state_accn', ), timeout = 3, message = MGMSG_MOT_REQ_VELPARAMS(chan_ident = self._chan_ident))
        return self._state_accn / (self._EncCnt * (self._T ** 2) * 65536)
    
    @property
    def get_vel_params(self):
        """
        Returns current velocity parameters.
        
        Returns
        -------
        out : tuple
            (minimum velocity, maximum velocity, acceleration)
            
        """
        return (self.min_vel, self.max_vel, self.accn)
    
    def set_min_vel(self, new_value):
        """
        Sets minimum velocity parameter. According to the Thorlabs
        documentation minimum velocity should be 0 by default.
        
        Parameters
        ----------
        min_vel : float or int
            minimum velocity
        
        Examples
        ----------
        s.min_vel(0)
        
        Note : do check allowed minimum value for minimum velocity
        before setting it.
        
        """
        self.set_vel_params(new_value, self.max_vel, self.accn)

    def set_max_vel(self, new_value):
        """
        Sets maximum velocity parameter.
        
        Parameters
        ----------
        max_vel : float or int
            maximum velocity
                
        Examples
        ----------
        s.max_vel(2)
            
        Note : do check allowed maximum value for maximum velocity 
        before setting it.
        
        """
        self.set_vel_params(self.min_vel, new_value, self.accn)

    def set_accn(self, new_value):
        """
        Sets acceleration parameter.
        
        Parameters
        ----------
        accn : float or int
            acceleration
                
        Examples
        ----------
        s.accn(1)
            
        Note : do check allowed minimum/maximum value for acceleration
        before setting it.
        
        """
        self.set_vel_params(self.min_vel, self.max_vel, new_value)

    def set_vel_params(self, min_vel, max_vel, accn):
        """
        Sets velocity parameters. According to the Thorlabs documentation
        minimum velocity should be 0 by default.
        
        Parameters
        ----------
        min_vel : float or int
            minimum velocity
        max_vel : float or int
            maximum velocity
        accn : float or int
            acceleration
                
        Examples
        ----------
        s.set_vel_params(0, 2, 1)
        
        Note : do check allowed maximum value for each parameter before
        setting them.
        
        """
        if isinstance(min_vel,(int,float)):
            try:
                assert (min_vel >= self._conf_def_min_vel) and (min_vel < max_vel) and (min_vel < self._conf_max_vel)
            except AssertionError:
                print('Oops! Try a different value for minimum velocity and it should be within [{0},{1}] {2}/s'. \
                      format(float(self._conf_def_min_vel),self._conf_max_vel,self.units))
                min_vel = self.min_vel
        else:
            raise TypeError('Minimum velocity value must be an integer or a float')
                
        if isinstance(max_vel,(int,float)):
            try:
                assert (max_vel > self._conf_def_min_vel) and (min_vel < max_vel) and (max_vel <= self._conf_max_vel)
            except AssertionError:
                print('Oops! Try a different value for maximum velocity and it should be within [{0},{1}] {2}/s'. \
                      format(float(self._conf_def_min_vel),self._conf_max_vel,self.units))
                max_vel = self.max_vel
        else:
            raise TypeError('Maximum velocity value must be an integer or a float')
                
        if isinstance(accn,(int,float)):
            try:
                assert (accn > 0) and (accn <= self._conf_max_accn)
            except AssertionError:
                print('Oops! Try a different value for acceleration and it should be within [{0},{1}] {2}/s²'. \
                      format(0.0,self._conf_max_accn,self.units))
                accn = self.accn
        else:
            raise TypeError('Acceleration value must be an integer or a float')
        
        msg = MGMSG_MOT_SET_VELPARAMS(
            chan_ident = self._chan_ident,
            min_velocity = int(min_vel *(self._EncCnt * self._T * 65536)),
            max_velocity = int(max_vel *(self._EncCnt * self._T * 65536)),
            acceleration = int(accn *(self._EncCnt * (self._T ** 2) * 65536)),
        )
        self._port.send_message(msg)
        
        # To set new values for the three parameters, we need to invalidate their current values
        self._state_min_vel = None
        self._state_max_vel = None
        self._state_accn = None
        
        
#####  HOMEPARAMS  ########################################################################################################################
    
    @property
    def home_vel(self):
        """
        Returns velocity of homing.
        
        Returns
        -------
        out : float
            homing velocity
        
        Information
        -----------
        homing velocity : float
            homing velocity of the motor.
            
        """
        self._wait_for_properties(('_state_home_velocity', ), timeout = 3, message = MGMSG_MOT_REQ_HOMEPARAMS(chan_ident = self._chan_ident))
        return self._state_home_velocity / (self._EncCnt * self._T * 65536)
    
    @property
    def home_dir(self):
        """
        Returns direction of homing.
        
        Returns
        -------
        out : int 
            homing direction
            
        Information
        -----------
        direction : int
            home in forward or reverse direction:
            - HOME_FWD = 1 : Home in the forward direction.
            - HOME_REV = 2 : Home in the reverse direction.
            
        """
        self._wait_for_properties(('_state_home_direction', ), timeout = 3, message = MGMSG_MOT_REQ_HOMEPARAMS(chan_ident = self._chan_ident))
        return self._state_home_direction
            
    @property
    def home_dir_str(self):
        """
        Returns direction of homing.
        
        Returns
        -------
        out : str 
            homing direction
            
        Information
        -----------
        direction : int
            home in forward or reverse direction:
            - HOME_FWD = 1 : Home in the forward direction.
            - HOME_REV = 2 : Home in the reverse direction.
            
        """
        self._wait_for_properties(('_state_home_direction', ), timeout = 3, message = MGMSG_MOT_REQ_HOMEPARAMS(chan_ident = self._chan_ident))
        if self._state_home_direction == 1:
                return 'forward'
        if self._state_home_direction == 2:
                return 'reverse'
    
    @property
    def home_limit_switch(self):
        """
        Returns limit switch for homing.
        
        Returns
        -------
        out : float
            limit switch
            
        Information
        -----------
        limiting switch : int
            forward limit switch or reverse limit switch:
            - HOMELIMSW_FWD = 4 : Use forward limit switch for home datum.
            - HOMELIMSW_REV = 1 : Use reverse limit switch for home datum.
            
        """
        self._wait_for_properties(('_state_home_limit_switch', ), timeout = 3, message = MGMSG_MOT_REQ_HOMEPARAMS(chan_ident = self._chan_ident))
        return self._state_home_limit_switch
    
    @property
    def home_offset_dist(self):
        """
        Returns offset distance for homing.
        
        Returns
        -------
        out : float
            offset distance
            
        """
        self._wait_for_properties(('_state_home_offset_distance', ), timeout = 3, message = MGMSG_MOT_REQ_HOMEPARAMS(chan_ident = self._chan_ident))
        return self._state_home_offset_distance / self._EncCnt
    
    @property
    def home_zero_offset_dist(self):
        """
        Returns zero offset distance for homing.
        
        Returns
        -------
        out : float
            zero offset distance
            
        """
        return self._conf_home_zero_offset
    
    @property
    def get_move_home_params(self):
        """
        Returns parameters used for homing.
        
        Returns
        -------
        out : tuple
            (direction, limiting switch, velocity, zero offset)
            
        Information
        -----------
        direction : int
            home in forward or reverse direction:
            - HOME_FWD = 1 : Home in the forward direction.
            - HOME_REV = 2 : Home in the reverse direction.
        limiting switch : int
            forward limit switch or reverse limit switch:
            - HOMELIMSW_FWD = 4 : Use forward limit switch for home datum.
            - HOMELIMSW_REV = 1 : Use reverse limit switch for home datum.
        velocity : float
            homing velocity of the motor.
        home_offset_distance : float
            zero offset by default.
            
        """
        direction =   self._conf_home_dir
        lim_switch =  self._conf_home_limit_switch
        velocity =    self._conf_home_vel
        zero_offset = self._conf_home_zero_offset
        
        return (direction.value, lim_switch.value, velocity.value,
                zero_offset.value)
    
    def set_home_vel(self, new_value):
        """
        Sets homing velocity
        
        Parameters
        ----------
        new_value : float or int
            homing velocity of the motor
            
        """
        self.set_home_params(new_value, self.home_dir, self.home_limit_switch, self._conf_home_zero_offset)
    
    def set_home_dir(self, new_value):
        """
        Sets homing direction
        
        Parameters
        ----------
        new_value : int
            home in forward or reverse direction:
            - HOME_FWD = 1 : Home in the forward direction.
            - HOME_REV = 2 : Home in the reverse direction.
            
        """
        self.set_home_params(self.home_vel, new_value, self.home_limit_switch, self._conf_home_zero_offset)
        
    def set_limit_switch(self, new_value):
        """
        Sets homing limit switch
        
        Parameters
        ----------
        new_value : int
            forward limit switch or reverse limit switch:
            - HOMELIMSW_FWD = 4 : Use forward limit switch for home datum.
            - HOMELIMSW_REV = 1 : Use reverse limit switch for home datum.
            
        """
        self.set_home_params(self.home_vel, self.home_dir, new_value, self._conf_home_zero_offset) 
    
    def set_home_params(self, home_velocity, home_direction, home_limit_switch, home_offset_distance = None):
        """
        Sets parameters used when homing.
        
        Parameters
        ----------
        home_direction : int
            home in forward or reverse direction:
            - HOME_FWD = 1 : Home in the forward direction.
            - HOME_REV = 2 : Home in the reverse direction.
        home_limit_switch : int
            forward limit switch or reverse limit switch:
            - HOMELIMSW_FWD = 4 : Use forward limit switch for home datum.
            - HOMELIMSW_REV = 1 : Use reverse limit switch for home datum.
        home_velocity : float or int
            homing velocity of the motor
        home_offset_distance : float
            offset distance (setting new value for homing offset distance
            is not recommended)
            Default: None.
            
        """
        if isinstance(home_velocity,(int,float)):
            try:
                assert (home_velocity > self._conf_def_min_vel) and (home_velocity < self._conf_max_vel)
            except AssertionError:
                print('Oops! Try a different value for homing velocity and it should be within [{0},{1}] {2}/s'. \
                      format(float(self._conf_def_min_vel),self._conf_max_vel,self.units))
                home_velocity = self.home_vel
        else:
            raise TypeError('Velocity value must be an integer or a float')
                
        if isinstance(home_direction,int):
            try:
                assert (home_direction == 1) or (home_direction == 2)
            except AssertionError:
                print('Oops! Try a different value for homing direction and it should be either {0} or {1}'. \
                      format(1,2))
                home_direction = self.home_dir
        else:
            raise TypeError('Direction value must be an integer')
                
        if isinstance(home_limit_switch,int):
            try:
                assert (home_limit_switch == 1) or (home_limit_switch == 4)
            except AssertionError:
                print('Oops! Try a different value for homing limit switch and it should be either {0} or {1}'. \
                      format(1,4))
                home_limit_switch = self.home_limit_switch
        else:
            raise TypeError('Limit switch value must be an integer')
        
        if home_offset_distance is None:
            home_offset_distance = self._conf_home_zero_offset
        else:
            home_offset_distance = home_offset_distance
                
        msg = MGMSG_MOT_SET_HOMEPARAMS( 
            chan_ident = self._chan_ident,
            home_velocity = int(home_velocity *(self._EncCnt * self._T * 65536)),
            home_direction = home_direction,
            limit_switch = home_limit_switch,
            offset_distance = int(home_offset_distance*self._EncCnt)
        )
        self._port.send_message(msg)
        #Invalidate current values
        self._state_home_velocity = None
        self._state_home_direction = None
        self._state_home_limit_switch = None
        self._state_home_offset_distance = None
        
    def move_home(self, blocking = False):
        '''
        Move to home position, i.e. position = 0 mm.
        
        Parameters
        ----------
        blocking: bool
            not wait until homing is completed.
            Default: False
            
        See also
        --------
        home_check
            
        '''
        if self.pos == 0:
            return None
        else:
            
            self._port.send_message(MGMSG_MOT_MOVE_HOME(chan_ident = self._chan_ident))
            # we make sure that the controller waits until homing is completed by adding an
            # 'if' loop to call property home_check.
            if not blocking:
                check_homed = self.home_check
                if check_homed:
                    return None
            
#####  SYSTEM PARAMETERS  ###############################################################################################
            
    @property
    def ser_no(self):
        """
        Returns the serial number of the motor.
        
        Returns
        -------
        out : int
            serial number
            
        """
        return self._extr_str[1]
    
    @property
    def ser_port(self):
        """
        Returns the serial port entry of the motor.
        
        Returns
        -------
        out : str
            serial port entry
            
        """
        return self._extr_str[0]
    
    @property
    def stage_model(self):
        """
        Returns the stage model.
        
        Returns
        -------
        out : str
            stage model
            
        """
        return self._name

    def status_bits(self,conversion = False):
        """
        Returns status bits of motor.
        
        Parameters:
        -----------
        conversion  : bool
            convert output integer from base 10 to base 16
            Default: False
        
        Returns
        -------
        out : (int)
            status bits in base 10 if False
              (str)
            status bits in base 16 if True
            
        """
        if not conversion:
            return self._state_status_bits
        else:
            return hex(self._state_status_bits)

#####  CONVERSION FACTORS  ##############################################################################################
        
    # Factor 1: EncCnt - a scaling factor. In motion controllers, however, normally the system only
    # knows the distance travelled in encoder counts (pulses) as measured by an encoder fitted
    # to the motor shaft. In most cases the motor shaft rotation is also scaled down further by a
    # gearbox and a leadscrew. In any case, the result is a scaling factor between encoder counts and
    # position. The value of this scaling factor depends on the stage. This scaling factor is represented
    # by the symbol EncCnt.
    
    @property
    def _EncCnt(self):
        '''
        Returns position-related scaling factor.
        
        Returns
        -------
        out : float
            scaling factor for position conversion
            
        Information
        -----------
        In motion controllers, however, normally the system
        only knows the distance travelled in encoder counts (pulses)
        (pulses) as measured by an encoder fitted to the motor shaft.
        In most cases the motor shaft rotation is also scaled down
        further by a gearbox and a leadscrew. In any case, the result
        is a scaling factor between encoder counts and position. The
        value of this scaling factor depends on the stage. This scaling
        factor is represented by the symbol EncCnt.

        '''
        return self._conf_steps_per_rev * self._conf_gearbox_ratio / self._conf_pitch
    
    # Factor 2: T
    # Time is related to the sampling interval of the system, and as a result, it depends on the motion
    # controller. Therefore, this value is the same for all stages driven by a particular controller.
    # The sampling interval is denoted by T.
    
    @property
    def _T(self):
        '''
        Returns time-related scaling factor.
        
        Returns
        -------
        out : float
            scaling factor for velocity and acceleration
            conversion
            
        Information
        -----------
        Time is related to the sampling interval of the
        system, and as a result, it depends on the motion
        controller. Therefore, this value is the same for
        all stages driven by a particular controller. The
        sampling interval is denoted by T.

        '''
        return 2048 / 6e6
    
    # factor 3: unit index
    @property
    def units(self):
        '''
        Returns unit of position.
        
        Returns
        -------
        out : str
            - 'mm' 
            - '°' if in degrees

        '''
        return {1: 'mm', 2: '°'}[self._conf_units]   


    def _wait_for_properties(self, properties, timeout = None, message = None, message_repeat_timeout = None):
        start_time = time.time()
        last_message_time = 0
        while any(getattr(self, prop) is None for prop in properties):
            if message is not None:
                if last_message_time == 0 or (message_repeat_timeout is not None and time.time() - last_message_time > message_repeat_timeout):
                    self._port.send_message(message)
                    last_message_time = time.time()
            time.sleep(0.1)
            if timeout is not None and time.time() - start_time >= timeout:
                return False
        return True
    
    def __del__(self):
        '''
        This function is a finalizer. It is called when an object is garbage
        collected when happens at some point after all references to the
        object have been deleted.
        
        '''
        print("Destructed: {0!r}".format(self._name))
        
    def __repr__(self):
        return '{0!r}'.format(self._port)
        

#Message which should maybe be implemented?
#Should be in port: MGMSG_HUB_REQ_BAYUSED, MGMSG_HUB_GET_BAYUSED,
#Really useful? MGMSG_MOT_SET_POSCOUNTER, MGMSG_MOT_REQ_POSCOUNTER, MGMSG_MOT_GET_POSCOUNTER, MGMSG_MOT_SET_ENCCOUNTER, MGMSG_MOT_REQ_ENCCOUNTER, MGMSG_MOT_GET_ENCCOUNTER, 
#MGMSG_MOT_SET_JOGPARAMS, MGMSG_MOT_REQ_JOGPARAMS, MGMSG_MOT_GET_JOGPARAMS, MGMSG_MOT_SET_GENMOVEPARAMS, MGMSG_MOT_REQ_GENMOVEPARAMS, MGMSG_MOT_GET_GENMOVEPARAMS, MGMSG_MOT_SET_MOVERELPARAMS, MGMSG_MOT_REQ_MOVERELPARAMS, MGMSG_MOT_GET_MOVERELPARAMS, MGMSG_MOT_SET_MOVEABSPARAMS, MGMSG_MOT_REQ_MOVEABSPARAMS, MGMSG_MOT_GET_MOVEABSPARAMS, MGMSG_MOT_SET_HOMEPARAMS, MGMSG_MOT_REQ_HOMEPARAMS, MGMSG_MOT_GET_HOMEPARAMS, MGMSG_MOT_SET_LIMSWITCHPARAMS, MGMSG_MOT_REQ_LIMSWITCHPARAMS, MGMSG_MOT_GET_LIMSWITCHPARAMS, MGMSG_MOT_MOVE_HOME, MGMSG_MOT_MOVE_HOMED, MGMSG_MOT_MOVE_RELATIVE_short,MGMSG_MOT_MOVE_RELATIVE_long, MGMSG_MOT_MOVE_COMPLETED, MGMSG_MOT_MOVE_ABSOLUTE_short,MGMSG_MOT_MOVE_ABSOLUTE_long, MGMSG_MOT_MOVE_JOG, MGMSG_MOT_MOVE_VELOCITY, MGMSG_MOT_MOVE_STOP, MGMSG_MOT_MOVE_STOPPED, MGMSG_MOT_SET_DCPIDPARAMS, MGMSG_MOT_REQ_DCPIDPARAMS, MGMSG_MOT_GET_DCPIDPARAMS, MGMSG_MOT_SET_AVMODES, MGMSG_MOT_REQ_AVMODES, MGMSG_MOT_GET_AVMODES, MGMSG_MOT_SET_POTPARAMS, MGMSG_MOT_REQ_POTPARAMS, MGMSG_MOT_GET_POTPARAMS, MGMSG_MOT_SET_BUTTONPARAMS, MGMSG_MOT_REQ_BUTTONPARAMS, MGMSG_MOT_GET_BUTTONPARAMS, MGMSG_MOT_SET_EEPROMPARAMS, MGMSG_MOT_REQ_DCSTATUSUPDATE, MGMSG_MOT_GET_DCSTATUSUPDATE, MGMSG_MOT_ACK_DCSTATUSUPDATE, MGMSG_MOT_REQ_STATUSBITS, MGMSG_MOT_GET_STATUSBITS, MGMSG_MOT_SUSPEND_ENDOFMOVEMSGS, MGMSG_MOT_RESUME_ENDOFMOVEMSGS
