# Modify Container Tags

## Purpose
The purpose of this gear is to rapidly and easily manipulate tags on containers within
flywheel without requiring SDK knowledge.  

## Use Cases
The gear has two primary use cases:

1. **Single File Input**: (Incomplete) modifies the tag of the file's parent acquisition.
Currently, in Flywheel files cannot be tagged, so parent acquisition will have to do.

![FileRun](/src/FileRun.png)

   * The intended use case for this mode is as a gear rule to automatically tag acquisitions
    of incoming files.  API permissions are currently preventing this gear from being used 
    as a rule.  Future implementations will attempt to modify tags using the metadata.json file
    to overcome this.  
    

    
2. **Bulk Container Input**: (Complete) Uses a series of configuration settings to select 
a subset of containers for tag modification.

![ConfigRun](/src/ConfigRun.png)

As use case 1 is currently broken, we will focus on 2:

## Bulk Container Input

A single container or group of containers is selected using a series of config settings.
The configuration settings are broken into 5 sections:

***A***: Section A specifies the type of tag modification you would like to make.


***B***: Section B specifies the Tags you would like to add or remove.  


***C***: Section C specifies containers to operate on.  To modify multiple containers at once,
a list of IDs can be passed in, separated with spaces or commas.  


***D***: Section D modifies the containers specified in section C.  By selecting options here,
the gear will no longer operate on the container(s) specified in C, but will instead operate
on the specific child type of container specified here. 


***E***: Section E Allows the user to provide a query to filter their results by.  Only containers 
that would return `True` for the query conditions are modified.  This allows the user to 
easily re-tag every subject in a project that matches a certain condition.

### Section A

Section A specifies the type of tag modification you would like to make.
   * **Action**: The action to perform on the tags.  Can be one of four actions:
        1. *Append Tag* : Adds the specified tag(s) to the selected container(s).
        1. *Remove Tag* : Removes the specified tag(s) from the selected container(s) if
        they have the tag(s).
        1. *Remove and Append*: Remove ALL tag(s) from the selected container(s), and 
        appends the specified tag(s).
        1. *Remove All*: Removes ALL tag(s) from the selected container(s).


### Section B

Section B specifies the Tags you would like to add or remove.  
   * **Tags**: A single tag or list of tags (comma or space separated) to perform the 
   specified action with.  Tags cannot be specified if the action is `Remove All`
   
### Section C
Section C specifies containers to operate on.  To modify multiple containers at once,
a list of IDs can be passed in, separated with spaces or commas.  
    
    EXAMPLE:
    We wish to add the tag "unprocessed" to two sessions.  We would configure the gear
    with the following settings:
    
    A - Action:  "Append Tag"
    B - Tags:    "Unprocessed"
    C - Subject: "<SUBJECT_CONTAINER_ID>"
   

ADDITIONALLY, the options
in section D can be used to specify that the gear should operate on all child containers 
of a certain type.  This means that rather than pass in every subject's container ID,
you can simply pass in the project path, and use section D to instruct the gear that you 
would like to modify tags on all child subjects of the containers provided here in section C.

   * **Project Path**: Flywheel Path (group/project) to a specified project to perform 
   tagging actions on.  If no options from section
   D are checked, then the gear will attempt to tag the project specified here. Can be 
   a list of projects separated by a comma or space

   * **Subject**: A container ID for to specify a subject to perform tagging actions on.
   If no options from section D are checked, the gear will attempt to tag only the subject
   containers specified here.  Can be a list of subject container ID's separated by a comma
   or space.

   * **Session**: A container ID for to specify a session to perform tagging actions on.
   If no options from section D are checked, the gear will attempt to tag only the session
   containers specified here.  Can be a list of session container ID's separated by a comma
   or space.   
   
   * **Acquisition**: A container ID for to specify a session to perform tagging actions on.
   If no options from section D are checked, the gear will attempt to tag only the acquisition
   containers specified here.  Can be a list of acquisition container ID's separated by a comma
   or space.   
   

### Section D

Section D modifies the containers specified in section C.  By selecting options here,
the gear will no longer operate on the container(s) specified in C, but will instead operate
on the specific child type of container specified here. 

    EXAMPLE:
    As in the example  above, let's now assume that we wish to append the tag 
    "Unprocessed" to ALL the sessions in the project with the flywheel path:
    "my_group/my_project"
    
    Method 1 (Incorrect):
    We COULD pass in every session ID in section B:
    
    A - Action:  "Append Tag"
    B - Tags:    "Unprocessed"
    C - Subject: "<SESSION_CONTAINER_ID_1>, <SESSION2_CONAINER_ID_2>, ...  <SESSION2_CONAINER_ID_X>"    
    
    But that could take a LONG time... 
    Instead we can use the "Process Child Sessions" option in section D.  To acieve this,
    we want to make sure we specify a container that is a parent to ALL the sessions we'd
    like to modify.  For example, we can't just pass in one subject ID and select 
    "Process Child Sessions", because that would only process the sessions belonging to
    the specified subject.  
    
    To modify ALL sessions in a project, we pass in the project path in section B, and
    select "Process Child Sessions" here in section D:
    
    Method 2 (Correct):
    A - Action:  "Append Tag"
    B - Tags:    "Unprocessed"
    C - Project: "my_group/my_project"
    D - Projcess Child Subjects: True    

NOTE1: when you use these options, the gear NO LONGER attempts to modify the tags on the container(s)
specified in section C.  ANY and ALL containers in section C are only used to find children
containers if any options are selected in this section.

NOTE2: ALL the containers specified in section C MUST at least in theory be able to have
the child container type specified here.  For example, you can't pass in a session in 
section C, and then select "Process Child Subjects" in section B, because a session cannot
have a child subject, only child acquisitions and analyses.  You must respect the Flywheel
Hierarchy.


   * **Process Child Subjects**: Process all children subjects of the container(s) specified
   In section C.  

   * **Process Child Sessions**: Process all children sessions of the container(s) specified
   In section C.

   * **Process Child Acquisitions**: Process all children acquisitions of the container(s)
   specified.

   * **Process Child Analyses**: Procjess all children Analyses of the contaier(s) specified.
   
   NOTE: Only immediate children analyses will be modified.  For example, if a subject ID 
   is provided in section C, and "Process Child Analyses" is `True`, ONLY the analyses 
   at the subject level will be modifed, even if the subject has sessions that also have
   analyses

### Section E

Section E Allows the user to provide a query to filter their results by.  Only containers 
that would return `True` for the query conditions are modified.  This allows the user to 
easily re-tag every subject in a project that matches a certain condition.

    EXAMPLE:
    The user wishes to tag all subjects over the age of 50 as "Old".  The following
    configuration settings can be used:
    
    A - Action:  "Append Tag"
    B - Tags:    "Old"
    C - Project: "my_group/my_project"
    D - Projcess Child Subjects: True  
    E - Query: "session.age_in_years > 50" 
    
    The gear is clever enough to find subjects who have a session that matches this criteria.
    





