import sys

def _print_stage_detection_improve_message(m):
    print('If you see this message, please send a mail with the following information: \n' + \
          '- controller type\n' + \
          '- stage type\n' + \
          '- this data: {0}'.format(m), file = sys.stderr)

def stage_name_from_get_hw_info(m):
    controller_type = m['serial_number'] // 1000000  #v7
    stage_type = m['empty_space'][-2]  #Reverse engineered
    hw_version = m['hw_version']
    model_number = m['model_number'].decode('ascii').strip('\x00')
    if controller_type in (60, 80):
        if hw_version == 3:
            return 'HS ZST6(B)'
        else:
            return 'ZST6(B)'
    elif controller_type in (27, 63, 83, 2197):
        #Info obtained from thorlabs technical support
        if stage_type == 0x01:
            _print_stage_detection_improve_message(m)
            return None  #Open circuit - no motor connected.
        elif stage_type == 0x02:
            return 'Z706'
        elif stage_type == 0x03:
            return 'Z712'
        elif stage_type == 0x04:
            return 'Z725'
        elif stage_type == 0x05:
            return 'CR1-Z7'
        elif stage_type == 0x06:
            return 'PRM1-Z8'
        elif stage_type == 0x07:
            return 'MTS25-Z8'
        elif stage_type == 0x08:
            return 'MTS50-Z8'
        elif stage_type == 0x09:
            return 'Z825'
        elif stage_type == 0x0A:
            return 'Z812'
        elif stage_type == 0x0B:
            return 'Z806'
        elif stage_type == 0x0C:
            _print_stage_detection_improve_message(m)
            return None  #Non Thorlabs motor.
        else:
            #This is reverse engineered...
            _print_stage_detection_improve_message(m)
            return 'Z606(B)'
    elif controller_type in (43, 93):
        return 'DRV414'
    elif controller_type in (94, ):
        if stage_type == 16:
            return 'MLS203 X'
        elif stage_type == 17:
            return 'MLS203 Y'
        _print_stage_detection_improve_message(m)
        return None
    elif controller_type in (45, ):
        if model_number == 'LTS150':
            return 'HS LTS150 150mm Stage'
        elif model_number == 'LTS300':
            return 'HS LTS300 300mm Stage'
        _print_stage_detection_improve_message(m)
        return None

    elif controller_type in (46, ):
        return "L490MZ Labjack"
    elif controller_type in (47, ):
        return "FW105 Filter Wheel"
    elif controller_type in (55, ):
        return "K100CR1 Rotation Stage"
    elif controller_type in (49, ):
        return "MLJ050 Labjack"
    elif controller_type in (37, ):
        return "MFF Filter Flipper"
    elif controller_type in (67, ):
        if stage_type == 20:
            return 'MVS005MZ'
        else:
            _print_stage_detection_improve_message(m)
            return 'DDSM100'
    else:
        _print_stage_detection_improve_message(m)
        return None