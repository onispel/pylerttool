from email.policy import default
import click, getpass
from datetime import datetime,timezone,date,time,timedelta
from pytimeparse.timeparse import timeparse

from amlib import tools, model
from . import LOCAL_TZ, DT_FORMATS
from . import echo_silence, echo_alert



@click.group(name="silence")
def silence_grp() -> None:
    """Commands for handling silences"""

@click.command(name='filter')
@click.option('--active/--noactive', default=True, show_default='--active')
@click.option('--pending/--nopending', default=True, show_default='--pending')
@click.option('--expired/--noexpired', default=False, show_default='--noexpired')
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--has-alerts', 'has_alerts', is_flag=True, default=False, help='Show only silences with matching alerts')
@click.option('--show-alerts', 'show_alerts', is_flag=True, default=False, help='Show alerts that match the silence')
@click.argument('match_filter', nargs=-1)
def silence_filter(active: bool, pending: bool, expired: bool, localtime: bool, has_alerts:bool, show_alerts: bool, match_filter: list[str] | None = None) -> None:
    """ Filter silences by state or matchers """
    tz_info = LOCAL_TZ if localtime else timezone.utc
    statelist = []
    if active:
        statelist.append(model.State.active)
    if pending:
        statelist.append(model.State.pending)
    if expired:
        statelist.append(model.State.expired)
    silences = tools.get_silences(tuple(statelist), tuple(match_filter)) if match_filter else []
    silence_counter = 0
    for silence in silences:
        alerts = tools.find_alerts(silence)
        if has_alerts and not alerts:
            continue
        silence_counter += 1
        echo_silence(silence, tz_info)
        if show_alerts:
            for alert in alerts:
                echo_alert(alert, tz_info)
        if alerts:
            click.echo(f"Found {len(alerts)} alerts matching this silence")
        else:
            click.echo("No alerts match this silence")
    if silence_counter == 0:
        click.echo("No silences found")
    else:
        click.echo(f"Found {silence_counter} silences")


@click.command(name='delete')
@click.argument('silence_id', nargs=-1)
def silence_delete(silence_id: str) -> None:
    """delete silences by id"""
    for sid in silence_id:
        okay = tools.expire_silence(sid)
        if okay:
            click.echo(f'SilenceID: {sid} ' +
                       click.style('*DELETED*', fg='green'))
        else:
            click.echo(f'SilenceID: {sid} ' + click.style('*ERROR*', fg='red'))


@click.command(name="expires")
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--before', '-b', type=click.DateTime(formats=DT_FORMATS), default=None, help='silence expires before given date/time (overrides "--within")')
@click.option('--within', '-w', type=str, default=None, help='silence expires within given timerange (i.e.: "2h30m")')
@click.option('--after', '-a', type=click.DateTime(formats=DT_FORMATS), default=None, help='silence expires after given date/time (overrides "--within")')
@click.option('--notwithin', '-n', type=str, default=None, help='silence expires AFTER given timerange (i.e.: "2h30m")')
@click.option('--pending/--nopending', 'pending', default=True, show_default='--pending', help='include or exclude pending silences')
@click.option('--has-alerts', 'has_alerts', is_flag=True, default=False, help='Show only silences with matching alerts')
@click.option('--show-alerts', 'show_alerts', is_flag=True, default=False, help='Show alerts that match the silence')
def silence_expires(localtime: bool, before: datetime | None, after: datetime | None, within: str | None, notwithin: str | None, pending: bool, has_alerts: bool, show_alerts: bool) -> None:
    """Search for silences that will expire"""
    tz_info = LOCAL_TZ if localtime else timezone.utc

    if len([opt for opt in (before, after, within, notwithin) if opt is not None]) != 1:
        raise click.UsageError(
            "Exactly ONE option of --before, --after, --within, --notwithin has to be used.")
    stats = [model.State.active]
    if pending:
        stats.append(model.State.pending)
    silence_list = tools.get_silences(tuple(stats))

    expiry_date = None
    if within:
        within_secs = timeparse(within)
        if not within_secs:
            raise click.BadOptionUsage('--within','invalid time range format')
        expiry_date = datetime.now().astimezone(tz_info) + timedelta(seconds=within_secs)
    if before:
        if before.date() == date(1900, 1, 1):
            before = datetime.combine(datetime.now(tz_info).date(), time(
                before.hour, before.minute, before.second))
        expiry_date = before.astimezone(tz_info)
    if expiry_date:
        silence_list = [silence for silence in silence_list if silence.endsAt < expiry_date]

    if notwithin:
        notwithin_secs = timeparse(notwithin)
        if not notwithin_secs:
            raise click.BadOptionUsage('--notwithin','invalid time range format')
        expiry_date = datetime.now().astimezone(tz_info) + timedelta(seconds=notwithin_secs)
    if after:
        if after.date() == date(1900, 1, 1):
            after = datetime.combine(datetime.now(tz_info).date(), time(
                after.hour, after.minute, after.second))
        expiry_date = after.astimezone(tz_info)
    if any((notwithin,after)) and expiry_date:
        silence_list = [silence for silence in silence_list if silence.endsAt > expiry_date]

    if silence_list:
        silence_counter = 0
        for silence in silence_list:
            alerts = tools.find_alerts(silence)
            if has_alerts and not alerts:
                continue
            silence_counter += 1
            echo_silence(silence, tz_info)
            if show_alerts:
                for alert in alerts:
                    echo_alert(alert, tz_info)
            if alerts:
                click.echo(f"Found {len(alerts)} alerts matching this silence")
            else:
                click.echo("No alerts match this silence")
        if silence_counter == 0:
            click.echo("No silences found")
        else:
            click.echo(f"Found {silence_counter} silences")
    else:
        click.echo('No expiring silences found')
        exit(1)


