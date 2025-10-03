"""

Input User Query, Type of  feature, 
Extract features and keywords based on Query Type
Make the initial context here
Pass on to Federator with context 

"""

# Different features will have different flows, contexts and decomposers
# But all will have same Query Manager, Federator and Executor 

"""
For each feature we will have a FLOW defined in flow.py
For each step in the flow we will have a function defined in steps.py
For each feature we will have a context defined in context.py
For each feature we will have a decomposer defined in decompose.py
"""