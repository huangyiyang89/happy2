import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from happy.interface import Cg


class Script:

    def __init__(self, cg: "Cg") -> None:
        self.name = "Unnamed script"
        self.cg = cg
        self.enable = False
        self._start_has_run = False
        self._stop_has_run = False
        self._last_time = time.time()
        self._on_init()

    def time_is_up(self,second:float=1.0):
        if time.time() - self._last_time > second:
            self._last_time = time.time()
            return True
        return False

    def update(self):
        
        if not self.enable:
            if not self._stop_has_run:
                self._on_stop()
                self._stop_has_run = True
                self._start_has_run = False
            return

        if not self._start_has_run:
            self._on_start()
            self._start_has_run = True
            self._stop_has_run = False

        
        self._on_update()

        if self.cg.state == 9 and self.cg.state2 == 3:
            self._on_not_battle()
            if self.cg.dialog.is_open:
                self._on_dialog()
            if self.cg.is_moving:
                self._on_moving()
            else:
                self._on_not_moving()

        if self.cg.battle.is_battling:
            self._on_battle()

            
    def _on_init(self):
        pass

    def _on_update(self):
        pass

    def _on_start(self):
        pass

    def _on_stop(self):
        pass

    def _on_battle(self):
        pass

    def _on_not_battle(self):
        pass

    def _on_moving(self):
        pass

    def _on_not_moving(self):
        pass

    def _on_dialog(self):
        pass


class ScriptManager:

    def __init__(self, cg: "Cg") -> None:
        self.cg = cg
        self._scripts = []

    def add(self, script: Script):
        self._scripts.append(script)

    def update(self):
        for script in self._scripts:
            script.update()
    
    def remove(self, script: Script):
        self._scripts.remove(script)

    def clear(self):
        self._scripts.clear()

    def __iter__(self):
        return iter(self._scripts)
    
    def __len__(self):
        return len(self._scripts)
    
    def __getitem__(self, index):
        return self._scripts[index]
    
    def __delitem__(self, index):
        del self._scripts[index]

    def __contains__(self, script: Script):
        return script in self._scripts
    
    def __reversed__(self):
        return reversed(self._scripts)
    
    def __repr__(self):
        return f"ScriptManager(scripts={self._scripts})"
    
    def __str__(self):
        return f"ScriptManager(scripts={self._scripts})"
    

