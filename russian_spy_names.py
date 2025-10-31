"""Russian Spy Names Generator for Anonymous Mode"""

import random

# Top 100 Russian male names suitable for spy personas
RUSSIAN_SPY_NAMES = [
    "Aleksandr", "Alexei", "Andrei", "Anton", "Arkady",
    "Arseny", "Artem", "Boris", "Daniil", "Denis",
    "Dmitry", "Egor", "Fedor", "Gennady", "Georgy",
    "Gleb", "Grigory", "Igor", "Ilya", "Ivan",
    "Kirill", "Konstantin", "Lev", "Leonid", "Makar",
    "Maksim", "Mark", "Matvey", "Mikhail", "Nikita",
    "Nikolai", "Oleg", "Pavel", "Petr", "Roman",
    "Ruslan", "Semyon", "Sergei", "Stanislav", "Stepan",
    "Timofey", "Timur", "Vadim", "Valentin", "Valery",
    "Viktor", "Vitaly", "Vladislav", "Vladimir", "Vyacheslav",
    "Yaroslav", "Yevgeny", "Yuri", "Zakhar", "Anatoly",
    "Bogdan", "Demyan", "Efim", "Filipp", "Gavril",
    "Innokenty", "Iosif", "Kondrat", "Kuzma", "Larion",
    "Luka", "Matvei", "Miron", "Nazar", "Nestor",
    "Pankrat", "Platon", "Prokhor", "Rodion", "Savely",
    "Sevastyan", "Taras", "Tikhon", "Trofim", "Vasily",
    "Veniamin", "Yegor", "Yefim", "Zinovy", "Afanasy",
    "Averky", "Davyd", "Elisey", "Ermolai", "Fadey",
    "Gordey", "Ignat", "Kliment", "Lavr", "Markel",
    "Modest", "Nikifor", "Pakhom", "Potap", "Rostislav"
]


def get_random_spy_name() -> str:
    """Generate a random Russian spy name for anonymous users.

    Returns:
        A random name from the Russian spy names list
    """
    return random.choice(RUSSIAN_SPY_NAMES)


def generate_unique_spy_name(existing_names: set) -> str:
    """Generate a unique spy name not in the existing set.

    Args:
        existing_names: Set of already used names in current session

    Returns:
        A unique Russian spy name, or a numbered variant if all names taken
    """
    # Try to find an unused name from the base list
    available = [name for name in RUSSIAN_SPY_NAMES if name not in existing_names]

    if available:
        return random.choice(available)

    # If all 100 names are taken, start appending numbers
    base_name = random.choice(RUSSIAN_SPY_NAMES)
    counter = 1
    while f"{base_name}{counter}" in existing_names:
        counter += 1

    return f"{base_name}{counter}"
