import logging
import re
import sys

import flywheel
import flywheel_gear_toolkit


log = logging.getLogger(__name__)


def process_tag(tag):

    if tag is None:
        tag = ''

    try:
        tag = str(tag)
    except Exception as e:
        log.exception(e)

    return(tag)


def validate_tag(tag):

    if not isinstance(tag, str):
        log.error(f"tag {tag} is not of type str despite conversion attempt")
        return(False)

    if tag == '':
        log.error(f"tag cannot be empty.")
        return(False)

    return(True)


def remove_all_tags(container):
    
    log.info(f'Removing all tags from container {container.label}')
    container_tags = container.get('tags')
    log.debug(f'tags:{container_tags}')
    if container_tags:
        for tag in container_tags:
            log.debug(f'Deleting tag {tag}')
            container.delete_tag(tag)
    container = container.reload()

    return(container)

def add_tag(container, tag, exist_ok=True):
    if container.container_type == 'file':
        container.label = container.name
    log.info(f'Adding tag {tag} to container {container.label}')
    # If the tag is already there but it's ok, return the container
    if container.get('tags') is None:
        container.add_tag(tag)
        
    elif tag in container.get('tags') and exist_ok:
        return(container)
    # Otherwise, try to add the tag.  it will either add it or raise an exception
    else:
        container.add_tag(tag)
        container = container.reload()
    return(container)


def remove_tag(container, tag):
    log.info(f'Removing tag {tag} from container {container.label}')
    container.delete_tag(tag)
    container = container.reload()
    return(container)


def modify_container_tag(container, tag, action='Append'):

    log.debug(f'attempting to add tag {tag} to container {container.get("name")}{container.get("label")}')
    
    if action == 'Append Tag' or action == 'Remove and Append':
        tag = process_tag(tag)

        if not validate_tag(tag):
            raise Exception(f"tag {tag} is invalid and cannot be appended")

        if action == 'Remove and Append':
            container = remove_all_tags(container)

        container = add_tag(container, tag)

    elif action == 'Remove Tag':
        container = remove_tag(container, tag)

    elif action == 'Remove All':
        container = remove_all_tags(container)

    else:
        log.error(f"Unknown action {action}")
        raise Exception(f"Unknown action {action}")

    return(container)


def get_container(fw, container_id, container_level):
    
    log.debug(f'container id: {container_id}')
    
    if container_level == 'project':
        try:
            if '/' in container_id:
                log.debug('detected path, using lookup')
                container = fw.lookup(container_id)
                container = container.reload()
            else:
                log.debug('detected ID, using fw.get_project()')
                container = fw.get_project(container_id)
        except Exception as e:
            container = fw.get(container_id)
            container_type = container.container_type
            log.error(f"container {container_id} was passed in as a {container_level}, "
                      f"but is container type {container_type}")
            raise (e)

    elif container_level == 'subject':
        try:
            container = fw.get_subject(container_id)
        except Exception as e:
            container = fw.get(container_id)
            container_type = container.container_type
            log.error(f"container {container_id} was passed in as a {container_level}, "
                      f"but is container type {container_type}")
            raise (e)

    elif container_level == 'session':
        try:
            container = fw.get_session(container_id)
        except Exception as e:
            container = fw.get(container_id)
            container_type = container.container_type
            log.error(f"container {container_id} was passed in as a {container_level}, "
                      f"but is container type {container_type}")
            raise (e)

    elif container_level == 'acquisition':
        try:
            container = fw.get_acquisition(container_id)
        except Exception as e:
            container = fw.get(container_id)
            container_type = container.container_type
            log.error(f"container {container_id} was passed in as a {container_level}, "
                      f"but is container type {container_type}")
            raise (e)

    elif container_level == 'file':
        # This becomes complicated now.
        # I don't think I'm implementing any "Set this specific file's tag".
        # I think the purpose is to process CHILD files of subjects/sessions, etc.
        try:
            container = None
        except:
            container = None

    else:
        log.error(f"Unknown container type {container_level}")
        raise Exception(f"Unknown container type {container_level}")

    return(container)


def get_subcontainers(fw, container, container_level, sc_level, query=None, child_file_filter=None):
    
    if query is not None and query is not "":
        query = f"{container_level}._id = {container.id} AND {query}"
        log.debug(f'Querrying: {query}')
        sq = {'structured_query': query, 'return_type': sc_level}
        log.debug(sq)
        results = fw.search(sq, size=10000)
        sub_containers = [fw.get(r[r.return_type].id) for r in results]

    else:
        if sc_level == 'subject':
            sub_containers = container.subjects(limit=10000)
        elif sc_level == 'session':
            sub_containers = container.sessions(limit=10000)
        elif sc_level == 'acquisition':
            if container_level == 'project':
                sub_containers = fw.acquisitions.find(f"project={container.id}", limit=10000)
            elif container_level == 'subject':
                sub_containers = fw.acquisitions.find(f"subject={container.id}", limit=10000)
            else:
                sub_containers = container.acquisitions(limit=10000)
        elif sc_level == 'analysis':
            sub_containers = container.analyses

        elif sc_level == 'file':
            sub_containers = container.files

            if child_file_filter:
                sub_containers = [sc for sc in sub_containers if re.match(child_file_filter, sc.name)]


        else:
            sub_containers = []
    
    log.debug(f'Number of containers: {len(sub_containers)}')
    return(sub_containers)



def process_containers(fw, container_level, process_subcontainers, container_id,
                       original_action, tags, query=None, child_file_filter=""):
    
    log.debug(f"container_level: {container_level}")
    log.debug(f"process_subcontainers: {process_subcontainers}")
    log.debug(f"container_id: {container_id}")
    log.debug(f"original_action: {original_action}")
    log.debug(f"tags: {tags}")
    log.debug(f"container_level: {container_level}")
    log.debug(f"query: {query}")
    log.debug(f"child file filter: {child_file_filter}")

    container = get_container(fw, container_id, container_level)

    if 'file' in process_subcontainers:
        file_level_present = True
    else:
        file_level_present = False

    if process_subcontainers == ['self']:
        if original_action == 'Remove All':
            modify_container_tag(container, None, original_action)
        else:
            action = original_action
            for tag in tags:
                modify_container_tag(container, tag, action)
                if original_action == 'Remove and Append':
                    action = 'Append'

    else:
        log.debug(f'proces_subcontainers: {process_subcontainers}')


        for sc_level in process_subcontainers:
            
            if sc_level != 'self':
            
                sub_containers = get_subcontainers(fw, container, container_level, sc_level, query, child_file_filter)
            
                if sub_containers is None:
                    continue

                if sc_level != 'file' and file_level_present:
                    log.debug(f'Getting files on level {sc_level} for processing')
                    sub_containers_files = []
                    for sub_container in sub_containers:
                        sub_container_level = sub_container.container_type
                        sub_container_files = get_subcontainers(fw, sub_container, sub_container_level, 'file', query, child_file_filter)
                        sub_containers_files.extend(sub_container_files)
                    log.debug(f'found {len(sub_containers_files)} files for processing')
                    sub_containers = sub_containers_files

                log.debug('MADE IT HERE')
                log.debug(sub_containers)
                for sub_container in sub_containers:
                    log.debug(f'looping through subcontainer, processing {sub_container.get("name")}{sub_container.get("label")}')

                    sub_container = sub_container.reload()
                    action = original_action
                    if action == 'Remove All':
                        modify_container_tag(sub_container, None, action)
                    else:
                        for tag in tags:
                            modify_container_tag(sub_container, tag, action)
                            if original_action == 'Remove and Append':
                                action = 'Append'