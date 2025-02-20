from happy.interface import Script

class AutoBattle(Script):

    def _on_init(self):
        self.name = "自动战斗"
        self.enable = True

    def _on_battle(self):
        if (
            self.cg.player.job_name == "遊民"
            and self.cg.items.right_hand
            and self.cg.items.right_hand.name == "平民小刀"
            and self.cg.battle.is_player_turn
        ):
            if self.cg.battle.is_waiting_anime:
                return
            unit = self.cg.battle.units.get(10)
            if unit:
                self.cg.battle.player.attack(unit)
                return

        if self.cg.battle.is_player_second_turn:
            self.cg.battle.player.attack(self.cg.battle.units.random_choice_enemy)
            
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

            if len(self.cg.battle.units.enemies) == 1:
                self.cg.battle.player.attack(self.cg.battle.units.random_choice_enemy)
                return

            self.cg.battle.player.cast_default(self.cg.battle.units)
            return

        if self.cg.battle.is_pet_turn:
            self.cg.battle.pet.cast_default(self.cg.battle.units)
