import logging
from happy.interface import Cg
from happy.interface.mem import CgMem, find_all_cg_process_id
from happy.util.pywinhandle import close_handles, find_handles

_crossgates: list[Cg] = []


def open_all():
    for process_id in find_all_cg_process_id():
        cg = _open_cg(process_id)
        cg.start_scripts_thread()
    _crossgates.sort(key=lambda cg: cg.account)
    return _crossgates


def open(account: str = "", player_name: str = "") -> Cg | None:
    for process_id in find_all_cg_process_id():
        new_cg = _open_cg(process_id)
        if new_cg and account in new_cg.account and player_name in new_cg.player.name:
            new_cg.start_scripts_thread()
            return new_cg
    return None


def _open_cg(process_id):
    for cg in _crossgates:
        if cg.mem.process_id == process_id:
            return cg
    try:
        mem = CgMem(process_id)
        cg = Cg(mem)
        _crossgates.append(cg)
        cg.stopped_callback = lambda cg: _crossgates.remove(cg)
        logging.debug(f"new cg instantce created, account: {cg.account} player name: {cg.player.name}")
        return cg
    except Exception("open process failed"):
        return None


def remove_open_limit():
    process_ids = list(find_all_cg_process_id())
    handles = find_handles(process_ids, ["汢敵"])
    close_handles(handles)
