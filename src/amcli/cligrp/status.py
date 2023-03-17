import click, tabulate
from datetime import timezone,tzinfo
from amlib import tools, model
from . import LOCAL_TZ

def echo_status(status: model.AlertmanagerStatus, tzi: tzinfo | None = timezone.utc) -> None:
    """ Print representation of status """
    stat_tbl = []
    cluster_info = [['Name', status.cluster.name]]
    cluster_info.append(['Status',status.cluster.status.value])
    if status.cluster.peers:
        cluster_peers = [[peer.address, peer.name] for peer in status.cluster.peers]
    cluster_info.append(['Peers', tabulate.tabulate(cluster_peers, tablefmt='plain')])
    stat_tbl.append(['Cluster', tabulate.tabulate(cluster_info, tablefmt='plain')])
    stat_tbl.append(['Uptime', str(status.uptime.astimezone(tzi))])
    version_info = [['Version', status.versionInfo.version]]
    version_info.append(['Revision', status.versionInfo.revision])
    version_info.append(['Branch', status.versionInfo.branch])
    version_info.append(['BuildUser', status.versionInfo.buildUser])
    version_info.append(['BuildDate', status.versionInfo.buildDate])
    version_info.append(['GoVersion', status.versionInfo.goVersion])
    stat_tbl.append(['VersionInfo', tabulate.tabulate(version_info, tablefmt='plain')])
    click.echo(tabulate.tabulate(stat_tbl))


@click.group(name="status")
def status_grp() -> None:
    """Cluster status commands"""
    pass

@click.command(name='show')
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
def status_show(localtime:bool) -> None:
    """ Show status of alertmanager """
    tz_info = LOCAL_TZ if localtime else timezone.utc
    status = tools.get_status()
    echo_status(status,tz_info)

@click.command(name='config')
def status_config() -> None:
    """ Show config of alertmanager """
    config = tools.get_status().config.original
    click.echo(config)

status_grp.add_command(status_show)
status_grp.add_command(status_config)