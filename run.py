import logging
import re
import sys

import flywheel
import flywheel_gear_toolkit

import utils.container_tags as ct
import utils.preprocess as pr

log = logging.getLogger(__name__)


def main(fw, gear_context):

    container_level = pr.get_container_level(gear_context.config)
    process_subcontainers = pr.get_subcontainers_to_process(gear_context.config)
    container_ids = pr.get_container_ids_from_config(gear_context.config)
    tag_list = pr.get_tag_list(gear_context.config)
    action = gear_context.config.get('A-Action')
    query = gear_context.config.get('E-Query')
    
    if not pr.validate_container_inputs(container_level, process_subcontainers, container_ids, action, tag_list):
        log.info('Initial validation failed.  Invalid Configuration.  See log to fix inputs.')
        sys.exit(1)
    
   
    container_ids = container_ids[container_level]
    
    for container in container_ids:
        ct.process_containers(fw, container_level, process_subcontainers, container,
                       action, tag_list, query)
    
    exit_status = 0
    return(exit_status)


def run_one(fw, context):
    exit_status = 0
    try:
        parent_acq = gear_context.get_input("file")["hierarchy"].get("id")
        acq = fw.get_acquisition(parent_acq)
        tag_list = pr.get_tag_list(gear_context.config)
        action = gear_context.config.get('A-Action')
        
        if action == 'Remove All':
            ct.modify_container_tag(acq, None, action)
        else:
            for tag in tag_list:
                ct.modify_container_tag(acq, tag, action)
                if action == 'Remove and Append':
                    action = 'Append'
    except Exception as e:
        log.exception(e)
        exit_status = 1
        
    return(exit_status)
                

if __name__ == "__main__":

    
    
    with flywheel_gear_toolkit.GearToolkitContext(config_path='/flywheel/v0/config.json') as gear_context:
        gear_context.config['debug_gear'] = True
        gear_context.init_logging()

        fw = flywheel.Client(gear_context.get_input("api_key")["key"])
        
        if gear_context.get_input("file") is not None:
            exit_status = run_one(fw, gear_context)
        else:
            exit_status = main(fw, gear_context)
            
    if exit_status != 0:
        log.error('Failed')
        sys.exit(exit_status)
        
    log.info(f"Successful dicom-send gear execution with exit status {exit_status}.")
