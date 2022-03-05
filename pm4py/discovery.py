import warnings
from typing import Tuple, Union, List, Dict, Any, Optional

import pandas as pd
from pandas import DataFrame

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.obj import EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, xes_constants, __event_log_deprecation_warning
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import constants


def discover_dfg(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[dict, dict, dict]:
    """
    Discovers a DFG from a log

    Parameters
    --------------
    log
        Event log
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.util import constants

        from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_dfg_graph
        activity_key = properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in properties else xes_constants.DEFAULT_NAME_KEY
        timestamp_key = properties[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in properties else xes_constants.DEFAULT_TIMESTAMP_KEY
        case_id_key = properties[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in properties else constants.CASE_CONCEPT_NAME
        dfg = get_dfg_graph(log, activity_key=activity_key,
                            timestamp_key=timestamp_key,
                            case_id_glue=case_id_key)
        from pm4py.statistics.start_activities.pandas import get as start_activities_module
        from pm4py.statistics.end_activities.pandas import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    else:
        from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
        dfg = dfg_discovery.apply(log, parameters=properties)
        from pm4py.statistics.start_activities.log import get as start_activities_module
        from pm4py.statistics.end_activities.log import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    return dfg, start_activities, end_activities


def discover_directly_follows_graph(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[dict, dict, dict]:
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    return discover_dfg(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)


def discover_performance_dfg(log: Union[EventLog, pd.DataFrame], business_hours: bool = False, worktiming: List[int] = [7, 17], weekends: List[int] = [6, 7], workcalendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[dict, dict, dict]:
    """
    Discovers a performance directly-follows graph from an event log

    Parameters
    ---------------
    log
        Event log
    business_hours
        Enables/disables the computation based on the business hours (default: False)
    worktiming
        (If the business hours are enabled) The hour range in which the resources of the log are working (default: 7 to 17)
    weekends
        (If the business hours are enabled) The weekends days (default: Saturday (6), Sunday (7))
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    performance_dfg
        Performance DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.util import constants

        from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_dfg_graph
        activity_key = properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in properties else xes_constants.DEFAULT_NAME_KEY
        timestamp_key = properties[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in properties else xes_constants.DEFAULT_TIMESTAMP_KEY
        case_id_key = properties[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in properties else constants.CASE_CONCEPT_NAME
        dfg = get_dfg_graph(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_glue=case_id_key, measure="performance", perf_aggregation_key="all",
                            business_hours=business_hours, worktiming=worktiming, weekends=weekends, workcalendar=workcalendar)
        from pm4py.statistics.start_activities.pandas import get as start_activities_module
        from pm4py.statistics.end_activities.pandas import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    else:
        from pm4py.algo.discovery.dfg.variants import performance as dfg_discovery
        properties[dfg_discovery.Parameters.AGGREGATION_MEASURE] = "all"
        properties[dfg_discovery.Parameters.BUSINESS_HOURS] = business_hours
        properties[dfg_discovery.Parameters.WORKTIMING] = worktiming
        properties[dfg_discovery.Parameters.WEEKENDS] = weekends
        dfg = dfg_discovery.apply(log, parameters=properties)
        from pm4py.statistics.start_activities.log import get as start_activities_module
        from pm4py.statistics.end_activities.log import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    return dfg, start_activities, end_activities


def discover_petri_net_alpha(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Alpha Miner

    Parameters
    --------------
    log
        Event log
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key))


def discover_petri_net_alpha_plus(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Alpha+ algorithm

    Parameters
    --------------
    log
        Event log
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key))


def discover_petri_net_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[
    PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the IMDFc algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    pt = discover_process_tree_inductive(log, noise_threshold, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    from pm4py.convert import convert_to_petri_net
    return convert_to_petri_net(pt)


def discover_petri_net_heuristics(log: Union[EventLog, pd.DataFrame], dependency_threshold: float = 0.5,
                                  and_threshold: float = 0.65,
                                  loop_two_threshold: float = 0.5, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discover a Petri net using the Heuristics Miner

    Parameters
    ---------------
    log
        Event log
    dependency_threshold
        Dependency threshold (default: 0.5)
    and_threshold
        AND threshold (default: 0.65)
    loop_two_threshold
        Loop two threshold (default: 0.5)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    heu_parameters = heuristics_miner.Variants.CLASSIC.value.Parameters
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters[heu_parameters.DEPENDENCY_THRESH] = dependency_threshold
    parameters[heu_parameters.AND_MEASURE_THRESH] = and_threshold
    parameters[heu_parameters.LOOP_LENGTH_TWO_THRESH] = loop_two_threshold

    return heuristics_miner.apply(log, variant=heuristics_miner.Variants.CLASSIC, parameters=parameters)


def discover_process_tree_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> ProcessTree:
    """
    Discovers a process tree using the IM algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    process_tree
        Process tree object
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters[inductive_miner.Variants.IM_CLEAN.value.Parameters.NOISE_THRESHOLD] = noise_threshold
    return inductive_miner.apply_tree(log, variant=inductive_miner.Variants.IM_CLEAN, parameters=parameters)


def discover_heuristics_net(log: Union[EventLog, pd.DataFrame], dependency_threshold: float = 0.5,
                            and_threshold: float = 0.65,
                            loop_two_threshold: float = 0.5, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> HeuristicsNet:
    """
    Discovers an heuristics net

    Parameters
    ---------------
    log
        Event log
    dependency_threshold
        Dependency threshold (default: 0.5)
    and_threshold
        AND threshold (default: 0.65)
    loop_two_threshold
        Loop two threshold (default: 0.5)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    heu_net
        Heuristics net
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    heu_parameters = heuristics_miner.Variants.CLASSIC.value.Parameters
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters[heu_parameters.DEPENDENCY_THRESH] = dependency_threshold
    parameters[heu_parameters.AND_MEASURE_THRESH] = and_threshold
    parameters[heu_parameters.LOOP_LENGTH_TWO_THRESH] = loop_two_threshold
    return heuristics_miner.apply_heu(log, variant=heuristics_miner.Variants.CLASSIC, parameters=parameters)


def derive_minimum_self_distance(log: Union[DataFrame, EventLog, EventStream], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Dict[str, int]:
    '''
        This algorithm computes the minimum self-distance for each activity observed in an event log.
        The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
        The activity key 'concept:name' is used.


        Parameters
        ----------
        log
            event log (either pandas.DataFrame, EventLog or EventStream)
        activity_key
            attribute to be used for the activity
        timestamp_key
            attribute to be used for the timestamp
        case_id_key
            attribute to be used as case identifier

        Returns
        -------
            dict mapping an activity to its self-distance, if it exists, otherwise it is not part of the dict.
        '''
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd
    return msd.apply(log, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key))


def discover_footprints(*args: Union[EventLog, Tuple[PetriNet, Marking, Marking], ProcessTree]) -> Union[
    List[Dict[str, Any]], Dict[str, Any]]:
    """
    Discovers the footprints out of the provided event log / pocess model

    Parameters
    --------------
    args
        Event log / process model
    """
    from pm4py.algo.discovery.footprints import algorithm as fp_discovery
    return fp_discovery.apply(*args)


def discover_eventually_follows_graph(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> Dict[Tuple[str, str], int]:
    """
    Gets the eventually follows graph from a log object

    Parameters
    ---------------
    log
        Log object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    eventually_follows_graph
        Dictionary of tuples of activities that eventually follows each other; along with the number of occurrences
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.eventually_follows.pandas import get
        return get.apply(log, parameters=properties)
    else:
        from pm4py.statistics.eventually_follows.log import get
        return get.apply(log, parameters=properties)


def discover_bpmn_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> BPMN:
    """
        Discovers a BPMN using the Inductive Miner algorithm

        Parameters
        --------------
        log
            Event log
        noise_threshold
            Noise threshold (default: 0.0)
        activity_key
            attribute to be used for the activity
        timestamp_key
            attribute to be used for the timestamp
        case_id_key
            attribute to be used as case identifier

        Returns
        --------------
        bpmn_diagram
            BPMN diagram
        """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    pt = discover_process_tree_inductive(log, noise_threshold, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    from pm4py.convert import convert_to_bpmn
    return convert_to_bpmn(pt)


def discover_ocdfg(ocel: OCEL, business_hours=False, worktiming=[7, 17], weekends=[6, 7]) -> Dict[str, Any]:
    """
    Discovers an OC-DFG from an object-centric event log.

    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.


    Parameters
    ----------------
    ocel
        Object-centric event log
    business_hours
        Boolean value that enables the usage of the business hours
    worktiming
        (if business hours are in use) work timing during the day (default: [7, 17])
    weekends
        (if business hours are in use) weekends (default: [6, 7])

    Returns
    ---------------
    ocdfg
        Object-centric directly-follows graph
    """
    parameters = {}
    parameters["business_hours"] = business_hours
    parameters["worktiming"] = worktiming
    parameters["weekends"] = weekends
    from pm4py.algo.discovery.ocel.ocdfg import algorithm as ocdfg_discovery
    return ocdfg_discovery.apply(ocel, parameters=parameters)


def discover_oc_petri_net(ocel: OCEL) -> Dict[str, Any]:
    """
    Discovers an object-centric Petri net from the provided object-centric event log.

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    -----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    ocpn
        Object-centric Petri net
    """
    from pm4py.algo.discovery.ocel.ocpn import algorithm as ocpn_discovery
    return ocpn_discovery.apply(ocel)
