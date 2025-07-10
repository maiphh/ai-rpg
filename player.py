class Player:
    def __init__(self, name= "player"):
        self.name = name

        self.inventory = []

        self.hp = 100
        self.max_hp = 100
        self.atk = 10
        self.df = 10
        self.level = 1
 
    
    def take_damage(self, damage):
        print(f"{self.name} takes {damage} damage!")
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return self.hp

    def heal(self, amount):
        print(f"{self.name} heals for {amount} HP!")
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return self.hp
    
    def adjust_atk(self, amount):
        print(f"{self.name}'s attack adjusted by {amount}!")
        self.atk += amount
        return self.atk

    def adjust_df(self, amount):
        print(f"{self.name}'s defense adjusted by {amount}!")
        self.df += amount
        return self.df
    
    def add_item(self, item_name, item_description, is_consumable=False):
        item = {
            "name": item_name,
            "description": item_description,
            "is_consumable": is_consumable
        }
        self.inventory.append(item)
        print(f"{self.name} added {item_name} to inventory.")
        return self.inventory
    
    def use_item(self, item_name):
        for item in self.inventory:
            if item["name"] == item_name:
                if item["is_consumable"]:
                    print(f"{self.name} uses {item_name}.")
                    self.inventory.remove(item)
                    return f"Used {item_name}."
                
        return f"{item_name} not found in inventory."

    def get_info(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "atk": self.atk,
            "df": self.df,
            "level": self.level,
            "inventory": self.inventory
        }

    def to_string(self):
        return (
            f"🧑 Player {self.name}: "
            f"❤️ HP={self.hp}/{self.max_hp}, "
            f"⚔️ ATK={self.atk}, "
            f"🛡️ DF={self.df}, "
            f"⭐ Level={self.level}, "
            f"🎒 Inventory={self.inventory}"
        )
        
        