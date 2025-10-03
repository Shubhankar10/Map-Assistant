# Orchestrator

"""
Base class to make generic federator which can call different APIs based on context and query type.

Input Context from Decomposer
Fetch Flow for the feature, 

Call each step for  the feature in sequence
Manage context with each step
Return final response

Mainly gather data from different APIs and combine them step by step

Last mai execute bhi toh ho he raha hai, final output bhi toh aajayeg steps complete hone ke baad

Federate kar k steps ko context k saath execute ko pass kar sakte
FLOW mai federate steps and execute steps alag rakh sakte hai, toh pehale federate hoke context build ho jayega phir execute hoke final output ayega
--------------------------------------------------------
Orchestrator class often combines both roles
Federation is about “planning”: what steps, in what sequence, which parameters, which branches.

Execution is about “doing”: actually invoking each step, handling outputs, retries, and updating the Context.

"""


"""
Lastly make a user k liye output from the final context.
"""