@click.command(name="expired")
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--after', '-a', type=click.DateTime(formats=DT_FORMATS), default=None, help='silence expired after given date/time (overrides "--within")')
@click.option('--within', '-w', type=str, default=None, help='silence expires within given timerange (i.e.: "2h30m")')
def silence_expired(localtime: bool, after: datetime | None, within: str | None) -> None:
    """Search for expired silences"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    # expiry_date = None
    if after is None and within is None:
        raise click.UsageError('"--after or --within as to be specified')
    if within:
        within_secs = timeparse(within)
        expiry_date = datetime.now().astimezone(
            tz_info) - timedelta(seconds=within_secs)
    if after:
        if after.date() == date(1900, 1, 1):
            after = datetime.combine(datetime.now(tz_info).date(), time(
                after.hour, after.minute, after.second))
        expiry_date = after.astimezone(tz_info)
    silence_list = tools.get_silences(tuple([model.State.expired]))
    if silence_list:
        silence_list = [
            silence for silence in silence_list if silence.endsAt > expiry_date]
        for silence in silence_list:
            echo_silence(silence, tz_info)
        if silence_list:
            click.echo(f"Found {len(silence_list)} expired silences")
        else:
            click.echo("No expired silences found")
    else:
        click.echo("No expired silences found")


@click.command(name='modify')
@click.option('--sid', type=str, required=True, help='Silence ID')
@click.option('--start', '-s', type=click.DateTime(formats=DT_FORMATS), default=None, help="startsAt")
@click.option('--duration', '-d', type=str, default=None, help='Duration -> endsAt (overrides --end)')
@click.option('--end', '-e', type=click.DateTime(formats=DT_FORMATS), default=None, help="endsAt")
@click.option('--creator', '-u', type=str, default=None, show_default='(current user)', help='Creator of silence')
@click.option('--comment', '-t', type=str, default=None, help='Comment on silence')
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--noop', is_flag=True, help="Do nothing - testing only.")
@click.option('--show-alerts', 'show_alerts', is_flag=True, default=False, help='Find alerts that match the silence')
@click.argument('matcher', nargs=-1)
def silence_modify(sid: str, start: datetime, duration: str, end: datetime, creator: str, comment: str, matcher: list[str], noop: bool, show_alerts:bool, localtime: bool) -> None:
    """modify existing silence"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    silence = tools.get_silence(sid)
    if silence:
        if start:
            if start.date() == date(1900, 1, 1):
                start = datetime.combine(datetime.now(tz_info).date(), time(
                    start.hour, start.minute, start.second))
            start = start.astimezone(tz_info)
            silence.startsAt = start
        if duration:
            duration_secs = timeparse(duration)
            end = silence.startsAt + timedelta(seconds=duration_secs)
        if end:
            if end.date() == date(1900, 1, 1):
                end = datetime.combine(start.date(), time(
                    end.hour, end.minute, end.second))
                if end <= start:
                    end = end + timedelta(days=1)
            end = end.astimezone(tz_info)
            silence.endsAt = end
        if creator:
            silence.createdBy = creator
        if comment:
            silence.comment = comment
        if matcher:
            matchers = []
            for single_match in matcher:
                matcher_obj = tools.parse_matcher(single_match)
                if matcher_obj:
                    matchers.append(matcher_obj)
            silence.matchers = model.Matchers.parse_obj(matchers)
        if noop:
            echo_silence(silence)
            alerts = tools.get_alerts(silence)
            if show_alerts:
                for alert in alerts:
                    echo_alert(alert)
            if alerts:
                click.echo(f'Found {len(alerts)} matching alerts')
            else:
                click.echo('No matching alerts found')

        else:
            okay, res = tools.set_silence(silence)
            if okay:
                click.echo(f'Silence created: {res}')
            else:
                raise click.UsageError(str(res))
    else:
        click.echo('Silence not found', err=True)


