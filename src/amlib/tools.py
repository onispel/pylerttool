"""Funtions for accessing alertmanager objects from model"""

import datetime
import re
from typing import Iterable
from functools import cache

import requests

from . import BASE_SILENCE_URL, BASE_API_URL, HEADERS, STD_TIMEOUT, Paths, model


def get_local_tzinfo() -> datetime.tzinfo|None:
    """Access local timezone."""
    return datetime.datetime.now().astimezone().tzinfo

def datetime_from_iso(dts: str, localtime: bool = True) -> datetime.datetime:
    """Convert ISO-datestring to datetime"""
    TZ = datetime.timezone.utc if not localtime else get_local_tzinfo()
    return datetime.datetime.fromisoformat(dts).replace(tzinfo=TZ)

def match(key: str, val: str, regex: bool = False, equal: bool = True) -> model.Matcher:
    """Helper function: Returns a Matcher-object for use in silences"""
    return model.Matcher(name=key, value=val, isRegex=regex, isEqual=equal)

def parse_matcher(expr: str) -> model.Matcher | None:
    """translates matcher-string into matcher-object"""
    matcher = None
    regex = r"(?P<key>\w+)(?P<op>!?=~?)(?P<val>.*)"
    matching = re.match(regex, expr)
    if matching:
        key, oper, val = matching.groups()
        is_eq = False if oper[0] == "!" else True
        is_re = True if oper[-1] == "~" else False
        matcher = match(key, val, is_re, is_eq)
    return matcher


def matcher_op_to_str(matcher: model.Matcher) -> str:
    """Helper function for creating Matcher objects from strings."""
    moper = ""
    if matcher.isEqual:
        moper = "="
    else:
        moper = "!="
    if matcher.isRegex:
        moper = moper[0] + "~"
    return moper


def silence_url(silence:model.GettableSilence) -> str:
    """Returns HTML-Url for Silence."""
    return F"{BASE_SILENCE_URL}{silence.id}"

def get_status() -> model.AlertmanagerStatus:
    """Returns status of Alertmanager"""
    resp = requests.get(BASE_API_URL + Paths.STATUS.value ,headers=HEADERS,timeout=STD_TIMEOUT)
    am_status = model.AlertmanagerStatus(**resp.json())
    return am_status

@cache
def get_silences(statelist: Iterable[model.State]|None = None,sfilter:Iterable[str]|None = None) -> list[model.GettableSilence]:
    """Returns a list of silences. Filtering can be done by a given state"""
    if not sfilter:
        sfilter = []
    resp = requests.get(BASE_API_URL + Paths.SILENCES.value ,params={'filter':sfilter},headers=HEADERS,timeout=STD_TIMEOUT)
    slist = model.GettableSilences.parse_obj(resp.json()).__root__
    if statelist:
        slist = [s for s in slist if s.status.state in statelist]
    return slist

def get_silence(silence_id: str) -> model.GettableSilence|None:
    """Returns a silence by its id."""
    resp = requests.get(f'{BASE_API_URL}{Paths.SILENCE.value}/{silence_id}',headers=HEADERS,timeout=STD_TIMEOUT)
    if resp.ok:
        silence = model.GettableSilence(**resp.json())
    else:
        silence = None
    return silence

def set_silence(silence: model.Silence) -> tuple[bool, str|dict[str, str]]:
    """Set or modify silence. Returns if request was successful and description ( True and silenceID if successful )"""
    resp = requests.post(f'{BASE_API_URL}{Paths.SILENCES.value}',data=silence.json(),headers=HEADERS,timeout=STD_TIMEOUT)
    retval = None
    if resp.ok:
        retval = resp.json()['silenceID']
    else:
        retval = resp.json()
    return (resp.ok, retval)

def expire_silence(silence_id: str) -> bool:
    """Expire a silence by its id."""
    resp = requests.delete(f'{BASE_API_URL}{Paths.SILENCE.value}/{silence_id}',headers=HEADERS,timeout=STD_TIMEOUT)
    return resp.ok

@cache
def get_alerts(active: bool = True, silenced: bool = True, inhibited: bool = True, unprocessed: bool = True, afilter: Iterable[str]|None =None, receiver: str|None =None ) -> list[model.GettableAlert]:
    """Returns a list of matching alerts."""
    params = {
        'active': active,
        'silenced': silenced,
        'inhibited': inhibited,
        'unprocessed': unprocessed,
        'filter': afilter,
        'receiver': receiver
    }
    params = { k: v for (k,v) in params.items() if v != None}
    resp = requests.get(BASE_API_URL + Paths.ALERTS.value, headers=HEADERS, params=params,timeout=STD_TIMEOUT)
    alert_list = model.GettableAlerts.parse_obj(resp.json()).__root__
    return alert_list

def get_alert_by_fingerprint(fingerprint: str, alert_list: list[model.GettableAlert]|None) -> model.GettableAlert|None:
    """Returns an alert according to its (hopefully unique) fingerprint."""
    alist = alert_list
    if not alist:
        alist = get_alerts()
    for alert in alist:
        if alert.fingerprint == fingerprint:
            return alert
    return None

def is_matching(value:str, matcher:model.Matcher) -> bool:
    """Helper to evaluate if a matcher suits a given value."""
    match (matcher.isEqual, matcher.isRegex):
        case (True, False):
            return value == matcher.value
        case (False, False):
            return value != matcher.value
        case (True, True):
            op_match = re.search(matcher.value,value)
            if op_match:
                return True
            else:
                return False
        case (False, True):
            op_match = re.search(matcher.value,value)
            if op_match:
                return False
            else:
                return True
        case _:
            return False

def is_matching_all(labels:model.LabelSet, matchers:model.Matchers) -> bool:
    """Returns True if all Matchers match the given LabelSet."""
    label_dict = {label[0]: label[1] for label in labels}
    for matcher in matchers.__root__:
        if matcher.name not in label_dict.keys():
            return False
        if not is_matching(label_dict[matcher.name],matcher):
            return False
    return True

def find_silences(alert: model.Alert) -> list[model.GettableSilence|None]:
    """Finds and returns silences for a given alert, 
    according to the labels of the alert and the matchers of the silence."""
    result_list: list[model.GettableSilence|None] = []
    silences = get_silences()
    for silence in silences:
        labels = dict(alert.labels)
        labels_keys = labels.keys()
        matching = True
        for matcher in silence.matchers.__root__:
            if matcher.name in labels_keys:
                if not is_matching(labels[matcher.name], matcher):
                    matching = False
                    break
            else:
                matching = False
                break
        if matching:
            result_list.append(silence)
    return result_list

def find_alerts(silence: model.Silence) -> list[model.GettableAlert]:
    """Finds and returns alerts for a given silence, 
    according to the labels of the alert and the matchers of the silence."""
    result_list: list[model.GettableAlert] = []
    alerts = get_alerts(active=True, silenced=True, inhibited=False, unprocessed=False)
    for alert in alerts:
        if is_matching_all(alert.labels, silence.matchers):
            result_list.append(alert)
    return result_list