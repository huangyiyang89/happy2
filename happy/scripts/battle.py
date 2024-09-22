
from happy.interface import Script

class AutoBattle(Script):

    def _on_init(self):
        self.name = "自动战斗"
        self.enable = True

    def _on_battle(self):
        
        if self.cg.battle.is_player_second_turn:
            self.cg.battle.player.attack()
            return

        if self.cg.battle.is_player_turn:
            if self.cg.battle.is_waiting_anime:
                return
            pet = self.cg.battle.pet
            drug = self.cg.items.first_drug

            if drug:
                recovery = drug.drug_restore * self.cg.player.value_recovery / 100
                if (
                    self.cg.battle.player.hp_lost >= recovery
                    or self.cg.battle.player.hp_per <= 30
                ):
                    self.cg.battle.player.use_item(drug)
                    return
                if pet and pet.hp_per < 30 and pet.hp > 0:
                    self.cg.battle.player.use_item(drug, pet)
                    return

            self.cg.battle.player.cast_default(self.cg.battle.units)
            return

        if self.cg.battle.is_pet_turn:
            self.cg.battle.pet.cast_default(self.cg.battle.units)
    



class EncounterScript(Script):

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "自动遇敌"
        self.range = 1
        self.start_x = 0
        self.start_y = 0
        self.injury_flag = False
    
    def _on_not_battle(self):
        return super()._on_not_battle()