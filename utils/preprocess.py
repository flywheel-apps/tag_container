import logging
import re


log = logging.getLogger(__name__)


def get_tag_list(config):
    tags = config.get('B-Tags')
    if tags:
        tags = re.split(",| ", tags)
    return(tags)


def get_container_ids_from_config(config):
    name2container = {'project': 'C-Project Path',
                      'subject': 'C-Subject',
                      'session': 'C-Session',
                      'acquisition': 'C-Acquisition'}
    
    container_dict = {}
   
    for container in name2container:
        container_ids = config.get(name2container[container])

        if container_ids is not None:
            container_ids = re.split(",| ", container_ids)

        container_dict[container] = container_ids
    log.debug(container_dict)
    return (container_dict)


def get_container_level(config):
    if config.get('C-Acquisition'):
        level = 'acquisition'
    elif config.get('C-Session'):
        level = 'session'
    elif config.get('C-Subject'):
        level = 'subject'
    elif config.get('C-Project Path'):
        level = 'project'
    else:
        log.info('No Level Detected')
        level = 'None'
        print(config)
    return (level)


def get_subcontainers_to_process(config):
    containers_to_process = ['self']
    if config.get('D-Process Child Subjects'):
        containers_to_process.append('subject')
    if config.get('D-Process Child Sessions'):
        containers_to_process.append('session')
    if config.get('D-Process Child Acquisitions'):
        containers_to_process.append('acquisition')
    if config.get('D-Process Child Analyses'):
        containers_to_process.append('analysis')

    return (containers_to_process)


def validate_container_inputs(container_level, process_subcontainers, container_ids, action, tags):
    valid = True

    # First see if the container level we're at has been specified as a sub-container
    # For example, the user specifies a session ID, and then checks "Process Child Sessions"
    # also check if sub-containers ABOVE the container level are checked:
    if container_level == 'acquisition':
        parents = ['session', 'subject', 'acquisition', 'analyses']
        if any([parent in process_subcontainers for parent in parents]):
            log.error('Cannot process sub-containers session/subject/acquisition/analyses'
                      ' for container acquisition')
            valid = False

    elif container_level == 'session':
        parents = ['subject', 'session']
        if any([parent in process_subcontainers for parent in parents]):
            log.error('Cannot process sub-containers session/subject for container session')
            valid = False

    elif container_level == 'subject':
        parents = ['subject']
        if any([parent in process_subcontainers for parent in parents]):
            log.error('Cannot process sub-containers subject for container subject')
            valid = False

    # Check if multiple container IDs are filled out
    if len([True for val in container_ids.values() if val is not None]) > 1:
        log.error('Multiple container levels are provided- Only one level '
                  '(Project, Subject, Session, or Acquisition), may have IDs.')
        log.debug(container_ids)
        valid = False
        
    if action != 'Remove All':
        if tags is None:
            log.error('Tag must be provided if action is not "Remove all"')
            valid = False
    else:
        if tags is not None:
            log.error('Tag cannot be present for the "remove all" function.  Did you mean remove and append?')
            valid = False
    

    return (valid)