@click.command(name='create')
@click.option('--start', '-s', type=click.DateTime(formats=DT_FORMATS), default=datetime.now(), help="startsAt")
@click.option('--duration', '-d', type=str, default=None, help='Duration -> endsAt (overrides --end)')
@click.option('--end', '-e', type=click.DateTime(formats=DT_FORMATS), default=None, help="endsAt")
@click.option('--creator', '-u', type=str, default=getpass.getuser(), show_default='(current user)', help='Creator of silence')
@click.option('--comment', '-t', type=str, required=True, help='Comment on silence')
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--noop', is_flag=True, help="Do nothing - just test.")
@click.option('--show-alerts', 'show_alerts', is_flag=True, default=False, help='Find alerts that match the silence')
@click.argument('matcher', nargs=-1)
def silence_create(start: datetime, duration: str | None, end: datetime, creator: str, comment: str, matcher: list[str], noop: bool, show_alerts: bool,  localtime: bool) -> None:
    """create a new silence"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    if start.date() == date(1900, 1, 1):  # no date is set (just time)
        start = datetime.combine(date.today(), time(
            start.hour, start.minute, start.second))
    start = start.astimezone(tz_info)
    if duration is None and end is None:
        raise click.UsageError("Either --duration or --end ist required.")
    if duration is not None:
        duration_secs = timeparse(duration)
        end = start + timedelta(seconds=duration_secs)
    else:
        if end.date() == date(1900, 1, 1):  # no date is set (just time)
            end = datetime.combine(start.date(), time(
                end.hour, end.minute, end.second))
            end = end.astimezone(tz_info)
            if end <= start:
                end = end + timedelta(days=1)
    end = end.astimezone(tz_info)
    matchers = []
    for single_match in matcher:
        matcher_obj = tools.parse_matcher(single_match)
        if matcher_obj:
            matchers.append(matcher_obj)
    silence = model.Silence(
        matchers=model.Matchers.parse_obj(matchers),
        startsAt=start, endsAt=end, createdBy=creator, comment=comment
    )
    if noop:
        echo_silence(silence, tz_info)
        alerts = tools.find_alerts(silence)
        if show_alerts:
            for alert in alerts:
                echo_alert(alert, tz_info)
        if alerts:
            click.echo(f'Found {len(alerts)} alerts')
        else:
            click.echo('No alerts found')
    else:
        okay, res = tools.set_silence(silence)
        print(res)
        if okay:
            click.echo(f'Silence ID:  {res}')
            click.echo(f'Silence URL: {tools.silence_url(tools.get_silence(str(res)))}') #type: ignore
        else:
            raise click.UsageError(str(res))


@click.command(name="show")
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--show-alerts', 'show_alerts', is_flag=True, default=False)
@click.argument('silence_id', type=str, nargs=-1)
def silence_show(localtime: bool, silence_id: str, show_alerts: bool) -> None:
    """show all information of a given silence id"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    for s_id in silence_id:
        silence = tools.get_silence(s_id)
        if silence:
            echo_silence(silence, tz_info)
            alerts = tools.find_alerts(silence)
            if show_alerts:
                for alert in alerts:
                    echo_alert(alert, tz_info)
            if alerts:
                click.echo(f'Found {len(alerts)} alerts')
            else:
                click.echo('No alerts found.')

silence_grp.add_command(silence_filter)
silence_grp.add_command(silence_show)
silence_grp.add_command(silence_create)
silence_grp.add_command(silence_modify)
silence_grp.add_command(silence_delete)
silence_grp.add_command(silence_expires)
silence_grp.add_command(silence_expired)