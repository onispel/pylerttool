from datetime import datetime,timezone,tzinfo
import click,tabulate
from urllib.parse import unquote
import amlib.model as model
from amlib.tools import matcher_op_to_str,silence_url

LOCAL_TZ = datetime.now().astimezone().tzinfo

DT_FORMATS = [
    '%Y-%m-%d',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%H:%M:%S',
    '%H:%M'
]

state_colors = {
    model.State.active: 'green',
    model.State.pending: 'yellow',
    model.State.expired: 'red'
}


def echo_silence(silence: model.Silence | model.GettableSilence, tzi: tzinfo | None = timezone.utc) -> None:
    """ Print representation of silence """
    silence_tbl: list[list[str]] = []
    #if hasattr(silence, 'id'): # only for gettable silences
    if type(silence) == model.GettableSilence:
        silence_tbl.append(['ID', click.style(silence.id, fg='yellow')])
    silence_tbl.append(['Starts at', str(silence.startsAt.astimezone(tzi))])
    silence_tbl.append(['Ends at', str(silence.endsAt.astimezone(tzi))])
    #if hasattr(silence, 'updatedAt'): # only for gettable silences
    if type(silence) == model.GettableSilence:
        silence_tbl.append(['Updated at', str(silence.updatedAt.astimezone(tzi))])
    silence_tbl.append(['Created by', str(silence.createdBy)])
    silence_tbl.append(['Comment', silence.comment])
    #if hasattr(silence, 'status'): # only for gettable silences
    if type(silence) == model.GettableSilence:
        silence_tbl.append(['State', click.style(silence.status.state.value,
               fg=state_colors[silence.status.state])])
    matchers = [(m.name, matcher_op_to_str(m), m.value)
                for m in silence.matchers.__root__]
    silence_tbl.append(['Matchers', tabulate.tabulate(matchers, tablefmt='plain')])
    #if hasattr(silence, 'id'): # only for gettable silences
    if type(silence) == model.GettableSilence:
        silence_tbl.append(['SilenceURL', silence_url(silence)])
    click.echo(tabulate.tabulate(silence_tbl))

    
def echo_alert(alert: model.GettableAlert, tzi: tzinfo | None = timezone.utc) -> None:
    """ Print representation of alert """
    alert_tbl = []
    alert_tbl.append(['fingerprint', click.style(alert.fingerprint, fg='yellow')])
    alert_tbl.append(['startsAt', str(alert.startsAt.astimezone(tzi))])
    alert_tbl.append(['endsAt', str(alert.endsAt.astimezone(tzi))])
    alert_tbl.append(['state', alert.status.state.value])
    # atb.append(['silencedBy',alert.status.state])
    receivers = [['', rec.name] for rec in alert.receivers]
    if len(receivers) > 0:
        receivers[0][0] = 'receivers'
        alert_tbl.extend(receivers)
    silencers = [['', sil] for sil in alert.status.silencedBy]
    if len(silencers) > 0:
        silencers[0][0] = "silencedBy"
        alert_tbl.extend(silencers)
    inhibitors = [['', inh] for inh in alert.status.inhibitedBy]
    if len(inhibitors) > 0:
        inhibitors[0][0] = "inhibitedBy"
        alert_tbl.extend(inhibitors)
    annotations = [[ann[0], '=', unquote(ann[1])] for ann in alert.annotations]
    if len(annotations) > 0:
        alert_tbl.append(['annotations', tabulate.tabulate(
            annotations, tablefmt='plain')])
    labels = [[label[0], '=', label[1]] for label in alert.labels]
    if len(labels) > 0:
        alert_tbl.append(['labels', tabulate.tabulate(labels, tablefmt='plain')])
    alert_tbl.append(['generatorURL', unquote(str(alert.generatorURL))])
    click.echo(tabulate.tabulate(alert_tbl))